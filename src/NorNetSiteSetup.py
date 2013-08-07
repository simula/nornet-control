#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet Site Setup
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


import sys;
import re;
import hashlib;
import datetime;

# Needs package python-ipaddr (Fedora Core, Ubuntu, Debian)!
from ipaddr import IPNetwork, IPv4Address, IPv4Network, IPv6Address, IPv6Network;

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


# ###### Create NorNet tag types ############################################
def makeNorNetTagTypes():
   # ====== Create tags =====================================================
   makeTagType('site/nornet', 'NorNet Managed Site',                      'nornet_is_managed_site')
   makeTagType('site/nornet', 'NorNet Site Index',                        'nornet_site_index')
   makeTagType('site/nornet', 'NorNet Site Domain Name',                  'nornet_site_domain')
   makeTagType('site/nornet', 'NorNet Site UTF-8',                        'nornet_site_utf8')
   makeTagType('site/nornet', 'NorNet Site City',                         'nornet_site_city')
   makeTagType('site/nornet', 'NorNet Site Province',                     'nornet_site_province')
   makeTagType('site/nornet', 'NorNet Site Country',                      'nornet_site_country')
   makeTagType('site/nornet', 'NorNet Site Country Code',                 'nornet_site_country_code')
   makeTagType('site/nornet', 'NorNet Site Altitude',                     'nornet_site_altitude')
   makeTagType('site/nornet', 'NorNet Site Default Provider Index',       'nornet_site_default_provider_index')
   makeTagType('site/nornet', 'NorNet Site Tunnelbox Internal Interface', 'nornet_site_tb_internal_interface')
   for i in range(0, NorNet_MaxNTPServers - 1):
      makeTagType('site/nornet', 'NorNet Site NTP Server ' + str(1 + i),  'nornet_site_ntp' + str(1 + i))

   for i in range(0, NorNet_MaxProviders - 1):
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Index',        'nornet_site_tbp' + str(i) + '_index')
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Interface',    'nornet_site_tbp' + str(i) + '_interface')
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Address IPv4', 'nornet_site_tbp' + str(i) + '_address_ipv4')
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Address IPv6', 'nornet_site_tbp' + str(i) + '_address_ipv6')
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Gateway IPv4', 'nornet_site_tbp' + str(i) + '_gateway_ipv4')
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Gateway IPv6', 'nornet_site_tbp' + str(i) + '_gateway_ipv6')

   makeTagType('node/nornet',      'NorNet Managed Node',             'nornet_is_managed_node')
   makeTagType('node/nornet',      'NorNet Node UTF-8',               'nornet_node_utf8')
   makeTagType('node/nornet',      'NorNet Node Index',               'nornet_node_index')
   makeTagType('node/nornet',      'NorNet Node Interface',           'nornet_node_interface')

   makeTagType('interface/nornet', 'NorNet Managed Interface',        'nornet_is_managed_interface')
   makeTagType('interface/nornet', 'NorNet Interface Provider Index', 'nornet_ifprovider_index')


# ###### Remove NorNet site #################################################
def removeNorNetSite(siteName):
   site = fetchNorNetSite(siteName, False)
   if site != None:
      if int(getTagValue(site['site_tags'], 'nornet_is_managed_site', '-1')) < 1:
         error('removeNorNetSite() will only remove NorNet sites!')
      log('Removing NorNet site ' + siteName + ' ...')
      siteID = site['site_id']
      getPLCServer().DeleteSite(getPLCAuthentication(), siteID)
   else:
      log('Site not found: ' + siteName)


# ###### Add or update site tag #############################################
def _addOrUpdateSiteTag(siteID, tagName, tagValue):
   filter = {
      'tagname' : tagName,
      'site_id' : siteID
   }
   tags = getPLCServer().GetSiteTags(getPLCAuthentication(), filter, ['site_tag_id'])
   if len(tags) == 0:
      return getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, tagName, tagValue)
   else:
      return getPLCServer().UpdateSiteTag(getPLCAuthentication(), tags[0]['site_tag_id'], tagValue)


