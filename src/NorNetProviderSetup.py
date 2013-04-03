#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet Provider Setup
# Copyright (C) 2012-2013 by Thomas Dreibholz
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


import hashlib;

# Needs package python-ipaddr (Fedora Core, Ubuntu, Debian)!
from ipaddr import IPv4Address, IPv4Network, IPv6Address, IPv6Network;

# NorNet
from NorNetTools import *;


# ====== Adapt if necessary =================================================

NorNet_ProviderList = {
#   ID     Name                                Short Name (ASCII only!)
# =====================================================================
     0 : [ 'UNKNOWN',                          'unknown'   ],

   # ------ Norway ---------------------------------------------
     1 : [ 'Uninett',                          'uninett'   ],
     2 : [ 'Hafslund',                         'hafslund'  ],
     3 : [ 'ICE',                              'ice'       ],

     4 : [ 'Telenor',                          'telenor'   ],
     5 : [ 'NetCom',                           'netcom'    ],
     6 : [ 'Tele2',                            'tele2'     ],
     7 : [ 'Network Norway',                   'netnorway' ],

   # ------ Germany --------------------------------------------
    30 : [ 'Deutsches Forschungsnetz',         'dfn'       ],
    31 : [ 'Versatel',                         'versatel'  ],
    32 : [ 'Deutsche Telekom',                 'dtag'      ]

}

# Prefixes for the internal IPv4 and IPv6 networks
NorNet_IPv4Prefix = IPv4Network('10.0.0.0/8')       # /8 prefix for internal IPv4 space (e.g. '10.0.0.0/8')
NorNet_IPv6Prefix = IPv6Network('fd00:0000::/32')   # /32 prefix for internal IPv6 space (e.g. 'fd00:0000::/32')

# The domain name of the central site
# (it will e.g. be used with the alias 'nfs' to look up the file server!)
NorNet_CentralSite_DomainName = 'simula.nornet'

# Source NAT range for IPv4 (to be set up at Central Site)
# NorNet_CentralSiteIPv4NATRange = [ IPv4Address('132.252.156.240'), IPv4Address('132.252.156.249') ]
NorNet_CentralSiteIPv4NATRange = [ IPv4Address('0.0.0.0'), IPv4Address('0.0.0.0') ]

# Public tunnelbox IP of Central Site for Default Provider. Needed for bootstrapping other tunnelboxes!
NorNet_CentralSite_BootstrapTunnelbox     = IPv4Address('128.39.36.143')
NorNet_CentralSite_BootstrapProviderIndex = 1

# TOS Settings for provider selection
NorNet_TOSSettings = [ 0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C ]

# Maximum number of NTP servers (e.g. 6+6 = 6x IPv4 + 6x IPv6)
NorNet_MaxNTPServers = 12

# ===========================================================================

# Maximum number of providers per site
NorNet_MaxProviders = 8

# NorNet Internet connection to/from outside world goes via Site 1!
NorNet_SiteIndex_Central = 1

# NorNet Tunnelbox is always Node 1!
NorNet_NodeIndex_Tunnelbox = 1

# PLC is Node 2 on the Central Site!
NorNet_SiteIndex_PLC = NorNet_SiteIndex_Central
NorNet_NodeIndex_PLC = 2

# NorNet Monitor is Node 3 on the Central Site!
NorNet_SiteIndex_Monitor  = NorNet_SiteIndex_Central
NorNet_NodeIndex_Monitor  = 3

# NorNet Monitor is Node 4 on the Central Site!
NorNet_SiteIndex_FileSrv  = NorNet_SiteIndex_Central
NorNet_NodeIndex_FileSrv  = 4



# ###### Get NorNet provider information ####################################
def getNorNetProviderInfo(providerIndex):
   try:
      return NorNet_ProviderList[providerIndex]
   except:
      return NorNet_ProviderList[0]


