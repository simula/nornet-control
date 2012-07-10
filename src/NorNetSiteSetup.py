#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet Site Setup
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


import sys;
import xmlrpclib;
import re;
import hashlib;
import datetime;

# Needs package python-ipaddr (Fedora Core, Ubuntu, Debian)!
from ipaddr import IPv4Address, IPv4Network, IPv6Address, IPv6Network;

# NorNet
from NorNetTools         import *;
from NorNetAPI           import *;
from NorNetProviderSetup import *;



# ###### Create tag type ####################################################
def makeTagType(category, description, tagName):
   found = getPLCServer().GetTagTypes(getPLCAuthentication(), tagName, ['tag_type_id'])
   if len(found) == 0:
      tagType = {}
      tagType['category']    = category
      tagType['description'] = description
      tagType['tagname']     = tagName
      getPLCServer().AddTagType(getPLCAuthentication(), tagType)


# ###### Remove NorNet site #################################################
def removeNorNetSite(siteName):
   siteID = findSiteID(siteName)
   if siteID != 0:
      log('Deleting site ' + str(siteID) + ' ...')
      getPLCServer().DeleteSite(getPLCAuthentication(), siteID)


# ###### Create NorNet site #################################################
def makeNorNetSite(siteName, siteAbbrvName, siteLoginBase, siteUrl, siteNorNetDomain,
                   siteNorNetIndex, siteCity, siteProvince, cityCountry, siteCountryCode,
                   siteLatitude, siteLogitude,
                   providerList):
  try:
      log('Adding site ' + siteName + ' ...')

      site = {}
      site['name']             = siteName
      site['abbreviated_name'] = siteAbbrvName
      site['login_base']       = siteLoginBase
      site['url']              = siteUrl
      site['enabled']          = True
      site['is_public']        = True
      site['latitude']         = siteLatitude
      site['longitude']        = siteLogitude
      site['max_slices']       = 10
      siteID = getPLCServer().AddSite(getPLCAuthentication(), site)
      if siteID <= 0:
         error('Unable to add site ' + siteName)

      if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_is_managed_site', '1') <= 0:
         error('Unable to add "nornet_is_managed_site" tag to site ' + siteName)
      if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_index', str(siteNorNetIndex)) <= 0:
         error('Unable to add "nornet_site_index" tag to site ' + siteName)
      if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_city', siteCity) <= 0:
         error('Unable to add "nornet_site_city" tag to site ' + siteName)
      if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_domain', siteNorNetDomain) <= 0:
         error('Unable to add "nornet_site_domain" tag to site ' + siteName)
      if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_province', siteProvince) <= 0:
         error('Unable to add "nornet_site_province" tag to site ' + siteName)
      if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_country', cityCountry) <= 0:
         error('Unable to add "nornet_site_country" tag to site ' + siteName)
      if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_country_code', siteCountryCode) <= 0:
         error('Unable to add "nornet_site_country_code" tag to site ' + siteName)

      i = 0
      for provider in providerList:
         if i <= NorNet_MaxProviders:
            providerName = str(provider[0])
            providerNorNetIndex = -1
            for p in NorNet_ProviderList:
               if NorNet_ProviderList[p][0] == providerName:
                  providerNorNetIndex = p
                  break
            if providerNorNetIndex <= 0:
               error("Bad provider " + provider)
            providerIPv4 = IPv4Address(provider[1])
            providerIPv6 = IPv6Address(provider[2])

            if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_tbp' + str(i) + '_index', str(providerNorNetIndex)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_index" tag to site ' + siteName)
            if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_tbp' + str(i) + '_address_ipv4', str(providerIPv4)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_ipv4" tag to site ' + siteName)
            if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_tbp' + str(i) + '_address_ipv6', str(providerIPv6)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_ipv6" tag to site ' + siteName)

         i = i + 1


      return siteID

  except Exception as e:
     error('Adding site ' + siteName + ' has failed: ' + str(e))