# ###### Create NorNet site #################################################
def makeNorNetSite(siteName, siteAbbrvName, siteEnabled, siteLoginBase, siteUrl, siteNorNetDomain,
                   siteNorNetIndex, siteCity, siteProvince, cityCountry, siteCountryCode,
                   siteLatitude, siteLogitude, siteAltitude,
                   providerList, defaultProvider, tbInternalInterface,
                   dnsServers, ntpServers):
   siteLabel= makeNameFromUnicode(siteName, False)
   siteName = siteLabel['ascii']
   try:
      # ====== Add site =====================================================
      log('Adding site ' + siteName + ' ...')
      site = {}
      site['name']             = siteName
      site['abbreviated_name'] = siteAbbrvName
      site['login_base']       = siteLoginBase
      site['url']              = siteUrl
      site['is_public']        = True
      site['latitude']         = siteLatitude
      site['longitude']        = siteLogitude
      site['max_slices']       = 10
      if siteEnabled == True:
         site['enabled']       = True
      else:
         site['enabled']       = False

      siteID = lookupSiteID(siteName)
      if siteID == 0:
         siteID = getPLCServer().AddSite(getPLCAuthentication(), site)
      else:
         if getPLCServer().UpdateSite(getPLCAuthentication(), siteID, site) != 1:
            siteID = 0
      if siteID <= 0:
         error('Unable to add/update site ' + siteName)

      # ====== Set NorNet tags ==============================================
      if _addOrUpdateSiteTag(siteID, 'nornet_is_managed_site', '1') <= 0:
         error('Unable to add "nornet_is_managed_site" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_index', str(siteNorNetIndex)) <= 0:
         error('Unable to add "nornet_site_index" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_utf8', siteLabel['utf8']) <= 0:
         error('Unable to add "nornet_site_utf8" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_city', siteCity) <= 0:
         error('Unable to add "nornet_site_city" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_domain', siteNorNetDomain) <= 0:
         error('Unable to add "nornet_site_domain" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_province', siteProvince) <= 0:
         error('Unable to add "nornet_site_province" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_country', cityCountry) <= 0:
         error('Unable to add "nornet_site_country" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_country_code', siteCountryCode) <= 0:
         error('Unable to add "nornet_site_country_code" tag to site ' + siteName)
      if _addOrUpdateSiteTag(siteID, 'nornet_site_altitude', str(siteAltitude)) <= 0:
         error('Unable to add "nornet_site_altitude" tag to site ' + siteName)

      # ====== Set providers ================================================
      gotDefaultProvider = False
      i = 0
      for provider in providerList:
         if i <= NorNet_MaxProviders:
            providerName = str(provider[0])
            providerIndex = -1
            for p in NorNet_ProviderList:
               if NorNet_ProviderList[p][0] == providerName:
                  providerIndex = p
                  break
            if providerIndex <= 0:
               error("Bad provider " + provider)
            if providerName == defaultProvider:
               if _addOrUpdateSiteTag(siteID, 'nornet_site_default_provider_index', str(providerIndex)) <= 0:
                  error('Unable to add "nornet_site_default_provider_index" tag to site ' + siteName)
               gotDefaultProvider = True

            providerInterface   = str(provider[1])
            providerAddressIPv4 = IPv4Network(provider[2])
            providerGatewayIPv4 = IPv4Address(provider[3])
            providerAddressIPv6 = IPv6Network(provider[4])
            providerGatewayIPv6 = IPv6Address(provider[5])

            if _addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_index', str(providerIndex)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_index" tag to site ' + siteName)
            if _addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_interface', providerInterface) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_interface" tag to site ' + siteName)
            if _addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_address_ipv4', str(providerAddressIPv4)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_address_ipv4" tag to site ' + siteName)
            if _addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_address_ipv6', str(providerAddressIPv6)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_address_ipv6" tag to site ' + siteName)
            if _addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_gateway_ipv4', str(providerGatewayIPv4)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_gateway_ipv4" tag to site ' + siteName)
            if _addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_gateway_ipv6', str(providerGatewayIPv6)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_gateway_ipv6" tag to site ' + siteName)

         i = i + 1

      if gotDefaultProvider == False:
         error('Site ' + siteName + ' is not connected to default provider ' + defaultProvider)

      # ====== Set NTP servers ==============================================
      for i in range(0, NorNet_MaxNTPServers - 1):
         if i >= len(ntpServers):
            break
         if _addOrUpdateSiteTag(siteID, 'nornet_site_ntp' + str(1 + i), str(IPNetwork(ntpServers[i]).ip)) <= 0:
            error('Unable to add "nornet_site_ntp' + str(1 + i) + '" tag to site ' + siteName)

      if _addOrUpdateSiteTag(siteID, 'nornet_site_tb_internal_interface', tbInternalInterface) <= 0:
         error('Unable to add "nornet_site_tb_internal_interface" tag to site ' + siteName)

   except Exception as e:
      error('Adding site ' + siteName + ' has failed: ' + str(e))

   return fetchNorNetSite(siteName, False)


