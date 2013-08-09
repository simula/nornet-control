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

   makeTagType('slice/nornet',     'NorNet Managed Slice',            'nornet_is_managed_slice')
   makeTagType('slice/nornet',     'NorNet Slice Node Index',         'nornet_slice_node_index')
   makeTagType('slice/nornet',     'NorNet Slice Own Addresses',      'nornet_slice_own_addresses')

   # ====== Missing tags for plnet ==========================================
   makeTagType('interface/config', 'IPv6 Auto-Configuration',          'ipv6_autoconf')
   for i in range(1,10):
      makeTagType('interface/config', 'IPv4 Secondary IPv4 Address',   'ipaddr'  + str(i))
      makeTagType('interface/config', 'IPv4 Secondary IPv4 Netmask',   'netmask' + str(i))

   # ====== Special tags for ovs_bridge handling ============================
   makeTagType('interface/ovs', 'Name of Open vSwitch bridge', 'ovs_bridge')
   getPLCServer().AddRoleToTagType(getPLCAuthentication(), 'admin', 'ovs_bridge')
   getPLCServer().AddRoleToTagType(getPLCAuthentication(), 'tech',  'ovs_bridge')

   makeTagType('slice/network', 'Placeholder for interface information while we wait for VirtualInterface objects in PLCAPI', 'interface')
   getPLCServer().AddRoleToTagType(getPLCAuthentication(), 'admin', 'interface')
 

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
                   ntpServers):
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
      ipv4SecondaryIndex = 1
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

               if providerIndex == siteDefProviderIndex:
                  interface = {}
                  interface['hostname']   = ifHostName
                  interface['ifname']     = norNetInterface
                  interface['type']       = 'ipv4'
                  interface['method']     = 'static'
                  interface['ip']         = str(ifIPv4.ip)
                  interface['netmask']    = str(ifIPv4.netmask)
                  interface['network']    = str(ifIPv4.network)
                  interface['broadcast']  = str(ifIPv4.broadcast)
                  interface['gateway']    = str(ifGatewayIPv4.ip)
                  interface['is_primary'] = True
                  interface['dns1']       = str(ifGatewayIPv4.ip)   # The tunnelbox is also the DNS server
                  ipv6Primary             = ifIPv6
                  ipv6Gateway             = ifGatewayIPv6.ip
                  interface['dns2']       = str(ifGatewayIPv6.ip)   # The tunnelbox is also the DNS server

                  primaryInterfaceID = getPLCServer().AddInterface(getPLCAuthentication(), nodeID, interface)
                  if primaryInterfaceID <= 0:
                     error('Unable to add interface ' + str(ifIPv4.ip))

                  if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, "ovs_bridge", 'public0') <= 0:
                     error('Unable to add "ovs_bridge" tag to interface ' + str(ifIPv4.ip))
                  if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, 'nornet_is_managed_interface', '1') <= 0:
                     error('Unable to add "nornet_is_managed_interface" tag to interface ' + str(ifIPv4.ip))
                  if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, 'nornet_ifprovider_index', str(providerIndex)) <= 0:
                     error('Unable to add "nornet_ifprovider_index" tag to interface ' + str(ifIPv4.ip))
                  
               else:
                  ipv6Secondaries.append(ifIPv6)

                  if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, 'ipaddr' + str(ipv4SecondaryIndex), str(ifIPv4.ip)) <= 0:
                     error('Unable to add "ipaddr' + str(ipv4SecondaryIndex) + '" tag to interface ' + str(ifIPv4.ip))
                  if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, 'netmask' + str(ipv4SecondaryIndex), str(ifIPv4.netmask)) <= 0:
                     error('Unable to add "netmask' + str(ipv4SecondaryIndex) + '" tag to interface ' + str(ifIPv4.ip))


      if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, 'ipv6addr', str(ipv6Primary)) <= 0:
         error('Unable to add "ipv6addr" tag to interface ' + str(ipv6Primary))
      if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, 'ipv6_autoconf', 'no') <= 0:
         error('Unable to add "ipv6_autoconf" tag to interface ' + str(ipv6Primary))
      if getPLCServer().AddInterfaceTag(getPLCAuthentication(), primaryInterfaceID, 'ipv6_defaultgw', str(ipv6Gateway)) <= 0:
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


# ###### Add or update node tag #############################################
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


