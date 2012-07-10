#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet Provider Setup
# Copyright (C) 2012 by Thomas Dreibholz
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


NorNet_MaxProviders = 8
NorNet_ProviderList = {
#   ID     Name                                Short Name (ASCII only!)
# =====================================================================
     0 : [ 'UNKNOWN',                          'unknown'  ],

     1 : [ 'Uninett',                          'uninett'  ],
     2 : [ 'Hafslund',                         'hafslund' ],

   100 : [ 'Telenor',                          'telenor'  ],
   101 : [ 'NetCom',                           'netcom'   ],
   102 : [ 'Tele2',                            'tele2'    ],
   103 : [ 'ICE',                              'ice'      ],

   222 : [ 'Deutsches Forschungsnetz',         'dfn'      ],
}
NorNet_TOSSettings = [ 0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C ]


# ###### Get NorNet provider information ####################################
def getNorNetProviderInfo(providerIndex):
   try:
      return NorNet_ProviderList[providerIndex]
   except:
      return NorNet_ProviderList[0]


# ###### Get NorNet interface IPv4 address ##################################
def makeNorNetIP(provider, site, host, version):
   p = int(provider)
   s = int(site)
   h = int(host)
   if ((p < 0) | (p > 255)):
      error('Bad provider ID')
   if ((s < 0) | (s > 255)):
      error('Bad site ID')
   if ((h < 0) | (h > 255)):
      error('Bad host ID')

   if version == 4:
      if site != 0:
         prefix = 24;
      else:
         prefix = 16;
      return IPv4Network('10.' + str(p) + '.' + str(s) + '.' + str(h) + '/' + str(prefix))
   else:
      if site != 0:
         prefix = 48;
      else:
         prefix = 32;
      return IPv6Network('fd00:' + \
                          str.replace(hex(p), '0x', '') + ':' + \
                          str.replace(hex(s), '0x', '') + ':' + \
                          str.replace(hex(h), '0x', '') + ':0:0::/' + str(prefix))


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
      address = (long(s[0:4], 16) & 0xfffc) | side
      address = int(IPv4Address('192.168.0.0')) | address
      return IPv4Address(address)
   else:
      address = address + str(side)
      return IPv6Address(address)


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