# ###### Create NorNet PCU ##################################################
def makeNorNetPCU(site, hostName, siteNorNetDomain, publicIPv4Address,
                  user, password, protocol, model, notes):
   try:
      pcuHostName = str.lower(hostName) + '.' + str.lower(siteNorNetDomain);
      log('Adding PCU ' + pcuHostName + ' to site ' + site['site_long_name'] + ' ...')

      pcu = {}
      pcu['username'] = user
      pcu['password'] = password
      pcu['protocol'] = protocol
      pcu['model']    = model
      pcu['notes']    = notes
      pcu['ip']       = str(publicIPv4Address)
      pcu['hostname'] = pcuHostName

      pcuID = lookupPCUID(pcuHostName)
      if pcuID == 0:
         pcuID = getPLCServer().AddPCU(getPLCAuthentication(), site['site_id'], pcu)
      else:
         if getPLCServer().UpdatePCU(getPLCAuthentication(), pcuID, pcu) != 1:
            pcuID = 0
      if pcuID <= 0:
         error('Unable to add/update PCU ' + pcuHostName)

      return pcuID

   except Exception as e:
      error('Adding PCU ' + pcuHostName + ' to site ' + site['site_long_name'] + ' has failed: ' + str(e))


# ###### Update interfaces of a node ########################################
def updateNorNetInterfaces(node, site, norNetInterface):
   # ====== Current interface settings ======================================
   currentAddressList     = [ ]
   currentInterfaceIDList = [ ]
   interfaceList = getPLCServer().GetInterfaces(getPLCAuthentication(),
                                                { 'node_id' : node['node_id'] })
   for interface in interfaceList:
      interfaceID      = interface['interface_id']
      interfaceTagList = getPLCServer().GetInterfaceTags(getPLCAuthentication(),
                                                         { 'interface_id' : interfaceID })
      if int(getTagValue(interfaceTagList, 'nornet_is_managed_interface', 0)) > 0:
         currentAddressList.append(IPAddress(interface['ip']))
         currentInterfaceIDList.append(interfaceID)


   # ====== Current interface settings ======================================
   newAddressList = [ ]
   providerList         = getNorNetProvidersForSite(site)
   siteIndex            = int(site['site_index'])
   siteDomain           = site['site_domain']
   siteDefProviderIndex = int(site['site_default_provider_index'])
   nodeID               = int(node['node_id'])
   nodeIndex            = int(node['node_index'])
   nodeName             = node['node_name']
   for providerIndex in providerList:
      ifIPv4 = makeNorNetIP(providerIndex, siteIndex, nodeIndex, 4)
      newAddressList.append(IPv4Address(ifIPv4.ip))


   # ====== Update interfaces ===============================================
   if currentAddressList == newAddressList:
      return(0)   # Nothing has changed -> nothing to do!

   try:
      for interface in interfaceList:
         interfaceID      = interface['interface_id']
         interfaceTagList = getPLCServer().DeleteInterface(getPLCAuthentication(), interfaceID)

      primaryInterfaceID = None
      ipv6Primary        = None
      ipv6Gateway        = None
      ipv6Secondaries    = []
      for onlyDefault in [ True, False ]:
         for providerIndex in providerList:

            if ( ((onlyDefault == True)  and (providerIndex == siteDefProviderIndex)) or \
                 ((onlyDefault == False) and (providerIndex != siteDefProviderIndex)) ):
               providerName = getNorNetProviderInfo(providerIndex)[1]

               if providerIndex == siteDefProviderIndex:
                  # Interface of default provider must use the hostname!
                  ifHostName = nodeName.split('.')[0] + '.' + str.lower(siteDomain)
               else:
                  ifHostName = nodeName.split('.')[0] + '.' + str.lower(providerName) + '.' + str.lower(siteDomain)
               ifIPv4        = makeNorNetIP(providerIndex, siteIndex, nodeIndex, 4)
               ifIPv6        = makeNorNetIP(providerIndex, siteIndex, nodeIndex, 6)
               ifGatewayIPv4 = makeNorNetIP(providerIndex, siteIndex, 1, 4)
               ifGatewayIPv6 = makeNorNetIP(providerIndex, siteIndex, 1, 6)
               ifAlias       = providerIndex

               interface = {}
               interface['hostname']      = ifHostName
               interface['ifname']        = norNetInterface
               interface['type']          = 'ipv4'
               interface['method']        = 'static'
               interface['ip']            = str(ifIPv4.ip)
               interface['netmask']       = str(ifIPv4.netmask)
               interface['network']       = str(ifIPv4.network)
               interface['broadcast']     = str(ifIPv4.broadcast)
               interface['gateway']       = str(ifGatewayIPv4.ip)
               if providerIndex == siteDefProviderIndex:
                  interface['is_primary'] = True
                  interface['dns1']       = str(ifGatewayIPv4.ip)   # The tunnelbox is also the DNS server
                  ipv6Primary             = ifIPv6
                  ipv6Gateway             = ifGatewayIPv6.ip
                  interface['dns2']       = str(ifGatewayIPv6.ip)   # The tunnelbox is also the DNS server
               else:
                  interface['is_primary'] = False
                  ipv6Secondaries.append(ifIPv6)
               # print interface

               interfaceID = getPLCServer().AddInterface(getPLCAuthentication(), nodeID, interface)
               if interfaceID <= 0:
                  error('Unable to add interface ' + str(ifIPv4.ip))

               if providerIndex != siteDefProviderIndex:
                  if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, "alias", str(ifAlias)) <= 0:
                     error('Unable to add "alias" tag to interface ' + str(ifIPv4.ip))
               else:
                  primaryInterfaceID = interfaceID
               if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, 'nornet_is_managed_interface', '1') <= 0:
                  error('Unable to add "nornet_is_managed_interface" tag to interface ' + str(ifIPv4.ip))
               if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, 'nornet_ifprovider_index', str(providerIndex)) <= 0:
                  error('Unable to add "nornet_ifprovider_index" tag to interface ' + str(ifIPv4.ip))


      if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, "ipv6addr", str(ipv6Primary)) <= 0:
         error('Unable to add "ipv6addr" tag to interface ' + str(ipv6Primary))
      if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, "ipv6_defaultgw", str(ipv6Gateway)) <= 0:
         error('Unable to add "ipv6_defaultgw" tag to interface ' + str(ipv6Gateway))
            
      secondaries = ""
      for secondaryAddress in ipv6Secondaries:
         if len(secondaries) > 0:
            secondaries = secondaries + ' ' 
         secondaries = secondaries + str(secondaryAddress)
      if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, "ipv6addr_secondaries", secondaries) <= 0:
         error('Unable to add "ipv6addr_secondaries" tag to interface ' + secondaries)

      return(1)

   except Exception as e:
      error('Updating interfaces of node ' + str(nodeID) + ' has failed: ' + str(e))