# ###### Add or update configuration file ###################################
def _addOrUpdateConfFile(configuration):
   filter = {
      'dest' : configuration['dest']
   }
   confFiles = getPLCServer().GetConfFiles(getPLCAuthentication(), filter, [ 'conf_file_id' ])
   if len(confFiles) == 0:
      return getPLCServer().AddConfFile(getPLCAuthentication(), configuration)
   else:
      if getPLCServer().UpdateConfFile(getPLCAuthentication(), confFiles[0]['conf_file_id'], configuration) == 1:
         return confFiles[0]['conf_file_id']
      return 0


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

      # ====== Hack to handle openvswitch start/stop correctly ==============
      # See https://docs.google.com/a/simula.no/document/d/1WRZ7kN6KwZRaeNOi51-uNmintCVwdkzhM2W3To6uV_Y/edit?pli=1 .
      confFileID = _addOrUpdateConfFile({
         'file_owner': u'root',
         'postinstall_cmd': u'/bin/systemctl reenable openvswitch.service',
         'error_cmd': u'', 'preinstall_cmd': u'',
         'dest': u'/lib/systemd/system/openvswitch.service',
         'ignore_cmd_errors': False,
         'enabled': True,
         'file_permissions': u'644',
         'source': u'PlanetLabConf/openvswitch/openvswitch.service',
         'always_update': False,
         'file_group': u'root'})
      if getPLCServer().AddConfFileToNode(getPLCAuthentication(), confFileID, nodeID) != 1:
         error('Unable to add openvswitch.service configuration file to node ' + nodeHostName)

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


# ###### Add or update slice tag ############################################
def _addOrUpdateSliceTag(sliceID, node, tagName, tagValue):
   if node != None:   
      nodeID = node['node_id']
      filter = {
         'tagname'  : tagName,
         'node_id'  : nodeID,
         'slice_id' : sliceID
      }
   else:
      nodeID = None
      filter = {
         'tagname'  : tagName,
         'slice_id' : sliceID
      }
    
   tags = getPLCServer().GetSliceTags(getPLCAuthentication(), filter, ['slice_tag_id','node_id'])
   if len(tags) == 0:
      return getPLCServer().AddSliceTag(getPLCAuthentication(), sliceID, tagName, tagValue, nodeID)
   else:
      return getPLCServer().UpdateSliceTag(getPLCAuthentication(), tags[0]['slice_tag_id'], tagValue)


# ###### Create NorNet slice ################################################
def makeNorNetSlice(sliceName, ownAddress, sliceDescription, sliceUrl, initscriptCode):
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

      if _addOrUpdateSliceTag(sliceID, None, 'nornet_is_managed_slice', '1') <= 0:
         error('Unable to add "nornet_is_managed_slice" tag to slice ' + sliceName)
      if ownAddress == True:
         allocateOwnAddress = 1
      else:
         allocateOwnAddress = 0
      if _addOrUpdateSliceTag(sliceID, None, 'nornet_slice_own_addresses', str(allocateOwnAddress)) <= 0:
         error('Unable to add "nornet_slice_own_addresses" tag to slice ' + sliceName)

   except Exception as e:
      error('Adding slice ' + sliceName + ' has failed: ' + str(e))

   return fetchNorNetSlice(sliceName)


# ###### Get slice node index of NorNet slice ###############################
def getSliceNodeIndexOfNorNetSlice(slice, node):
   for tag in slice['slice_tags']:
      if ((tag['node_id'] == node['node_id']) and
          (tag['tagname'] == 'nornet_slice_node_index')):
         return(int(tag['value']))
   return 0


# ###### Find a slice node index for a new slice ############################
def _findPossibleSliceNodeIndex(fullNodeList, fullSliceList, thisSlice, thisNode):
   possibleSliceNodeIndexes = NorNet_Configuration['NorNet_Slice_NodeIndexRange']

   for slice in fullSliceList:
      for node in fullNodeList:
         if ((slice['slice_id'] == thisSlice['slice_id']) and
             (node['node_id'] == thisNode['node_id'])):
            # Ignore current slice's allocation on current node
            continue

         if node['node_id'] in slice['slice_node_ids']:
            sliceNodeIndex = getSliceNodeIndexOfNorNetSlice(slice, node)
            if sliceNodeIndex > 0:
               try:
                  possibleSliceNodeIndexes.remove(sliceNodeIndex)
               except:
                  pass

   if len(possibleSliceNodeIndexes) > 0:
      i = 0   # int(round(random.uniform(0, len(possibleSliceNodeIndexes)-1)))
      return possibleSliceNodeIndexes[i]

   return 0