# ###### Create NorNet PCU ##################################################
def makeNorNetPCU(siteID, hostName, siteNorNetDomain, publicIPv4Address,
                  user, password, protocol, model, notes):
   try:
      pcuHostName = str.lower(hostName) + '.' + str.lower(siteNorNetDomain);
      log('Adding PCU ' + pcuHostName + ' ...')

      pcu = {}
      pcu['username'] = user
      pcu['password'] = password
      pcu['protocol'] = protocol
      pcu['model']    = model
      pcu['notes']    = notes
      pcu['ip']       = str(publicIPv4Address)
      pcu['hostname'] = pcuHostName

      pcuID = getPLCServer().AddPCU(getPLCAuthentication(), siteID, pcu)
      if pcuID <= 0:
         error('Unable to add PCU ' + pcuHostName)

      return pcuID

   except Exception as e:
      error('Adding PCU ' + pcuHostName + ' has failed: ' + str(e))


# ###### Update interfaces of a node ########################################
def updateNorNetInterfaces(nodeID, siteTagsList):
   try:
      # ====== Get node tags ================================================
      nodeTagList = fetchNodeTagsList(nodeID)
      nodeNorNetIndex = int(getTagValue(nodeTagList, 'nornet_node_index', '-1'))
      if nodeNorNetIndex < 0:
         error('Bad nornet_node_index setting')
      nodeNorNetAddress = int(getTagValue(nodeTagList, 'nornet_node_address', '-1'))
      if nodeNorNetAddress < 0:
         error('Bad nornet_node_address setting')

      # ====== Current interface settings ===================================
      currentAddressList     = [ ]
      currentInterfaceIDList = [ ]
      interfaceList = getPLCServer().GetInterfaces(getPLCAuthentication(), { 'node_id' : nodeID })
      for interface in interfaceList:
         interfaceID      = interface['interface_id']
         interfaceTagList = getPLCServer().GetInterfaceTags(getPLCAuthentication(),
                                                        { 'interface_id' : interfaceID })
         if int(getTagValue(interfaceTagList, 'nornet_is_managed_interface', 0)) > 0:
            currentAddressList.append(IPAddress(interface['ip']))
            currentInterfaceIDList.append(interfaceID)


      # ====== Current interface settings ===================================
      newAddressList = [ ]
      for i in range(0, NorNet_MaxProviders - 1):
         providerNorNetIndex = int(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_index', '-1'))
         if providerNorNetIndex >= 0:
            siteNorNetIndex = int(getTagValue(siteTagsList, 'nornet_site_index', '-1'))
            if siteNorNetIndex < 0:
               error('Bad nornet_site_index setting')

            providerIPv4 = getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv4', '')
            # providerIPv6 = getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv6', '')
            if providerIPv4 != '':
               ifIPv4 = makeNorNetIP(providerNorNetIndex, siteNorNetIndex, nodeNorNetAddress, 4)
               newAddressList.append(IPv4Address(ifIPv4.ip))


      # ====== Update interfaces ============================================
      if currentAddressList == newAddressList:
         return(0)

      siteNorNetDomain = getTagValue(siteTagsList, 'nornet_site_domain', '')
      if siteNorNetIndex == '':
         error('Bad nornet_site_domain setting')
      siteNorNetIndex = int(getTagValue(siteTagsList, 'nornet_site_index', '-1'))
      if siteNorNetIndex < 0:
         error('Bad nornet_site_index setting')

      for i in range(0, NorNet_MaxProviders - 1):
         providerNorNetIndex = int(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_index', '-1'))
         if providerNorNetIndex >= 0:
            providerNorNetName = getNorNetProviderInfo(providerNorNetIndex)[1]

            ifHostName        = 'node' + str(nodeNorNetIndex) + '-' + str.lower(providerNorNetName) + '.' + str.lower(siteNorNetDomain)
            ifIPv4            = makeNorNetIP(providerNorNetIndex, siteNorNetIndex, nodeNorNetAddress, 4)
            ifGateway         = makeNorNetIP(providerNorNetIndex, siteNorNetIndex, 1, 4)
            ifProviderNetwork = makeNorNetIP(providerNorNetIndex, 0, 0, 4)
            ifAlias           = providerNorNetIndex

            interface = {}
            interface['hostname']   = ifHostName
            interface['is_primary'] = False
            interface['ifname']     = 'eth0'
            interface['type']       = 'ipv4'
            interface['method']     = 'static'
            interface['ip']         = str(ifIPv4.ip)
            interface['netmask']    = str(ifIPv4.netmask)
            interface['network']    = str(ifIPv4.network)
            interface['broadcast']  = str(ifIPv4.broadcast)
            interface['gateway']    = str(ifGateway.ip)

            interfaceID = getPLCServer().AddInterface(getPLCAuthentication(), nodeID, interface)
            if interfaceID <= 0:
               error('Unable to add secondary interface ' + str(ifIPv4.ip))

            if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, "alias", str(ifAlias)) <= 0:
               error('Unable to add "alias" tag to interface ' + str(ifIPv4.ip))

            if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, 'nornet_is_managed_interface', '1') <= 0:
               error('Unable to add "nornet_is_managed_interface" tag to interface ' + str(ifIPv4.ip))
            if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, 'nornet_ifprovider_index', str(providerNorNetIndex)) <= 0:
               error('Unable to add "nornet_ifprovider_index" tag to interface ' + str(ifIPv4.ip))

      return(1)

   except Exception as e:
      error('Updating interfaces of node ' + str(nodeID) + ' has failed: ' + str(e))


