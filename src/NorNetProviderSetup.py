#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NorNet Provider Setup
# Copyright (C) 2012-2026 by Thomas Dreibholz
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

import hashlib

from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

# NorNet
import NorNetConfiguration
from NorNetTools import *



# ###### Get NorNet interface IPv4 address ##################################
def makeNorNetIP(provider, site, node, version, sliceIndex = 0):
   p = int(provider)
   s = int(site)
   n = int(node)
   if ((p < NorNetConfiguration.NorNet_MinProviderIndex - 1) or (p > NorNetConfiguration.NorNet_MaxProviderIndex)):
      error('Bad provider index')
   if ((s < NorNetConfiguration.NorNet_MinSiteIndex - 1) or (s > NorNetConfiguration.NorNet_MaxSiteIndex)):
      error('Bad site index')
   if ((n < NorNetConfiguration.NorNet_MinNodeIndex - 1) or (n > NorNetConfiguration.NorNet_MaxNodeIndex)):
      error('Bad node index')
   if ((sliceIndex < NorNetConfiguration.NorNet_MinSliceIndex - 1) or (sliceIndex > NorNetConfiguration.NorNet_MaxSliceIndex)):
      error('Bad slice index')

   # ====== IPv4 handling ===================================================
   if version == 4:
      if s != 0:
         prefix = 24;    # NorNet + Provider + Site
      elif p != 0:
         prefix = 16;    # NorNet + Provider
      else:
         prefix = 8;     # NorNet

      # For IPv4, we only have the slice node index.
      if sliceIndex != 0:
         # Replace the node index by the slice index.
         n = sliceIndex

      a = IPv4Address('0.' + str(p) + '.' + str(s) + '.' + str(n))
      a = int(NorNetConfiguration.NorNet_Configuration['NorNet_IPv4Prefix']) | int(a)
      return IPv4Interface(str(IPv4Address(a)) + '/' + str(prefix))

   # ====== IPv6 handling ===================================================
   else:
      if s != 0:
         prefix = 64;    # NorNet + Provider + Site
      elif p != 0:
         prefix = 56;    # NorNet + Provider
      else:
         prefix = 48;    # NorNet

      # For IPv6, we have enough space to encode node index and slice node index!

      a = IPv6Address('0:0:0:' + \
                      str.replace(hex((p << 8) | s), '0x', '') + '::' + \
                      str.replace(hex(sliceIndex), '0x', '') + ':' + \
                      str.replace(hex(n), '0x', ''))
      a = IPv6Address(int(NorNetConfiguration.NorNet_Configuration['NorNet_IPv6Prefix']) | int(a))
      return IPv6Interface(str(a) + '/' + str(prefix))


# ###### Get NorNet information from address ################################
def getNorNetInformationForAddress(address):
   norNetInformation = None
   if address in NorNetConfiguration.NorNet_Configuration['NorNet_IPv6Prefix'].network:
      a = int(address)
      b = int((a >> 64) & 0xffffffff)
      norNetInformation = {
         'address':        address,
         'provider_index': (b & 0xff000000) >> 24,
         'site_index':     (b & 0x00ff0000) >> 16,
         'node_index':     (b & 0x0000ff00) >> 8,
         'vnet_index':     (b & 0x000000ff)
      }

   if address in NorNetConfiguration.NorNet_Configuration['NorNet_IPv4Prefix'].network:
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
      if address in NorNetConfiguration.NorNet_Configuration['NorNet_IPv6Prefix'].network:
         return getNorNetInformationForAddress(address)

   localAddressList = getLocalAddresses(4)
   for address in localAddressList:
      if address in NorNetConfiguration.NorNet_Configuration['NorNet_IPv4Prefix'].network:
         return getNorNetInformationForAddress(address)

   return None


