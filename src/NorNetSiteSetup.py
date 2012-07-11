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
   site = fetchNorNetSite(siteName)
   if site != None:
      if int(getTagValue(site['site_tags'], 'nornet_is_managed_site', '-1')) < 1:
         error('removeNorNetSite() will only remove NorNet sites!')
      log('Removing NorNet site ' + siteName + ' ...')
      siteID = site['site_id']
      getPLCServer().DeleteSite(getPLCAuthentication(), siteID)


# ###### Create NorNet site #################################################
def makeNorNetSite(siteName, siteAbbrvName, siteLoginBase, siteUrl, siteNorNetDomain,
                   siteNorNetIndex, siteCity, siteProvince, cityCountry, siteCountryCode,
                   siteLatitude, siteLogitude,
                   providerList, defaultProvider):
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
               if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_default_provider_index', str(providerIndex)) <= 0:
                  error('Unable to add "nornet_site_default_provider_index" tag to site ' + siteName)
               gotDefaultProvider = True

            providerIPv4 = IPv4Address(provider[1])
            providerIPv6 = IPv6Address(provider[2])

            if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_tbp' + str(i) + '_index', str(providerIndex)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_index" tag to site ' + siteName)
            if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_tbp' + str(i) + '_address_ipv4', str(providerIPv4)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_ipv4" tag to site ' + siteName)
            if getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, 'nornet_site_tbp' + str(i) + '_address_ipv6', str(providerIPv6)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_ipv6" tag to site ' + siteName)

         i = i + 1

      if gotDefaultProvider == False:
         error('Site ' + siteName + ' is not connected to default provider ' + defaultProvider)

   except Exception as e:
      error('Adding site ' + siteName + ' has failed: ' + str(e))

   return fetchNorNetSite(siteName)


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

      pcuID = getPLCServer().AddPCU(getPLCAuthentication(), site['site_id'], pcu)
      if pcuID <= 0:
         error('Unable to add PCU ' + pcuHostName)

      return pcuID

   except Exception as e:
      error('Adding PCU ' + pcuHostName + ' to site ' + site['site_long_name'] + ' has failed: ' + str(e))


# ###### Update interfaces of a node ########################################
def updateNorNetInterfaces(node, site, publicDNS):
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
   nodeAddress          = int(node['node_address'])
   nodeName             = node['node_name']
   for providerIndex in providerList:
      ifIPv4 = makeNorNetIP(providerIndex, siteIndex, nodeAddress, 4)
      newAddressList.append(IPv4Address(ifIPv4.ip))


   # ====== Update interfaces ===============================================
   if currentAddressList == newAddressList:
      return(0)   # Nothing has changed -> nothing to do!

   try:
      for interface in interfaceList:
         interfaceID      = interface['interface_id']
         interfaceTagList = getPLCServer().DeleteInterface(getPLCAuthentication(), interfaceID)

      for providerIndex in providerList:
         providerName = getNorNetProviderInfo(providerIndex)[1]

         ifHostName        = nodeName.split('.')[0] + '-' + str.lower(providerName) + '.' + str.lower(siteDomain)
         ifIPv4            = makeNorNetIP(providerIndex, siteIndex, nodeAddress, 4)
         ifGateway         = makeNorNetIP(providerIndex, siteIndex, 1, 4)
         ifProviderNetwork = makeNorNetIP(providerIndex, 0, 0, 4)
         ifAlias           = providerIndex

         interface = {}
         interface['hostname']   = ifHostName
         if providerIndex == siteDefProviderIndex:
            interface['is_primary'] = True
            interface['dns1']       = str(publicDNS[0])
            if len(publicDNS) > 1:
               interface['dns2']    = str(publicDNS[1])
         else:
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
            error('Unable to add interface ' + str(ifIPv4.ip))

         if providerIndex != siteDefProviderIndex:
            if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, "alias", str(ifAlias)) <= 0:
               error('Unable to add "alias" tag to interface ' + str(ifIPv4.ip))
         if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, 'nornet_is_managed_interface', '1') <= 0:
            error('Unable to add "nornet_is_managed_interface" tag to interface ' + str(ifIPv4.ip))
         if getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, 'nornet_ifprovider_index', str(providerIndex)) <= 0:
            error('Unable to add "nornet_ifprovider_index" tag to interface ' + str(ifIPv4.ip))

      return(1)

   except Exception as e:
      error('Updating interfaces of node ' + str(nodeID) + ' has failed: ' + str(e))


# ###### Create NorNet node #################################################
def makeNorNetNode(site, nodeNiceName, nodeNorNetIndex, addressBase,
                   pcuID, pcuPort, publicDNS):
      nodeHostName = nodeNiceName   # Domain to be added below!

      # ====== Get site information ============================================
      siteNorNetIndex = int(getTagValue(site['site_tags'], 'nornet_site_index', '-1'))
      if siteNorNetIndex < 0:
         error("Site " + site['site_long_name'] + ' has no NorNet site index!')
      siteNorNetDomain = getTagValue(site['site_tags'], 'nornet_site_domain', '')
      if siteNorNetIndex == '':
         error("Site " + site['site_long_name'] + ' has no NorNet domain name!')

   # ====== Create node =====================================================
   #try:
      nodeHostName = nodeHostName + '.' + str.lower(siteNorNetDomain);
      log('Adding node ' + nodeHostName + ' to site ' + site['site_long_name'] + ' ...')

      node = {}
      node['hostname']   = nodeHostName
      node['boot_state'] = 'reinstall'
      node['model']      = 'Amiga 5000'
      nodeID = getPLCServer().AddNode(getPLCAuthentication(), site['site_id'], node)
      if nodeID <= 0:
         error('Unable to add node ' + nodeHostName)

      if getPLCServer().AddNodeTag(getPLCAuthentication(), nodeID, 'nornet_is_managed_node', '1') <= 0:
         error('Unable to add "nornet_is_managed_node" tag to node ' + nodeHostName)
      if getPLCServer().AddNodeTag(getPLCAuthentication(), nodeID, 'nornet_node_index', str(nodeNorNetIndex)) <= 0:
         error('Unable to add "nornet_node_index" tag to node ' + nodeHostName)
      if getPLCServer().AddNodeTag(getPLCAuthentication(), nodeID, 'nornet_node_address', str(nodeNorNetIndex + addressBase)) <= 0:
         error('Unable to add "nornet_node_address" tag to node ' + nodeHostName)

      # ====== Add node to PCU ==============================================
      if pcuID > 0:
         if getPLCServer().AddNodeToPCU(getPLCAuthentication(), nodeID, pcuID, pcuPort) != 1:
            error('Unable to add node ' + nodeHostName + " to PCU " + str(pcuID) + ", port " + str(pcuPort))

      # ====== Create NorNet interfaces =====================================
      newNode = fetchNorNetNode(nodeHostName)
      if newNode == None:
         error('Unable to find new node ' + nodeHostName)
      updateNorNetInterfaces(newNode, site, publicDNS)

      return newNode

   #except Exception as e:
      #error('Adding node ' + nodeHostName + ' has failed: ' + str(e))
