#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# NorNet System Setup Commons
# Copyright (C) 2014-2017 by Thomas Dreibholz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact: dreibh@simula.no

import re
import os

from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

# NorNet
from NorNetTools         import *
from NorNetConfiguration import *
from NorNetAPI           import *
from NorNetProviderSetup import *
from NorNetNodeSetup     import *


# ###### Write Automatic Configuration Information ##########################
def writeAutoConfigInformation(outputFile, comment='#'):
   outputFile.write(comment + ' ################ AUTOMATICALLY-GENERATED FILE! ################\n')
   outputFile.write(comment + ' #### Changes will be overwritten by NorNet config scripts! ####\n')
   outputFile.write(comment + ' ################ AUTOMATICALLY-GENERATED FILE! ################\n\n')


# ###### Write hostname file ################################################
def writeHostname(outputName, hostName, domainName):
   outputFile = codecs.open(outputName, 'w', 'utf-8')
   outputFile.write(hostName + '.' + domainName + '\n')
   outputFile.close()


# ###### Write hosts file ###################################################
def writeHosts(outputName, hostName, domainName):
   outputFile = codecs.open(outputName, 'w', 'utf-8')
   outputFile.write('127.0.0.1\tlocalhost\n')
   outputFile.write('127.0.1.1\t' + hostName + '.' + domainName + ' ' + hostName + '\n\n')
   outputFile.write('# The following lines are desirable for IPv6 capable hosts\n')
   outputFile.write('::1\tip6-localhost ip6-loopback\n')
   outputFile.write('fe00::0\tip6-localnet\n')
   outputFile.write('ff00::0\tip6-mcastprefix\n')
   outputFile.write('ff02::1\tip6-allnodes\n')
   outputFile.write('ff02::2\tip6-allrouters\n')
   outputFile.close()


# ###### Write sysctl.conf file #############################################
def writeSysctlConfiguration(outputName, interfaceName):
   interfaceTag = interfaceName.replace(".", "/")
   outputFile = codecs.open(outputName, 'w', 'utf-8')
   writeAutoConfigInformation(outputFile)

   outputFile.write('# Disable IPv6 auto-config on NorNet interface:\n')
   outputFile.write('net.ipv6.conf.' + interfaceTag + '.use_tempaddr=0\n')
   outputFile.write('net.ipv6.conf.' + interfaceTag + '.autoconf=0\n')
   outputFile.write('net.ipv6.conf.' + interfaceTag + '.accept_ra=0\n')

   outputFile.write('\n# Disable redirects:\n')
   outputFile.write('net.ipv4.conf.all.accept_redirects=0\n')
   outputFile.write('net.ipv4.conf.all.secure_redirects=0\n')
   outputFile.write('net.ipv6.conf.all.accept_redirects=0\n')

   outputFile.write('\n# Enable TCP ECN:\n')
   outputFile.write('net.ipv4.tcp_ecn=1\n')

   outputFile.write('\n# Prevent blocking in case of kernel issues:\n')
   # Reboot in case of kernel panic after 10s.
   # "INFO: task <name> blocked for more than 120 seconds." causes kernel panic.
   outputFile.write('kernel.panic=10\n')
   outputFile.write('kernel.hung_task_panic=1\n')

   outputFile.write('\n# Reduce blocking problems:\n')
   # References:
   # - https://www.blackmoreops.com/2014/09/22/linux-kernel-panic-issue-fix-hung_task_timeout_secs-blocked-120-seconds-problem/
   # - http://blog.ronnyegner-consulting.de/2011/10/13/info-task-blocked-for-more-than-120-seconds/comment-page-1/
   outputFile.write('vm.dirty_background_ratio=5\n')   # Default: 10
   outputFile.write('vm.dirty_ratio=10\n')             # Default: 20

   outputFile.close()