# ###### Add NorNet slice to NorNet nodes  ##################################
def addNorNetSliceToNorNetNodes(fullSiteList, fullNodeList, fullSliceList, slice, nodesList):
   nodeIDs = []
   for node in nodesList:
      nodeIndex = node['node_index']
      
      # ====== Add slice to node ============================================
      getPLCServer().AddSliceToNodes(getPLCAuthentication(),
                                     slice['slice_id'], [ node['node_id'] ])

      # ====== Give slice its own addresses, if requested ===================
      sliceOwnAddresses = slice['slice_own_addresses']
      if sliceOwnAddresses != 0:
         # ====== Get slice node index ======================================
         sliceNodeIndex = _findPossibleSliceNodeIndex(fullNodeList, fullSliceList, slice, node)
         if sliceNodeIndex == 0:
            error('No possible slice node index available!')
       
         # ====== Create configuration ======================================
         site = getNorNetSiteOfNode(fullSiteList, node)
         if site == None:
            error('Site not found?!')
         siteIndex = site['site_index']

         bridgeInterfaceConfig = {}
         bridgeInterfaceConfig['bridge']        = 'public0'
         bridgeInterfaceConfig['BOOTPROTO']     = 'static'
         bridgeInterfaceConfig['DEVICE']        = 'eth0'
         bridgeInterfaceConfig['ONBOOT']        = 'yes'
         bridgeInterfaceConfig['PRIMARY']       = 'yes'
         bridgeInterfaceConfig['IPV6INIT']      = 'yes'
         bridgeInterfaceConfig['IPV6_AUTOCONF'] = 'no'

         addresses       = 0
         secondariesIPv6 = []
         providerList = getNorNetProvidersForSite(site)
         for onlyDefault in [ True, False ]:
            for providerIndex in providerList:
               if ( ((onlyDefault == True)  and (providerIndex == site['site_default_provider_index'])) or \
                    ((onlyDefault == False) and (providerIndex != site['site_default_provider_index'])) ):

                  # For IPv4, we only have the slice node index.
                  ifIPv4 = makeNorNetIP(providerIndex, siteIndex, sliceNodeIndex, 4)
                  # For IPv6, we have enough space to encode node index and slice node index!
                  ifIPv6 = makeNorNetIP(providerIndex, siteIndex, nodeIndex, 6, sliceNodeIndex)

                  if addresses == 0:
                     bridgeInterfaceConfig['IPADDR'] = str(ifIPv4.ip)
                     bridgeInterfaceConfig['NETMASK'] = str(ifIPv4.netmask)
                  else:
                     bridgeInterfaceConfig['IPADDR'  + str(addresses)] = str(ifIPv4.ip)
                     bridgeInterfaceConfig['NETMASK' + str(addresses)] = str(ifIPv4.netmask)

                  if addresses == 0:
                     ifGatewayIPv4 = makeNorNetIP(providerIndex, siteIndex, NorNet_NodeIndex_Tunnelbox, 4)
                     bridgeInterfaceConfig['GATEWAY'] = str(ifGatewayIPv4.ip)
                     bridgeInterfaceConfig['DNS1']    = str(ifGatewayIPv4.ip)

                     ifGatewayIPv6 = makeNorNetIP(providerIndex, siteIndex, NorNet_NodeIndex_Tunnelbox, 6)
                     bridgeInterfaceConfig['IPV6ADDR']       = str(ifIPv6)
                     bridgeInterfaceConfig['IPV6_DEFAULTGW'] = str(ifGatewayIPv6.ip)
                     bridgeInterfaceConfig['DNS2']           = str(ifGatewayIPv6.ip)
                  else:
                     secondariesIPv6.append(ifIPv6)

                  addresses = addresses + 1
                  
         if addresses > 1:
            secondaries = ''
            for secondaryIPv6 in secondariesIPv6:
               if len(secondaries) > 0:
                  secondaries = secondaries + ' '
               secondaries = secondaries + str(secondaryIPv6)
            bridgeInterfaceConfig['IPV6ADDR_SECONDARIES'] = secondaries
            
         # print bridgeInterfaceConfig
         if _addOrUpdateSliceTag(slice['slice_id'], node, 'nornet_slice_node_index', str(sliceNodeIndex)) <= 0:
            error('Unable to add "nornet_slice_node_index" tag to slice ' + sliceName)
         if _addOrUpdateSliceTag(slice['slice_id'], node, 'interface', str(bridgeInterfaceConfig)) <= 0:
            error('Unable to add "interface" tag to slice ' + sliceName)


# ###### Add users to NorNet slice  #########################################
def addNorNetUsersToNorNetSlice(slice, usersList):
   for user in usersList:
      getPLCServer().AddPersonToSlice(getPLCAuthentication(),
                                      user['user_id'], slice['slice_id'])