# ###### Add or update Node tag #############################################
def _addOrUpdateNodeTag(nodeID, tagName, tagValue):
   filter = {
      'tagname' : tagName,
      'node_id' : nodeID
   }
   tags = getPLCServer().GetNodeTags(getPLCAuthentication(), filter, ['node_tag_id'])
   if len(tags) == 0:
      return getPLCServer().AddNodeTag(getPLCAuthentication(), nodeID, tagName, tagValue)
   else:
      return getPLCServer().UpdateNodeTag(getPLCAuthentication(), tags[0]['node_tag_id'], tagValue)


# ###### Create NorNet node #################################################
def makeNorNetNode(site, nodeNiceName, nodeNorNetIndex,
                   pcuID, pcuPort, norNetInterface,
                   model, bootState):
   dnsName      = makeNameFromUnicode(nodeNiceName)
   nodeHostName = dnsName['ascii']   # Domain to be added below!

   # ====== Get site information ============================================
   siteNorNetIndex = int(getTagValue(site['site_tags'], 'nornet_site_index', '-1'))
   if siteNorNetIndex < 0:
      error("Site " + site['site_long_name'] + ' has no NorNet site index!')
   siteNorNetDomain = getTagValue(site['site_tags'], 'nornet_site_domain', '')
   if siteNorNetIndex == '':
      error("Site " + site['site_long_name'] + ' has no NorNet domain name!')

   # ====== Create node =====================================================
   try:
      nodeHostName     = nodeHostName + '.' + str.lower(siteNorNetDomain);
      nodeHostNameUTF8 = dnsName['utf8'] + '.' + str.lower(siteNorNetDomain);
      log('Adding node ' + nodeHostName + ' (' + nodeHostNameUTF8 + ') to site ' + site['site_long_name'] + ' ...')

      node = {}
      node['hostname']   = nodeHostName
      node['model']      = model
      node['boot_state'] = bootState
      nodeID = lookupNodeID(nodeHostName)
      if nodeID == 0:
         node['boot_state'] = 'reinstall'   # New nodes need reinstall ...
         nodeID = getPLCServer().AddNode(getPLCAuthentication(), site['site_id'], node)
      else:
         if getPLCServer().UpdateNode(getPLCAuthentication(), nodeID, node) != 1:
            nodeID = 0
      if nodeID <= 0:
         error('Unable to add/update node ' + nodeHostName)

      if _addOrUpdateNodeTag(nodeID, 'nornet_node_utf8', nodeHostNameUTF8) <= 0:
         error('Unable to add "nornet_node_utf8" tag to node ' + nodeHostName)
      if _addOrUpdateNodeTag(nodeID, 'nornet_is_managed_node', '1') <= 0:
         error('Unable to add "nornet_is_managed_node" tag to node ' + nodeHostName)
      if _addOrUpdateNodeTag(nodeID, 'nornet_node_index', str(nodeNorNetIndex)) <= 0:
         error('Unable to add "nornet_node_index" tag to node ' + nodeHostName)
      if _addOrUpdateNodeTag(nodeID, 'nornet_node_interface', norNetInterface) <= 0:
         error('Unable to add "nornet_node_interface" tag to node ' + nodeHostName)

      # ====== Add node to PCU ==============================================
      if pcuID > 0:
         oldPCUID = lookupPCUIDforNode(nodeID)
         if oldPCUID != 0:
            getPLCServer().DeleteNodeFromPCU(getPLCAuthentication(), nodeID, oldPCUID)
         if getPLCServer().AddNodeToPCU(getPLCAuthentication(), nodeID, pcuID, pcuPort) != 1:
            error('Unable to add node ' + nodeHostName + " to PCU " + str(pcuID) + ", port " + str(pcuPort))

      # ====== Create NorNet interfaces =====================================
      newNode = fetchNorNetNode(nodeHostName)
      if newNode == None:
         error('Unable to find new node ' + nodeHostName)
      updateNorNetInterfaces(newNode, site, norNetInterface)

      return newNode

   except Exception as e:
      error('Adding node ' + nodeHostName + ' has failed: ' + str(e))