# ###### Write proxy configuration file #####################################
def writeProxyConfiguration(suffix, siteDomain, variant, controlBoxMode):
   proxyName = 'proxy.' + siteDomain
   for shell in [ 'sh', 'csh' ]:
      proxyConf = codecs.open('proxy.' + shell + suffix, 'w', 'utf-8')
      if controlBoxMode == False:
         if shell == 'sh':
            proxyConf.write('export http_proxy="http://' + proxyName  + ':3128/"\n')
            proxyConf.write('export ftp_proxy="http://'  + proxyName  + ':3128/"\n')
            proxyConf.write('export no_proxy="' + siteDomain + '"\n')
         elif shell == 'csh':
            proxyConf.write('setenv http_proxy "http://' + proxyName  + ':3128/"\n')
            proxyConf.write('setenv ftp_proxy "http://'  + proxyName  + ':3128/"\n')
            proxyConf.write('setenv no_proxy "' + siteDomain + '"\n')
      proxyConf.close()

   if variant == 'Debian':
      proxyConf = codecs.open('apt-proxy' + suffix, 'w', 'utf-8')
      if controlBoxMode == False:
         proxyConf.write('Acquire::http::Proxy "http://' + proxyName + ':3128/";\n')
         proxyConf.write('Acquire::ftp::Proxy "http://' + proxyName + ':3128/";\n')
      proxyConf.close()