# ###### Get NorNet tunnel inner IPv4 address ###############################
def makeNorNetTunnelIP(outgoingSite, outgoingProvider, incomingSite, incomingProvider, version):
   if ((outgoingSite < NorNetConfiguration.NorNet_MinSiteIndex - 1) or (outgoingSite > NorNetConfiguration.NorNet_MaxSiteIndex)):
      error('Bad site index')
   if ((incomingSite < NorNetConfiguration.NorNet_MinSiteIndex - 1) or (incomingSite > NorNetConfiguration.NorNet_MaxSiteIndex)):
      error('Bad site index')
   if ((outgoingProvider < NorNetConfiguration.NorNet_MinProviderIndex - 1) or (outgoingProvider > NorNetConfiguration.NorNet_MaxProviderIndex)):
      error('Bad provider index')
   if ((incomingProvider < NorNetConfiguration.NorNet_MinProviderIndex - 1) or (incomingProvider > NorNetConfiguration.NorNet_MaxProviderIndex)):
      error('Bad provider index')

   if ((outgoingSite == 0) and (incomingSite == 0)):
      if version == 4:
         return NorNetConfiguration.NorNet_Configuration['NorNet_IPv4TunnelPrefix']
      else:
         return NorNetConfiguration.NorNet_Configuration['NorNet_IPv6TunnelPrefix']

   if incomingSite < outgoingSite:
      side  = 0
      sLow  = incomingSite
      pLow  = incomingProvider
      sHigh = outgoingSite
      pHigh = outgoingProvider
   else:
      side  = 1
      sLow  = outgoingSite
      pLow  = outgoingProvider
      sHigh = incomingSite
      pHigh = incomingProvider


   source      = str.replace(hex((sHigh << 8) | pHigh), '0x', '')
   destination = str.replace(hex((sLow << 8)  | pLow), '0x', '')
   address     = IPv6Address(int(NorNetConfiguration.NorNet_Configuration['NorNet_IPv6TunnelPrefix'].ip) | int(IPv6Address('0:0:0:0:0:' + source + ':' + destination + ':0')))
   if version == 4:
      # The space is too small in IPv4 addresses. Use MD5 to create most likely
      # unique addresses.
      m = hashlib.md5()
      label = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' + str(address)
      m.update(label.encode('utf-8'))
      s = m.hexdigest()
      value   = int(s[0:8], 16) & 0xfffffffe
      mask    = ~int(NorNetConfiguration.NorNet_Configuration['NorNet_IPv4TunnelPrefix'].netmask) & 0xffffffff
      prefix  = int(NorNetConfiguration.NorNet_Configuration['NorNet_IPv4TunnelPrefix'])
      address = prefix | ((value & mask) | side)
      return IPv4Interface(str(IPv4Address(address)) + '/31')
   else:
      address = IPv6Address(int(address) | (side + 1))
      return IPv6Interface(str(address) + '/112')


# ###### Get NorNet interface IPv4 address ##################################
def makeNorNetTunnelKey(outgoingSite, outgoingProvider, incomingSite, incomingProvider):
   if ((outgoingSite < NorNetConfiguration.NorNet_MinSiteIndex) or (outgoingSite > NorNetConfiguration.NorNet_MaxSiteIndex)):
      error('Bad site index')
   if ((incomingSite < NorNetConfiguration.NorNet_MinSiteIndex) or (incomingSite > NorNetConfiguration.NorNet_MaxSiteIndex)):
      error('Bad site index')
   if ((outgoingProvider < NorNetConfiguration.NorNet_MinProviderIndex) or (outgoingProvider > NorNetConfiguration.NorNet_MaxProviderIndex)):
      error('Bad provider index')
   if ((incomingProvider < NorNetConfiguration.NorNet_MinProviderIndex) or (incomingProvider > NorNetConfiguration.NorNet_MaxProviderIndex)):
      error('Bad provider index')

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
         if ((localOuterAddress.ip == IPv6Address('::')) or (remoteOuterAddress.ip == IPv6Address('::'))):
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