# ###### Get NorNet interface IPv4 address ##################################
def makeNorNetIP(provider, site, node, subnode, version):
   p = int(provider)
   s = int(site)
   n = int(node)
   v = int(subnode)
   if ((p < 0) | (p > 255)):
      error('Bad provider ID')
   if ((s < 0) | (s > 255)):
      error('Bad site ID')
   if ((n < 0) | (n > 255)):
      error('Bad host ID')

   # ====== IPv4 handling ===================================================
   if version == 4:
      if v > 0:   # Ignore negative values!
         error('Bad subnode ID; must be 0 for IPv4')
      if s != 0:
         prefix = 24;    # NorNet + Provider + Site
      elif p != 0:
         prefix = 16;    # NorNet + Provider
      else:
         prefix = 8;     # NorNet
      a = IPv4Address('0.' + str(p) + '.' + str(s) + '.' + str(n))
      a = int(NorNet_IPv4Prefix) | int(a)
      return IPv4Network(str(IPv4Address(a)) + '/' + str(prefix))

   # ====== IPv6 handling ===================================================
   else:
      nodeNet = n
      nodeNum = 0
      if v != 0:
         prefix = 64     # NorNet + Provider + Site + NodeNetwork + VirtalNodeNet
         if v < 0:       # Special case: NodeNetwork zero; get IP of node in this network.
             v = 0
             nodeNet = 0
             nodeNum = n
      elif n != 0:
         prefix = 56     # NorNet + Provider + Site + NodeNetwork
      elif s != 0:
         prefix = 48;    # NorNet + Provider + Site
      elif p != 0:
         prefix = 40;    # NorNet + Provider
      else:
         prefix = 32;    # NorNet
      a = IPv6Address('0:0:' + \
                      str.replace(hex((p << 8) | s), '0x', '') + ':' + \
                      str.replace(hex((nodeNet << 8) | v), '0x', '') + '::' + \
                      str.replace(hex(nodeNum), '0x', ''))
      a = int(NorNet_IPv6Prefix) | int(a)
      return IPv6Network(str(IPv6Address(a)) + '/' + str(prefix))


# ###### Get NorNet information from address ################################
def getNorNetInformationForAddress(address):
   norNetInformation = None
   if NorNet_IPv6Prefix.Contains(address):
      a = int(address)
      b = int((a >> 64) & 0xffffffff)
      norNetInformation = {
         'address':        address,
         'provider_index': (b & 0xff000000) >> 24,
         'site_index':     (b & 0x00ff0000) >> 16,
         'node_index':     (b & 0x0000ff00) >> 8,
         'vnet_index':     (b & 0x000000ff)
      }

   if NorNet_IPv4Prefix.Contains(address):
      a = int(address)
      norNetInformation = {
         'address':        address,
         'provider_index': (a & 0x00ff0000) >> 16,
         'site_index':     (a & 0x0000ff00) >> 8,
         'node_index':     (a & 0x000000ff),
         'vnet_index':     None
      }

   return norNetInformation


# ###### Get NorNet information about myself (host) #########################
def getMyNorNetInformation():
   localAddressList = getLocalAddresses(6)
   for address in localAddressList:
      if NorNet_IPv6Prefix.Contains(address):
         return getNorNetInformationForAddress(address)

   localAddressList = getLocalAddresses(4)
   for address in localAddressList:
      if NorNet_IPv4Prefix.Contains(address):
         return getNorNetInformationForAddress(address)

   return None


# ###### Get NorNet tunnel inner IPv4 address ###############################
def makeNorNetTunnelIP(outgoingSite, outgoingProvider, incomingSite, incomingProvider, version):
   if ((outgoingSite < 0) | (outgoingSite > 255)):
      error('Bad site ID')
   if ((incomingSite < 0) | (incomingSite > 255)):
      error('Bad site ID')
   if ((outgoingProvider < 0) | (outgoingProvider > 255)):
      error('Bad provider ID')
   if ((incomingProvider < 0) | (incomingProvider > 255)):
      error('Bad provider ID')

   if ((outgoingSite == 0) and (incomingSite == 0)):
      if version == 4:
         return IPv4Network('192.168.0.0/16')
      else:
         return IPv6Network('fdff:ffff::/32')

   if incomingSite < outgoingSite:
      side  = 1
      sLow  = incomingSite
      pLow  = incomingProvider
      sHigh = outgoingSite
      pHigh = outgoingProvider
   else:
      side  = 2
      sLow  = outgoingSite
      pLow  = outgoingProvider
      sHigh = incomingSite
      pHigh = incomingProvider


   source      = str.replace(hex((sHigh << 8) | pHigh), '0x', '')
   destination = str.replace(hex((sLow << 8)  | pLow), '0x', '')
   address     = 'fdff:ffff:' + source + ':' + destination + '::'
   if version == 4:
      # The space is to small in IPv4 addresses. Use MD5 to create most likely
      # unique addresses.
      m = hashlib.md5()
      m.update(address)
      s = m.hexdigest()
      address = (int(s[0:4], 16) & 0xfffc) | side
      address = int(IPv4Address('192.168.0.0')) | address
      return IPv4Network(str(IPv4Address(address)) + '/30')
   else:
      address = address + str(side)
      return IPv6Network(address + '/64')