# ###### Remove NorNet user #################################################
def removeNorNetUser(userName):
   userID = lookupPersonID(userName)
   if userID != None:
      log('Removing NorNet user ' + userName + ' ...')
      getPLCServer().DeletePerson(getPLCAuthentication(), userID)


# ###### Create NorNet user #################################################
def makeNorNetUser(userName, password, site, title, firstName, lastName, phone, url, publicKey, roles):
   try:
      # ====== Add user =====================================================
      log('Adding user ' + userName + ' ...')
      user = {}
      user['email']      = userName
      user['password']   = password
      user['title']      = title
      user['first_name'] = firstName
      user['last_name']  = lastName
      user['url']        = url
      user['phone']      = phone
      user['url']        = url
      user['enabled']    = True

      userID = lookupPersonID(userName)
      if userID == 0:
         userID = getPLCServer().AddPerson(getPLCAuthentication(), user)
         # NOTE: Directly call UpdatePerson to enable it!
      if getPLCServer().UpdatePerson(getPLCAuthentication(), userID, user) == 1:
         if publicKey != None:
            key = {}
            key['key_type'] = 'ssh'
            key['key']      = publicKey
            getPLCServer().AddPersonKey(getPLCAuthentication(), userID, key)
         for role in roles:
            getPLCServer().AddRoleToPerson(getPLCAuthentication(), role, userID)
         if site != None:
            getPLCServer().AddPersonToSite(getPLCAuthentication(), userID, site['site_id'])
            getPLCServer().SetPersonPrimarySite(getPLCAuthentication(), userID, site['site_id'])
      else:
        userID = 0

      if userID <= 0:
         error('Unable to add/update user ' + userName)

   except Exception as e:
      error('Adding user ' + userName + ' has failed: ' + str(e))

   return fetchNorNetUser(userName)