# ###### Create NorNet node #################################################
def makeNorNetNode(siteID, nodeNiceName, nodeNorNetIndex, firstAddressNumber,
                   pcuID, pcuPort,
                   publicIPv4Address, publicGateway, publicDNS):
   nodeHostName = nodeNiceName   # Domain to be set below!
   try:
      # ====== Get site information =========================================
      siteTagsList    = fetchSiteTagsList(siteID)
      siteNorNetIndex = int(getTagValue(siteTagsList, 'nornet_site_index', '-1'))
      if siteNorNetIndex < 0:
         error("Site " + str(siteID) + ' has no NorNet site index!')
      siteNorNetDomain = getTagValue(siteTagsList, 'nornet_site_domain', '')
      if siteNorNetIndex == '':
         error("Site " + str(siteID) + ' has no NorNet domain name!')


      # ====== Create node ==================================================
      nodeHostName = nodeHostName + '.' + str.lower(siteNorNetDomain);
      log('Adding node ' + nodeHostName + ' ...')

      node = {}
      node['hostname']   = nodeHostName
      node['boot_state'] = 'reinstall'
      node['model']      = 'Amiga 5000'
      nodeID = getPLCServer().AddNode(getPLCAuthentication(), siteID, node)
      if nodeID <= 0:
         error('Unable to add node ' + nodeHostName)

      if getPLCServer().AddNodeTag(getPLCAuthentication(), nodeID, 'nornet_is_managed_node', '1') <= 0:
         error('Unable to add "nornet_is_managed_node" tag to node ' + nodeHostName)
      if getPLCServer().AddNodeTag(getPLCAuthentication(), nodeID, 'nornet_node_index', str(nodeNorNetIndex)) <= 0:
         error('Unable to add "nornet_node_index" tag to node ' + nodeHostName)
      if getPLCServer().AddNodeTag(getPLCAuthentication(), nodeID, 'nornet_node_address', str(nodeNorNetIndex + firstAddressNumber)) <= 0:
         error('Unable to add "nornet_node_address" tag to node ' + nodeHostName)


      # ====== Add node to PCU ==============================================
      if pcuID > 0:
         if getPLCServer().AddNodeToPCU(getPLCAuthentication(), nodeID, pcuID, pcuPort) != 1:
            error('Unable to add node ' + nodeHostName + " to PCU " + str(pcuID) + ", port " + str(pcuPort))


      # ====== Create primary interface =====================================
      interface = {}
      interface['hostname']   = nodeHostName
      interface['is_primary'] = True
      interface['ifname']     = 'eth0'
      interface['type']       = 'ipv4'
      interface['method']     = 'static'
      interface['ip']         = str(publicIPv4Address.ip)
      interface['netmask']    = str(publicIPv4Address.netmask)
      interface['network']    = str(publicIPv4Address.network)
      interface['broadcast']  = str(publicIPv4Address.broadcast)
      interface['gateway']    = str(publicGateway)
      interface['dns1']       = str(publicDNS[0])
      if len(publicDNS) > 1:
         interface['dns2']    = str(publicDNS[1])
      if getPLCServer().AddInterface(getPLCAuthentication(), nodeID, interface) <= 0:
         error('Unable to add primary interface ' + str(publicIPv4Address.ip))


      # ====== Create NorNet interfaces =====================================
      updateNorNetInterfaces(nodeID, siteTagsList)

      return nodeID

   except Exception as e:
      error('Adding node ' + nodeHostName + ' has failed: ' + str(e))