# ###### Write interface configuration file #################################
def writeInterfaceConfiguration(suffix, variant, interfaceName, controlBoxMode,
                                hostName, domainName, nodeIndex, siteIndex,
                                providerList, defaultProviderIndex,
                                bridgeInterface = None):
   # ====== Write Debian /etc/network/interfaces ============================
   if variant == 'Debian':
      outputFile = codecs.open('interfaces' + suffix, 'w', 'utf-8')

      outputFile.write('# ====== Loopback ======\n')
      outputFile.write('auto lo\n')
      outputFile.write('iface lo inet loopback\n\n')
      outputFile.write('iface lo inet6 loopback\n\n')

      outputFile.write('# ====== NorNet-Internal Networks ======\n')
      bridgeTo = None
      if bridgeInterface != None:
        outputFile.write('iface ' + interfaceName + ' inet manual\n\n')
        bridgeTo      = interfaceName
        interfaceName = bridgeInterface

      outputFile.write('auto ' + interfaceName + '\n')
      logSuffix = " >>/var/log/nornet-ifupdown.log 2>&1"
      for version in [ 4, 6 ]:
         providerConfigs = []
         for onlyDefault in [ True, False ]:
            providerNumber  = 0
            for providerIndex in providerList:
               if ( ((onlyDefault == True)  and (providerIndex == defaultProviderIndex)) or \
                    ((onlyDefault == False) and (providerIndex != defaultProviderIndex)) ):

                  # ====== Addressing =======================================
                  address = makeNorNetIP(providerIndex, siteIndex, nodeIndex,                  version)
                  gateway = makeNorNetIP(providerIndex, siteIndex, NorNet_NodeIndex_Tunnelbox, version)
                  metric = NorNet_RoutingMetric_AdditionalProvider + providerNumber
                  if providerIndex == defaultProviderIndex:
                     metric = NorNet_RoutingMetric_DefaultProvider
                  addrOpts = ''
                  if version == 4:
                     addrOpts = 'broadcast ' + str(address.network.broadcast_address)

                  if controlBoxMode == False:
                     network = 'default'
                  else:
                     network = str(makeNorNetIP(0, 0, 0, version))

                  # ====== Write configuration ==============================
                  if providerIndex == defaultProviderIndex:
                     if version == 4:
                        outputFile.write('iface ' + interfaceName + ' inet manual\n')
                        if bridgeTo != None:
                           outputFile.write('\tbridge_ports    ' + bridgeTo + '\n')
                           outputFile.write('\tbridge_stp      off\n')
                           outputFile.write('\tbridge_waitport 0\n')
                           outputFile.write('\tbridge_fd       0\n')
                     else:
                        outputFile.write('\niface ' + interfaceName + ' inet6 manual\n')

                  # ====== Write DNS configuration ==========================
                  if providerIndex == defaultProviderIndex:
                     outputFile.write('\tdns-nameservers ' + str(gateway.ip) + '\n')
                     outputFile.write('\tdns-search      ' + domainName + '\n')

                  providerConfigs.append([ str(address), network, str(gateway.ip), str(metric), addrOpts ])

               providerNumber = providerNumber + 1

         # ====== Write address and default route ===========================
         outputFile.write('\tpre-up          /sbin/Interface-Setup ' + interfaceName + ' ' + \
                           'pre-up    ipv' + str(version) + '\n')

         for action in [ 'up  ', 'down' ]:
            outputFile.write('\t' + action + '            /sbin/Interface-Setup ' + interfaceName + ' ' + \
                              action + '      ipv' + str(version))
            for providerConfig in providerConfigs:
               outputFile.write('\t' + \
                                providerConfig[0] + ' ' + \
                                providerConfig[1] + ' ' + \
                                providerConfig[2] + ' ' + \
                                providerConfig[3] + ' ' + \
                                '"' + providerConfig[4] + '"')
            outputFile.write('\n')

         for action in [ 'post-up  ', 'post-down' ]:
            outputFile.write('\t' + action + '       /sbin/Interface-Setup ' + interfaceName + ' ' + \
                              action + ' ipv' + str(version) + '\n')
      outputFile.close()


   # ====== Fedora /etc/sysconfig/network-scripts/ifcfg-* ===================
   elif variant == 'Fedora':
      outputFile = codecs.open('ifcfg' + suffix, 'w', 'utf-8')

      # ------ Interface is bridged ----------------------------
      bridgeTo = None
      if bridgeInterface != None:
         bridgeTo      = interfaceName
         interfaceName = bridgeInterface
 
         outputFile.write('DEVICE=' + bridgeTo + '\n')
         outputFile.write('ONBOOT=yes\n')
         outputFile.write('BOOTPROTO=none\n')
         outputFile.write('NM_CONTROLLED=no\n')
         outputFile.write('BRIDGE=' + interfaceName + '\n')
         outputFile.close()

         outputFile = codecs.open('ifcfg-bridge' + suffix, 'w', 'utf-8')
      # --------------------------------------------------------

      outputFile.write('DEVICE=' + interfaceName + '\n')
      if bridgeTo != None:
         outputFile.write('TYPE=Bridge\n')
      outputFile.write('ONBOOT=yes\n')
      outputFile.write('BOOTPROTO=static\n')
      outputFile.write('NM_CONTROLLED=no\n')

      routesIPv4 = []
      routesIPv6 = []
      for version in [ 4, 6 ]:
         secondariesIPv6 = []
         addressNumber   = 0
         for onlyDefault in [ True, False ]:
            providerNumber  = 0
            for providerIndex in providerList:
               if ( ((onlyDefault == True)  and (providerIndex == defaultProviderIndex)) or \
                    ((onlyDefault == False) and (providerIndex != defaultProviderIndex)) ):

                  # ====== Addressing =======================================
                  address = makeNorNetIP(providerIndex, siteIndex, nodeIndex,                  version)
                  gateway = makeNorNetIP(providerIndex, siteIndex, NorNet_NodeIndex_Tunnelbox, version)
                  metric = NorNet_RoutingMetric_AdditionalProvider + providerNumber
                  if providerIndex == defaultProviderIndex:
                     metric = NorNet_RoutingMetric_DefaultProvider

                  if controlBoxMode == False:
                     network = 'default'
                  else:
                     network = str(makeNorNetIP(0, 0, 0, version))

                  if version == 4:
                     outputFile.write('\nIPADDR'  + str(addressNumber) + '=' + str(address.ip)                        + '\n')
                     outputFile.write('NETMASK'   + str(addressNumber) + '=' + str(address.network.netmask)           + '\n')
                     outputFile.write('BROADCAST' + str(addressNumber) + '=' + str(address.network.broadcast_address) + '\n')
                     if providerIndex == defaultProviderIndex:
                        outputFile.write('DNS1=' + str(gateway.ip) + '\n')
                     routesIPv4.append([ str(network), str(gateway.ip), str(metric), str(address.ip) ])

                  elif version == 6:
                     if providerIndex == defaultProviderIndex:
                        outputFile.write('\nIPV6INIT=yes\n')
                        outputFile.write('IPV6_AUTOCONF=no\n')
                        outputFile.write('IPV6ADDR=' + str(address)    + '\n')
                        outputFile.write('DNS2='     + str(gateway.ip) + '\n')

                     else:
                        secondariesIPv6.append(address)
                     routesIPv6.append([ str(network), str(gateway.ip), str(metric), str(address.ip) ])

                  addressNumber = addressNumber + 1

               providerNumber = providerNumber + 1

      # ====== Write IPv6 secondaries ====================================
      secondaries = ''
      for secondaryIPv6 in secondariesIPv6:
         if len(secondaries) > 0:
            secondaries = secondaries + ' '
         secondaries = secondaries + str(secondaryIPv6)
      outputFile.write('IPV6ADDR_SECONDARIES="' + secondaries + '"\n')

      outputFile.close()


      # ====== Write routes files ===========================================
      routesIPv4File = codecs.open('route' + suffix, 'w', 'utf-8')
      for route in routesIPv4:
         routesIPv4File.write(route[0] + ' via ' + route[1] + ' src ' + route[3] + ' metric ' + route[2] + '\n')
      routesIPv4File.close()

      routesIPv6File = codecs.open('route6' + suffix, 'w', 'utf-8')
      for route in routesIPv6:
         routesIPv6File.write(route[0] + ' via ' + route[1] + ' src ' + route[3] + ' metric ' + route[2] + '\n')
      routesIPv6File.close()


   # ====== FreeBSD rc.conf =================================================
   elif variant == 'FreeBSD':
      outputFile = codecs.open('rc.conf' + suffix, 'w', 'utf-8')

      outputFile.write('hostname="' + hostName + '.' + domainName + '"\n')

      routesIPv4      = []
      routesIPv6      = []
      aliasNumber     = 0
      for onlyDefault in [ True, False ]:
         for providerIndex in providerList:
            if ( ((onlyDefault == True)  and (providerIndex == defaultProviderIndex)) or \
                  ((onlyDefault == False) and (providerIndex != defaultProviderIndex)) ):
               for version in [ 4, 6 ]:

                  if providerIndex == defaultProviderIndex:
                     aliasString = ''
                  else:
                     aliasString = '_alias' + str(aliasNumber)
                     aliasNumber = aliasNumber + 1

                  # ====== Addressing =======================================
                  address = makeNorNetIP(providerIndex, siteIndex, nodeIndex,                  version)
                  gateway = makeNorNetIP(providerIndex, siteIndex, NorNet_NodeIndex_Tunnelbox, version)

                  if controlBoxMode == False:
                     network = 'default'
                  else:
                     network = str(makeNorNetIP(0, 0, 0, version))

                  # ====== Write configuration ==============================
                  if version == 4:
                     if providerIndex == defaultProviderIndex:
                        routesIPv4.append([ str(network), str(gateway.ip) ])
                     outputFile.write('ifconfig_' + interfaceName + aliasString + '="inet ' +
                                      str(address.ip) + ' netmask ' +
                                      str(address.netmask) +
                                      '"\n')
                  else:
                     if providerIndex == defaultProviderIndex:
                        routesIPv6.append([ str(network), str(gateway.ip) ])
                     if aliasString == '':
                        ipv6String = '_ipv6'
                     else:
                        ipv6String = ''
                     outputFile.write('ifconfig_' + interfaceName + ipv6String + aliasString + '="inet6 ' +
                                      str(address.ip) + ' prefixlen ' +
                                      str(address.network.prefixlen) + '"\n')

      # ====== Routes =======================================================
      for version in [ 4, 6 ]:
         if version == 4:
            ipv6String = ''
            routes = routesIPv4
         else:
            ipv6String = 'ipv6_'
            routes = routesIPv6

         n = 0
         outputFile.write(ipv6String + 'static_routes="')
         for route in routes:
            if n > 0:
               outputFile.write(' ')
            outputFile.write('nornet' + str(n))
            n = n + 1
         outputFile.write('"\n')

         n = 0
         for route in routes:
            outputFile.write(ipv6String + 'route_nornet' + str(n) + '="-net ' + route[0] + ' ' + route[1] + '"\n')
            n = n + 1


      # ====== Services =====================================================
      outputFile.write('ntpd_enable="YES"\n')
      outputFile.write('autofs_enable="YES"\n')

      outputFile.close()

      # ====== DNS ==========================================================
      outputFile = codecs.open('resolv.conf' + suffix, 'w', 'utf-8')
      for version in [ 4, 6 ]:
         dns = makeNorNetIP(defaultProviderIndex, siteIndex, NorNet_NodeIndex_Tunnelbox, version)
         outputFile.write('nameserver ' + str(dns.ip) + '\n')
      outputFile.write('search ' + domainName + '\n')
      outputFile.close()


   # ====== Unknown variant =================================================
   else:
      error('Unknown distribution variant: ' + variant)