# ###### Get NorNet interface IPv4 address ##################################
def makeNorNetTunnelKey(outgoingSite, outgoingProvider, incomingSite, incomingProvider):
   if ((outgoingSite < 0) | (outgoingSite > 255)):
      error('Bad site ID')
   if ((incomingSite < 0) | (incomingSite > 255)):
      error('Bad site ID')
   if ((outgoingProvider < 0) | (outgoingProvider > 255)):
      error('Bad provider ID')
   if ((incomingProvider < 0) | (incomingProvider > 255)):
      error('Bad provider ID')

   if incomingSite < outgoingSite:
      sLow  = incomingSite
      pLow  = incomingProvider
      sHigh = outgoingSite
      pHigh = outgoingProvider
   else:
      sLow  = outgoingSite
      pLow  = outgoingProvider
      sHigh = incomingSite
      pHigh = incomingProvider

   tunnelID = (sLow << 24) | (pLow << 16) | \
              (sHigh << 8) | (pHigh)
   return(tunnelID)


# ###### Get tunnel configuration ###########################################
def getTunnel(localSite, localProvider, remoteSite, remoteProvider, version):
   localSiteIndex      = localSite['site_index']
   localProviderIndex  = localProvider['provider_index']
   remoteProviderIndex = remoteProvider['provider_index']
   remoteSiteIndex     = remoteSite['site_index']

   # ====== Get tunnel configuration ========================================
   tunnelOverIPv4 = False
   if (version != 4):
      try:
         localOuterAddress  = localProvider['provider_tunnelbox_ipv6']
         remoteOuterAddress = remoteProvider['provider_tunnelbox_ipv6']
         if ((localOuterAddress == IPv6Address('::')) or (remoteOuterAddress == IPv6Address('::'))):
            tunnelOverIPv4 = True
         else:
            tunnelInterface = 'seks' + str(remoteSiteIndex) + "-" + str(localProviderIndex) + '-' + str(remoteProviderIndex)
      except:
         tunnelOverIPv4 = True

   if ((version == 4) or (tunnelOverIPv4 == True)):
      localOuterAddress  = localProvider['provider_tunnelbox_ipv4']
      remoteOuterAddress = remoteProvider['provider_tunnelbox_ipv4']
      tunnelInterface    = 'gre' + str(remoteSiteIndex) + "-" + str(localProviderIndex) + '-' + str(remoteProviderIndex)

   localInnerAddress     =  makeNorNetTunnelIP(localSiteIndex, localProviderIndex,
                                               remoteSiteIndex, remoteProviderIndex, version)
   remoteInnerAddress    =  makeNorNetTunnelIP(remoteSiteIndex, remoteProviderIndex,
                                               localSiteIndex, localProviderIndex, version)
   tunnelKey = makeNorNetTunnelKey(localSiteIndex, localProviderIndex,
                                   remoteSiteIndex, remoteProviderIndex)

   # ====== Create tunnel structure =========================================
   norNetTunnel = {
      'tunnel_interface'            : tunnelInterface,
      'tunnel_local_outer_address'  : localOuterAddress,
      'tunnel_remote_outer_address' : remoteOuterAddress,
      'tunnel_local_inner_address'  : localInnerAddress,
      'tunnel_remote_inner_address' : remoteInnerAddress,
      'tunnel_key'                  : tunnelKey,
      'tunnel_over_ipv4'            : tunnelOverIPv4
   }

   return norNetTunnel