# ###### Remove NorNet slice ################################################
def removeNorNetSlice(sliceName):
   sliceID = lookupSliceID(sliceName)
   if sliceID != None:
      log('Removing NorNet slice ' + sliceName + ' ...')
      getPLCServer().DeleteSlice(getPLCAuthentication(), sliceID)


# ###### Create NorNet slice ################################################
def makeNorNetSlice(sliceName, sliceDescription, sliceUrl, initscriptCode):
   try:
      # ====== Add slice =====================================================
      log('Adding slice ' + sliceName + ' ...')
      slice = {}
      slice['name']            = sliceName
      slice['description']     = sliceDescription
      slice['url']             = sliceUrl
      slice['initscript_code'] = initscriptCode
      slice['max_nodes']       = 1000000

      sliceID = lookupSliceID(sliceName)
      if sliceID == 0:
         sliceToAdd = slice
         sliceID = getPLCServer().AddSlice(getPLCAuthentication(), slice)

      # UpdateSlice() may only have certain fields. Therefore, initialize
      # "slice" object again, with only the allowed fields included.
      slice = {}
      slice['description']     = sliceDescription
      slice['url']             = sliceUrl
      slice['initscript_code'] = initscriptCode
      
      if getPLCServer().UpdateSlice(getPLCAuthentication(), sliceID, slice) != 1:
        sliceID = 0

      if sliceID <= 0:
         error('Unable to add/update slice ' + sliceName)

   except Exception as e:
      error('Adding slice ' + sliceName + ' has failed: ' + str(e))

   return fetchNorNetSlice(sliceName)


# ###### Add NorNet slice to NorNet nodes  ##################################
def addNorNetSliceToNorNetNodes(slice, nodesList):
   nodeIDs = []
   for node in nodesList:
      nodeIDs.append(int(node['node_id']))
   getPLCServer().AddSliceToNodes(getPLCAuthentication(),
                                  slice['slice_id'], nodeIDs)


# ###### Add users to NorNet slice  #########################################
def addNorNetUsersToNorNetSlice(slice, usersList):
   for user in usersList:
      getPLCServer().AddPersonToSlice(getPLCAuthentication(),
                                      user['user_id'], slice['slice_id'])
