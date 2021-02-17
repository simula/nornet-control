#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NorNet Site Setup
# Copyright (C) 2012-2021 by Thomas Dreibholz
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


import sys
import re
import os
import hashlib
import datetime
import time

from ipaddress import ip_interface, IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

# NorNet
from NorNetTools         import *
from NorNetAPI           import *
from NorNetProviderSetup import *



# ###### Create tag type ####################################################
def makeTagType(category, description, tagName, roles = []):
   found = getPLCServer().GetTagTypes(getPLCAuthentication(), tagName, ['tag_type_id'])
   if len(found) == 0:
      tagType = {}
      tagType['category']    = category
      tagType['description'] = description
      tagType['tagname']     = tagName
      getPLCServer().AddTagType(getPLCAuthentication(), tagType)
   for role in roles:
      getPLCServer().AddRoleToTagType(getPLCAuthentication(), role, tagName)


# ###### Create NorNet tag types ############################################
def makeNorNetTagTypes():
   # ====== Create tags =====================================================
   makeTagType('site/nornet', 'NorNet Managed Site',                      'nornet_is_managed_site',   [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site Index',                        'nornet_site_index',        [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site Domain Name',                  'nornet_site_domain',       [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site UTF-8',                        'nornet_site_utf8',         [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site City',                         'nornet_site_city',         [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site Province',                     'nornet_site_province',     [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site Country',                      'nornet_site_country',      [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site Country Code',                 'nornet_site_country_code', [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site Altitude',                     'nornet_site_altitude',     [ 'admin', 'pi' ])
   makeTagType('site/nornet', 'NorNet Site Default Provider Index',       'nornet_site_default_provider_index', [ 'admin' ])
   makeTagType('site/nornet', 'NorNet Site Tunnelbox Internal Interface', 'nornet_site_tb_internal_interface',  [ 'admin' ])
   for i in range(0, NorNet_MaxNTPServers):
      makeTagType('site/nornet', 'NorNet Site NTP Server ' + str(i),      'nornet_site_ntp' + str(i),     [ 'admin', 'tech' ])
   for i in range(0, NorNet_MaxSiteContacts):
      makeTagType('site/nornet', 'NorNet Site Contact ' + str(i),         'nornet_site_contact' + str(i), [ 'admin', 'pi' ])

   for i in range(0, NorNet_MaxProviders):
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Index',        'nornet_site_tbp' + str(i) + '_index',        [ 'admin' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Interface',    'nornet_site_tbp' + str(i) + '_interface',    [ 'admin' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Address IPv4', 'nornet_site_tbp' + str(i) + '_address_ipv4', [ 'admin' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Address IPv6', 'nornet_site_tbp' + str(i) + '_address_ipv6', [ 'admin' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Gateway IPv4', 'nornet_site_tbp' + str(i) + '_gateway_ipv4', [ 'admin' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Gateway IPv6', 'nornet_site_tbp' + str(i) + '_gateway_ipv6', [ 'admin' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' MTU',          'nornet_site_tbp' + str(i) + '_mtu',          [ 'admin', 'tech' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Type',         'nornet_site_tbp' + str(i) + '_type',         [ 'admin', 'tech' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Downstream',   'nornet_site_tbp' + str(i) + '_downstream',   [ 'admin', 'tech' ])
      makeTagType('site/nornet', 'NorNet Site Tunnelbox Provider-' + str(i) + ' Upstream',     'nornet_site_tbp' + str(i) + '_upstream',     [ 'admin', 'tech' ])

   makeTagType('node/nornet',      'NorNet Managed Node',                  'nornet_is_managed_node',       [ 'admin' ])
   makeTagType('node/nornet',      'NorNet Node UTF-8',                    'nornet_node_utf8',             [ 'admin' ])
   makeTagType('node/nornet',      'NorNet Node Index',                    'nornet_node_index',            [ 'admin' ])
   makeTagType('node/nornet',      'NorNet Node Interface',                'nornet_node_interface',        [ 'admin' ])
   makeTagType('node/nornet',      'NorNet Node Machine Host',             'nornet_node_machine_host',     [ 'admin', 'tech' ])
   makeTagType('node/nornet',      'NorNet Node Machine Display',          'nornet_node_machine_display',  [ 'admin', 'tech' ])

   makeTagType('interface/nornet', 'NorNet Managed Interface',             'nornet_is_managed_interface',  [ 'admin' ])
   makeTagType('interface/nornet', 'NorNet Interface Provider Index',      'nornet_ifprovider_index',      [ 'admin' ])

   makeTagType('slice/nornet',     'NorNet Managed Slice',                 'nornet_is_managed_slice',      [ 'admin' ])
   makeTagType('slice/nornet',     'NorNet Slice Node Index',              'nornet_slice_node_index',      [ 'admin' ])
   makeTagType('slice/nornet',     'NorNet Slice Own Addresses',           'nornet_slice_own_addresses',   [ 'admin' ])

   # SysCtls
   nornetSysCtls = [
      'net.ipv4.tcp_ecn',
      'net.ipv4.tcp_rmem',
      'net.ipv4.tcp_wmem',
      'net.ipv4.tcp_congestion_control',
      'net.sctp.sctp_rmem',
      'net.sctp.sctp_wmem'
   ]
   for nornetSysCtl in nornetSysCtls:
      makeTagType('slice/sysctl', 'SysCtl ' + nornetSysCtl, 'vsys_sysctl.' + nornetSysCtl, [ 'admin' ])

   # ====== Missing tags for plnet ==========================================
   makeTagType('interface/config', 'IPv6 Auto-Configuration',          'ipv6_autoconf')
   for i in range(0, NorNet_MaxProviders):
      makeTagType('interface/config', 'IPv4 Secondary IPv4 Address',   'ipaddr'  + str(i + 1), [ 'admin' ])
      makeTagType('interface/config', 'IPv4 Secondary IPv4 Netmask',   'netmask' + str(i + 1), [ 'admin' ])

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

      plcSiteNTPConfName = '/var/www/html/PlanetLabConf/ntp/ntp.conf.' + site['site_domain']
      try:
         os.remove(plcSiteNTPConfName)
      except:
         pass

      for shell in [ 'sh', 'csh' ]:
         proxyConfName = '/var/www/html/PlanetLabConf/proxy/proxy.' + shell + '.' + site['site_domain']
         try:
            os.remove(proxyConfName)
         except:
            pass

   else:
      log('Site not found: ' + siteName)


# ###### Add or update site tag #############################################
def addOrUpdateSiteTag(siteID, tagName, tagValue):
   filter = {
      'tagname' : tagName,
      'site_id' : siteID
   }
   tags = getPLCServer().GetSiteTags(getPLCAuthentication(), filter, ['site_tag_id'])
   if len(tags) == 0:
      return getPLCServer().AddSiteTag(getPLCAuthentication(), siteID, tagName, tagValue)
   else:
      return getPLCServer().UpdateSiteTag(getPLCAuthentication(), tags[0]['site_tag_id'], tagValue)


# ###### Delete site tag ####################################################
def _deleteSiteTag(siteID, tagName):
   filter = {
      'tagname' : tagName,
      'site_id' : siteID
   }
   tags = getPLCServer().GetSiteTags(getPLCAuthentication(), filter, ['site_tag_id'])
   if len(tags) != 0:
      return getPLCServer().DeleteSiteTag(getPLCAuthentication(), tags[0]['site_tag_id'])


# ###### Create NorNet site #################################################
def makeNorNetSite(siteName, siteAbbrvName, siteEnabled, siteLoginBase, siteUrl, siteNorNetDomain,
                   siteNorNetIndex, siteCity, siteProvince, cityCountry, siteCountryCode,
                   siteLatitude, siteLogitude, siteAltitude, siteContacts,
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
      if addOrUpdateSiteTag(siteID, 'nornet_is_managed_site', '1') <= 0:
         error('Unable to add "nornet_is_managed_site" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_index', str(siteNorNetIndex)) <= 0:
         error('Unable to add "nornet_site_index" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_utf8', siteLabel['utf8']) <= 0:
         error('Unable to add "nornet_site_utf8" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_city', siteCity) <= 0:
         error('Unable to add "nornet_site_city" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_domain', siteNorNetDomain) <= 0:
         error('Unable to add "nornet_site_domain" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_province', siteProvince) <= 0:
         error('Unable to add "nornet_site_province" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_country', cityCountry) <= 0:
         error('Unable to add "nornet_site_country" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_country_code', siteCountryCode) <= 0:
         error('Unable to add "nornet_site_country_code" tag to site ' + siteName)
      if addOrUpdateSiteTag(siteID, 'nornet_site_altitude', str(siteAltitude)) <= 0:
         error('Unable to add "nornet_site_altitude" tag to site ' + siteName)

      # ====== Set providers ================================================
      gotDefaultProvider   = False
      defaultProviderIndex = None
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
               error("Unknown provider " + providerName)
            if providerName == defaultProvider:
               defaultProviderIndex = providerIndex
               if addOrUpdateSiteTag(siteID, 'nornet_site_default_provider_index', str(providerIndex)) <= 0:
                  error('Unable to add "nornet_site_default_provider_index" tag to site ' + siteName)
               gotDefaultProvider = True

            providerInterface   = str(provider[1])
            providerAddressIPv4 = IPv4Interface(provider[2])
            providerGatewayIPv4 = IPv4Address(provider[3])
            providerAddressIPv6 = IPv6Interface(provider[4])
            providerGatewayIPv6 = IPv6Address(provider[5])
            providerMTU        = 576
            providerType       = ''
            providerUpstream   = 0
            providerDownstream = 0
            try:
               providerMTU        = int(provider[6])
               providerType       = provider[7]
               providerUpstream   = int(provider[8])
               providerDownstream = int(provider[9])
            except:
               error('Incomplete provider metadata: ' + str(provider))
               
            if ((providerMTU < 1280) or (providerMTU > 9000)):
               error('Bad MTU for provider: ' + str(provider))

            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_index', str(providerIndex)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_index" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_interface', providerInterface) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_interface" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_address_ipv4', str(providerAddressIPv4)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_address_ipv4" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_address_ipv6', str(providerAddressIPv6)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_address_ipv6" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_gateway_ipv4', str(providerGatewayIPv4)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_gateway_ipv4" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_gateway_ipv6', str(providerGatewayIPv6)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_gateway_ipv6" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_mtu', str(providerMTU)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_mtu" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_type', str(providerType)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_type" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_downstream', str(providerDownstream)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_downstream" tag to site ' + siteName)
            if addOrUpdateSiteTag(siteID, 'nornet_site_tbp' + str(i) + '_upstream', str(providerUpstream)) <= 0:
               error('Unable to add "nornet_site_tbp' + str(i) + '_upstream" tag to site ' + siteName)

         i = i + 1

      # Remove previously-used (but now deleted) providers:
      while i < NorNet_MaxProviders:
         for suffix in [ '_index', '_interface',  '_address_ipv4', '_address_ipv6', '_gateway_ipv4', '_gateway_ipv6' ]:
            _deleteSiteTag(siteID, 'nornet_site_tbp' + str(i) + suffix)
         i = i + 1

      if gotDefaultProvider == False:
         error('Site ' + siteName + ' is not connected to default provider ' + defaultProvider)

      # ====== Set contacts =================================================
      i = 0
      for contact in siteContacts:
         if i >= NorNet_MaxSiteContacts:
            break
         if addOrUpdateSiteTag(siteID, 'nornet_site_contact' + str(i), contact) <= 0:
            error('Unable to add "nornet_site_contact' + str(i) + '" tag to site ' + siteName)
         i = i + 1

      # Remove previously-used (but now deleted) contacts:
      while i < NorNet_MaxSiteContacts:
         _deleteSiteTag(siteID, 'nornet_site_contact' + str(i))
         i = i + 1

      # ====== Set NTP servers ==============================================
      for i in range(0, NorNet_MaxNTPServers):
         if i >= len(ntpServers):
            break
         if addOrUpdateSiteTag(siteID, 'nornet_site_ntp' + str(i), str(ip_interface(ntpServers[i]).ip)) <= 0:
            error('Unable to add "nornet_site_ntp' + str(i) + '" tag to site ' + siteName)

      # Write a PlanetLabConf file to set the NTP server of nodes at the site
      plcSiteNTPConfName = '/var/www/html/PlanetLabConf/ntp/ntp.conf.' + siteNorNetDomain
      try:
         plcSiteNTPConf = codecs.open(plcSiteNTPConfName, 'w', 'utf-8')
         for version in [ 6 ]:
            ntpAddress = makeNorNetIP(defaultProviderIndex, siteNorNetIndex, NorNet_NodeIndex_Tunnelbox, version)
            plcSiteNTPConf.write('server ' + str(ntpAddress.ip) + "\n")
         plcSiteNTPConf.close()
      except:
         print(('WARNING: Unable to write ' + plcSiteNTPConfName))

      # ====== Set internal interface =======================================
      if addOrUpdateSiteTag(siteID, 'nornet_site_tb_internal_interface', tbInternalInterface) <= 0:
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


# ###### Add or update interface tag ########################################
def addOrUpdateInterfaceTag(interfaceID, tagName, tagValue):
   filter = {
      'tagname'      : tagName,
      'interface_id' : interfaceID
   }
   tags = getPLCServer().GetInterfaceTags(getPLCAuthentication(), filter, ['interface_tag_id'])
   if len(tags) == 0:
      return getPLCServer().AddInterfaceTag(getPLCAuthentication(), interfaceID, tagName, tagValue)
   else:
      return getPLCServer().UpdateInterfaceTag(getPLCAuthentication(), tags[0]['interface_tag_id'], tagValue)


# ###### Delete interface tag ####################################################
def _deleteInterfaceTag(interfaceID, tagName):
   filter = {
      'tagname'      : tagName,
      'interface_id' : interfaceID
   }
   tags = getPLCServer().GetInterfaceTags(getPLCAuthentication(), filter, ['interface_tag_id'])
   if len(tags) != 0:
      return getPLCServer().DeleteInterfaceTag(getPLCAuthentication(), tags[0]['interface_tag_id'])


# ###### Update interfaces of a node ########################################
def _updateNorNetInterfaces(node, site, norNetInterface):
   providerList         = getNorNetProvidersForSite(site)
   siteIndex            = int(site['site_index'])
   siteDomain           = site['site_domain']
   siteDefProviderIndex = int(site['site_default_provider_index'])
   nodeID               = int(node['node_id'])
   nodeIndex            = int(node['node_index'])
   nodeName             = node['node_name']

   try:
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
                  interface['network']    = str(ifIPv4.network.network_address)
                  interface['netmask']    = str(ifIPv4.netmask)
                  interface['broadcast']  = str(ifIPv4.network.broadcast_address)
                  interface['gateway']    = str(ifGatewayIPv4.ip)
                  interface['is_primary'] = True
                  interface['dns1']       = str(ifGatewayIPv4.ip)   # The tunnelbox is also the DNS server
                  ipv6Primary             = ifIPv6
                  ipv6Gateway             = ifGatewayIPv6.ip
                  interface['dns2']       = str(ifGatewayIPv6.ip)   # The tunnelbox is also the DNS server

                  primaryInterfaceID = lookupPrimaryInterfaceID(node)
                  if primaryInterfaceID == 0:
                     primaryInterfaceID = getPLCServer().AddInterface(getPLCAuthentication(), nodeID, interface)
                  else:
                     if getPLCServer().UpdateInterface(getPLCAuthentication(), primaryInterfaceID, interface) != 1:
                        primaryInterfaceID = 0
                  if primaryInterfaceID <= 0:
                     error('Unable to add/update interface ' + norNetInterface)

                  if addOrUpdateInterfaceTag(primaryInterfaceID, "ovs_bridge", 'public0') <= 0:
                     error('Unable to add "ovs_bridge" tag to interface ' + str(ifIPv4.ip))
                  if addOrUpdateInterfaceTag(primaryInterfaceID, 'nornet_is_managed_interface', '1') <= 0:
                     error('Unable to add "nornet_is_managed_interface" tag to interface ' + str(ifIPv4.ip))
                  if addOrUpdateInterfaceTag(primaryInterfaceID, 'nornet_ifprovider_index', str(providerIndex)) <= 0:
                     error('Unable to add "nornet_ifprovider_index" tag to interface ' + str(ifIPv4.ip))

               else:
                  ipv6Secondaries.append(ifIPv6)
                  if addOrUpdateInterfaceTag(primaryInterfaceID, 'ipaddr' + str(ipv4SecondaryIndex), str(ifIPv4.ip)) <= 0:
                     error('Unable to add "ipaddr' + str(ipv4SecondaryIndex) + '" tag to interface ' + str(ifIPv4.ip))
                  if addOrUpdateInterfaceTag(primaryInterfaceID, 'netmask' + str(ipv4SecondaryIndex), str(ifIPv4.netmask)) <= 0:
                     error('Unable to add "netmask' + str(ipv4SecondaryIndex) + '" tag to interface ' + str(ifIPv4.ip))
                  ipv4SecondaryIndex = ipv4SecondaryIndex + 1


      # Remove deleted ISPs
      while ipv4SecondaryIndex < NorNet_MaxProviders:
         for prefix in [ 'ipaddr', 'netmask' ]:
            _deleteInterfaceTag(primaryInterfaceID, prefix + str(ipv4SecondaryIndex))
         ipv4SecondaryIndex = ipv4SecondaryIndex + 1

      # Add IPv6 configuration
      if addOrUpdateInterfaceTag(primaryInterfaceID, 'ipv6addr', str(ipv6Primary)) <= 0:
         error('Unable to add "ipv6addr" tag to interface ' + str(ipv6Primary))
      if addOrUpdateInterfaceTag(primaryInterfaceID, 'ipv6_autoconf', 'no') <= 0:
         error('Unable to add "ipv6_autoconf" tag to interface ' + str(ipv6Primary))
      if addOrUpdateInterfaceTag(primaryInterfaceID, 'ipv6_defaultgw', str(ipv6Gateway)) <= 0:
         error('Unable to add "ipv6_defaultgw" tag to interface ' + str(ipv6Gateway))
      secondaries = ""
      for secondaryAddress in ipv6Secondaries:
         if len(secondaries) > 0:
            secondaries = secondaries + ' '
         secondaries = secondaries + str(secondaryAddress)
      if addOrUpdateInterfaceTag(primaryInterfaceID, "ipv6addr_secondaries", secondaries) <= 0:
         error('Unable to add "ipv6addr_secondaries" tag to interface ' + secondaries)

      return(1)

   except Exception as e:
      error('Updating interfaces of node ' + str(nodeID) + ' has failed: ' + str(e))


# ###### Add or update node tag #############################################
def addOrUpdateNodeTag(nodeID, tagName, tagValue):
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
def addOrUpdateConfFile(configuration):
   filter = {
      # Selection must be based on source, because there may be node-specific
      # sources for the same destination file!
      'source' : configuration['source']
   }
   confFiles = getPLCServer().GetConfFiles(getPLCAuthentication(), filter, [ 'conf_file_id' ])
   if len(confFiles) == 0:
      return getPLCServer().AddConfFile(getPLCAuthentication(), configuration)
   else:
      if getPLCServer().UpdateConfFile(getPLCAuthentication(), confFiles[0]['conf_file_id'], configuration) == 1:
         return confFiles[0]['conf_file_id']
      return 0


# ###### Create NorNet node #################################################
def makeNorNetNode(fullSliceList,
                   site, nodeNiceName, nodeNorNetIndex,
                   pcuID, pcuPort, norNetInterface,
                   model, bootState,
                   machineHost, machineDisplay):
   dnsName      = makeNameFromUnicode(nodeNiceName)
   nodeHostName = str.lower(dnsName['ascii'])   # Domain to be added below!

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

      existingNode = fetchNorNetNode(nodeHostName)
      if existingNode == None:
         node['boot_state'] = 'reinstall'   # New nodes need reinstall ...
         nodeID = getPLCServer().AddNode(getPLCAuthentication(), site['site_id'], node)
      else:
         nodeID = existingNode['node_id']
         if existingNode['node_state'] == 'reinstall':
            node['boot_state'] = 'reinstall'   # Updated node still needs a reinstall ...
         if getPLCServer().UpdateNode(getPLCAuthentication(), nodeID, node) != 1:
            nodeID = 0
      if nodeID <= 0:
         error('Unable to add/update node ' + nodeHostName)

      # Set extensions.
      # Initially, add NorNetManagement and NorNetNode. Then,
      # NodeUpdate will install all packages that are listed
      # in the groups extensionNorNetManagement and extensionNorNetNode.
      getPLCServer().SetNodeExtensions(getPLCAuthentication(), nodeID, 'NorNetManagement NorNetNode')

      if addOrUpdateNodeTag(nodeID, 'nornet_node_utf8', nodeHostNameUTF8) <= 0:
         error('Unable to add "nornet_node_utf8" tag to node ' + nodeHostName)
      if addOrUpdateNodeTag(nodeID, 'nornet_is_managed_node', '1') <= 0:
         error('Unable to add "nornet_is_managed_node" tag to node ' + nodeHostName)
      if addOrUpdateNodeTag(nodeID, 'nornet_node_index', str(nodeNorNetIndex)) <= 0:
         error('Unable to add "nornet_node_index" tag to node ' + nodeHostName)
      if addOrUpdateNodeTag(nodeID, 'nornet_node_interface', norNetInterface) <= 0:
         error('Unable to add "nornet_node_interface" tag to node ' + nodeHostName)
      if addOrUpdateNodeTag(nodeID, 'nornet_node_machine_host', machineHost) <= 0:
         error('Unable to add "nornet_node_machine_host" tag to node ' + nodeHostName)
      if addOrUpdateNodeTag(nodeID, 'nornet_node_machine_display', machineDisplay) <= 0:
         error('Unable to add "nornet_node_machine_display" tag to node ' + nodeHostName)

      # ====== Remove old configuration files ===============================
      #files = getPLCServer().GetConfFiles(getPLCAuthentication(), {}, ['conf_file_id', 'node_ids','source','dest'])
      #for file in files:
      #   if nodeID in file['node_ids']:
      #      print(file['conf_file_id'], file['dest'],file['source'])
      #      getPLCServer().DeleteConfFile(getPLCAuthentication(), file['conf_file_id'])

      # ====== nodemanager ==================================================
      # !!! FIXME: This should not be necessary, but currently the nm.service
      # assumes the existence of this file!
      nmConfigName    = '/var/www/html/PlanetLabConf/nodemanager'
      fileSource      = nmConfigName.replace('/var/www/html/', '')
      fileDestination = '/etc/sysconfig/nodemanager'
      confFileID = addOrUpdateConfFile({
         'postinstall_cmd' : 'service nm restart',
         'dest'            : fileDestination,
         'source'          : fileSource})
      if getPLCServer().AddConfFileToNode(getPLCAuthentication(), confFileID, nodeID) != 1:
         error('Unable to add nodemanager configuration file to node ' + nodeHostName)

      try:
         nmConfig = codecs.open(nmConfigName, 'w', 'utf-8')
         nmConfig.write('OPTIONS=""\n')
         nmConfig.close()
      except:
         print(('WARNING: Unable to write ' + nmConfigName))

      # ====== Add yum repositories =========================================
      yumRepoSourceFile = codecs.open('Repositories/nornet.repo', 'r', 'utf-8')
      yumRepoSource = yumRepoSourceFile.read()
      yumRepoSourceFile.close()

      yumKeySourceFile = codecs.open('Repositories/nornet.key', 'r', 'utf-8')
      yumKeySource = yumKeySourceFile.read()
      yumKeySourceFile.close()

      yumRepoName = '/var/www/html/PlanetLabConf/nornet.repo'
      try:
         yumRepo = codecs.open(yumRepoName, 'w', 'utf-8')
         yumRepo.write(yumRepoSource)
         yumRepo.close()
      except:
         print(('WARNING: Unable to write ' + yumRepoName))

      yumKeyName = '/var/www/html/PlanetLabConf/nornet.key'
      try:
         yumKey = codecs.open(yumKeyName, 'w', 'utf-8')
         yumKey.write(yumKeySource)
         yumKey.close()
      except:
         print(('WARNING: Unable to write ' + yumRepoName))

      fileSource      = yumRepoName.replace('/var/www/html/', '')
      fileDestination = '/etc/yum.myplc.d/nornet.repo'
      confFileID = addOrUpdateConfFile({
         'file_owner'        : 'root',
         'postinstall_cmd'   : '',
         'error_cmd'         : '',
         'preinstall_cmd'    : '',
         'dest'              : fileDestination,
         'ignore_cmd_errors' : False,
         'enabled'           : True,
         'file_permissions'  : '644',
         'source'            : fileSource,
         'always_update'     : False,
         'file_group'        : 'root'})
      if getPLCServer().AddConfFileToNode(getPLCAuthentication(), confFileID, nodeID) != 1:
         error('Unable to add repository configuration file to node ' + nodeHostName)

      fileSource      = yumKeyName.replace('/var/www/html/', '')
      fileDestination = '/etc/pki/rpm-gpg/nornet.key'
      confFileID = addOrUpdateConfFile({
         'file_owner'        : 'root',
         'postinstall_cmd'   : '',
         'error_cmd'         : '',
         'preinstall_cmd'    : '',
         'dest'              : fileDestination,
         'ignore_cmd_errors' : False,
         'enabled'           : True,
         'file_permissions'  : '644',
         'source'            : fileSource,
         'always_update'     : False,
         'file_group'        : 'root'})
      if getPLCServer().AddConfFileToNode(getPLCAuthentication(), confFileID, nodeID) != 1:
         error('Unable to add repository configuration file to node ' + nodeHostName)

      # ====== Provide proxy configurations =================================
      try:
         os.mkdir('/var/www/html/PlanetLabConf/proxy/')
      except:
         pass
      proxyName = 'proxy.' + siteNorNetDomain
      for shell in [ 'sh', 'csh' ]:
         proxyConfName = '/var/www/html/PlanetLabConf/proxy/proxy.' + shell + '.' + siteNorNetDomain
         try:
            proxyConf = codecs.open(proxyConfName, 'w', 'utf-8')
            if shell == 'sh':
               proxyConf.write('export http_proxy="http://' + proxyName  + ':3128/"\n')
               proxyConf.write('export ftp_proxy="http://'  + proxyName  + ':3128/"\n')
               proxyConf.write('export no_proxy="' + siteNorNetDomain + '"\n')
            elif shell == 'csh':
               proxyConf.write('setenv http_proxy "http://' + proxyName  + ':3128/"\n')
               proxyConf.write('setenv ftp_proxy "http://'  + proxyName  + ':3128/"\n')
               proxyConf.write('setenv no_proxy "' + siteNorNetDomain + '"\n')
            proxyConf.close()
         except:
            print(('WARNING: Unable to write ' + proxyConfName))

         fileSource      = 'PlanetLabConf/proxy/proxy.' + shell + '.' + siteNorNetDomain
         fileDestination = '/etc/profile.d/proxy.' + shell
         confFileID = addOrUpdateConfFile({
            'file_owner'        : 'root',
            'postinstall_cmd'   : '',
            'error_cmd'         : '',
            'preinstall_cmd'    : '',
            'dest'              : fileDestination,
            'ignore_cmd_errors' : False,
            'enabled'           : True,
            'file_permissions'  : '644',
            'source'            : fileSource,
            'always_update'     : False,
            'file_group'        : 'root'})
         if getPLCServer().AddConfFileToNode(getPLCAuthentication(), confFileID, nodeID) != 1:
            error('Unable to add proxy.' + shell + ' configuration file to node ' + nodeHostName)

      # ====== Hack to handle openvswitch start/stop correctly ==============
      # See https://docs.google.com/a/simula.no/document/d/1WRZ7kN6KwZRaeNOi51-uNmintCVwdkzhM2W3To6uV_Y/edit?pli=1 .
      confFileID = addOrUpdateConfFile({
         'file_owner'        : 'root',
         'postinstall_cmd'   : '/bin/systemctl reenable openvswitch.service',
         'error_cmd'         : '',
         'preinstall_cmd'    : '',
         'dest'              : '/lib/systemd/system/openvswitch.service',
         'ignore_cmd_errors' : False,
         'enabled'           : True,
         'file_permissions'  : '644',
         'source'            : 'PlanetLabConf/openvswitch/openvswitch.service',
         'always_update'     : False,
         'file_group'        : 'root'})
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
      _updateNorNetInterfaces(newNode, site, norNetInterface)

      # ====== Print configuration files of the node ========================
      #files = getPLCServer().GetConfFiles(getPLCAuthentication(), {}, ['conf_file_id', 'node_ids', 'source', 'dest'])
      #for file in files:
      #   if nodeID in file['node_ids']:
      #      print('Config file ' + str(file['conf_file_id']) + ': ' + file['source'] + ' -> ' + file['dest'])

      # ====== Update slivers with new configuration ========================
      for slice in fullSliceList:
         sliceNodeIndex = getSliceNodeIndexOfNorNetSlice(slice, newNode)
         if sliceNodeIndex != 0:
            print(('Updating ' + slice['slice_name']))
            _updateSliceNodeNetConfig(slice, newNode, site, sliceNodeIndex)

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
def addOrUpdateSliceTag(sliceID, node, tagName, tagValue):
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
def makeNorNetSlice(sliceName, ownAddress, sliceDescription, sliceUrl, expirationTime, fcDistro = None, plDistro = None):
   try:
      # ====== Add slice =====================================================
      log('Adding slice ' + sliceName + ' ...')
      slice = {}
      slice['name']        = sliceName
      slice['description'] = sliceDescription
      slice['url']         = sliceUrl
      slice['max_nodes']   = 1000000

      existingSlice = getPLCServer().GetSlices(getPLCAuthentication(),
                                               { 'name' : sliceName },
                                               [ 'slice_id', 'node_ids', 'name', 'description', 'url', 'initscript_code', 'expires' ])
      try:
         sliceID = int(existingSlice[0]['slice_id'])
         # print(existingSlice)
         if sliceUrl == None:
            sliceUrl = existingSlice[0]['url']
         if sliceDescription == None:
            sliceDescription = existingSlice[0]['description']
      except:
         sliceID = 0

      if sliceUrl == None:
         sliceUrl = 'invalid:'
      if sliceDescription == None:
         sliceDescription = '!!! NO DESCRIPTION !!!'

      if sliceID == 0:
         sliceID = getPLCServer().AddSlice(getPLCAuthentication(), slice)

      # UpdateSlice() may only have certain fields. Therefore, initialize
      # "slice" object again, with only the allowed fields included.
      slice = {}
      slice['description'] = sliceDescription
      slice['url']         = sliceUrl
      if expirationTime == 0:
         slice['expires'] = int(time.mktime(time.strptime('2038-01-18@23:59:59', '%Y-%m-%d@%H:%M:%S')))
      else:
         slice['expires'] = int(expirationTime)

      if sliceID == 0:
         sliceID = getPLCServer().AddSlice(getPLCAuthentication(), slice)
      if sliceID != 0:
         if getPLCServer().UpdateSlice(getPLCAuthentication(), sliceID, slice) != 1:
           sliceID = 0

      if sliceID <= 0:
         error('Unable to add/update slice ' + sliceName)

      if addOrUpdateSliceTag(sliceID, None, 'nornet_is_managed_slice', '1') <= 0:
         error('Unable to add "nornet_is_managed_slice" tag to slice ' + sliceName)
      if ownAddress == True:
         allocateOwnAddress = 1
      else:
         allocateOwnAddress = 0
      if addOrUpdateSliceTag(sliceID, None, 'nornet_slice_own_addresses', str(allocateOwnAddress)) <= 0:
         error('Unable to add "nornet_slice_own_addresses" tag to slice ' + sliceName)
      if fcDistro != None:
         if addOrUpdateSliceTag(sliceID, None, 'fcdistro', fcDistro) <= 0:
            error('Unable to add "fcDistro" tag to slice ' + sliceName)
      if plDistro != None:
         if addOrUpdateSliceTag(sliceID, None, 'pldistro', plDistro) <= 0:
            error('Unable to add "plDistro" tag to slice ' + sliceName)

   except Exception as e:
      error('Adding slice ' + sliceName + ' has failed: ' + str(e))

   return fetchNorNetSlice(sliceName)


# ###### Find a slice node index for a new slice ############################
def _findPossibleSliceNodeIndex(fullSiteList, fullNodeList, fullSliceList, thisSlice, thisNode):
   thisSite                 = getNorNetSiteOfNode(fullSiteList, thisNode)
   possibleSliceNodeIndexes = list(NorNet_Configuration['NorNet_Slice_NodeIndexRange'])

   log('Finding node ID for slice ' + thisSlice['slice_name'] + \
       ' on node ' + thisNode['node_name'] + \
       ' at site ' + thisSite['site_long_name'] + ' ...')

   preferredNodeIndex = None
   for node in fullNodeList:
      site = getNorNetSiteOfNode(fullSiteList, node)
      if site['site_id'] != thisSite['site_id']:
         continue

      # log('-> Node ' + node['node_name'])
      for slice in fullSliceList:
         if ((slice['slice_id'] == thisSlice['slice_id']) and
             (node['node_id'] == thisNode['node_id'])):
            # Ignore current slice's allocation on current node
            preferredNodeIndex = getSliceNodeIndexOfNorNetSlice(slice, node)

         elif node['node_id'] in slice['slice_node_ids']:
            sliceNodeIndex = getSliceNodeIndexOfNorNetSlice(slice, node)
            if ((sliceNodeIndex > 0) and (sliceNodeIndex in possibleSliceNodeIndexes)):
               possibleSliceNodeIndexes.remove(sliceNodeIndex)

   if len(possibleSliceNodeIndexes) > 0:
      if ((preferredNodeIndex != None) and
          (preferredNodeIndex in possibleSliceNodeIndexes)):
         log('=> Using existing allocation: ' + str(preferredNodeIndex))
         return preferredNodeIndex
      else:
         i = 0   # int(round(random.uniform(0, len(possibleSliceNodeIndexes)-1)))
         log('=> Using new allocation: ' + str(possibleSliceNodeIndexes[i]))
         return possibleSliceNodeIndexes[i]

   return 0


# ###### Select some nodes ##################################################
def _selectNodes(slice, siteNodeList, maxNodesPerSite):
   # ====== Distinguish odd and even nodes ==================================
   selectedNodes = []
   evenNodes     = []
   oddNodes      = []
   for node in siteNodeList:
      if (node['node_id'] % 2) == 1:
         oddNodes.append(node)
      else:
         evenNodes.append(node)


   # ====== Preselect nodes that are already allocated to this slice ========
   sliceTags = slice['slice_tags']
   for sliceTag in sliceTags:
      if sliceTag['tagname'] == 'nornet_slice_node_index':
         for node in siteNodeList:
            if node['node_id'] == sliceTag['node_id']:
               if len(selectedNodes) < maxNodesPerSite:
                  selectedNodes.append(node)


   # ====== Select random nodes =============================================
   updated = True
   while ((len(selectedNodes) < maxNodesPerSite) and (updated == True)):
      updated = False
      if len(oddNodes) > 0:
         r = int(round(random.uniform(0, len(oddNodes) - 1)))
         if not oddNodes[r] in selectedNodes:
            selectedNodes.append(oddNodes[r])
         oddNodes.remove(oddNodes[r])
         updated = True
      if ((len(selectedNodes) < maxNodesPerSite) and (len(evenNodes) > 0)):
         r = int(round(random.uniform(0, len(evenNodes) - 1)))
         if not evenNodes[r] in selectedNodes:
            selectedNodes.append(evenNodes[r])
         evenNodes.remove(evenNodes[r])
         updated = True

   #for node in selectedNodes:
      #print('S=',node['node_name'])

   return(selectedNodes)


# ###### Update per-sliver network configuration ############################
def _updateSliceNodeNetConfig(slice, node, site, sliceNodeIndex):
   siteIndex = site['site_index']
   nodeIndex = node['node_index']

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

            ifIPv4 = makeNorNetIP(providerIndex, siteIndex, nodeIndex, 4, sliceNodeIndex)
            ifIPv6 = makeNorNetIP(providerIndex, siteIndex, nodeIndex, 6, sliceNodeIndex)

            if addresses == 0:
               bridgeInterfaceConfig['IPADDR']  = str(ifIPv4.ip)
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

   if addOrUpdateSliceTag(slice['slice_id'], node, 'nornet_slice_node_index', str(sliceNodeIndex)) <= 0:
      error('Unable to add "nornet_slice_node_index" tag to slice ' + sliceName)
   if addOrUpdateSliceTag(slice['slice_id'], node, 'interface', str(bridgeInterfaceConfig)) <= 0:
      error('Unable to add "interface" tag to slice ' + sliceName)


# ###### Add NorNet slice to NorNet nodes  ##################################
def addNorNetSliceToNorNetNodes(fullSiteList, fullNodeList, fullSliceList, slice, nodesList, maxNodesPerSite):
   addedNodeIDs = []
   nodeIDs = []
   for siteIndex in fullSiteList:
      site         = fullSiteList[siteIndex]
      siteNodeList = []
      for node in nodesList:
         if node['node_site_id'] != site['site_id']:
            continue
         siteNodeList.append(node)

      selectedNodeList = _selectNodes(slice, siteNodeList, maxNodesPerSite)
      for node in selectedNodeList:
         # ====== Add slice to node =========================================
         getPLCServer().AddSliceToNodes(getPLCAuthentication(),
                                        slice['slice_id'], [ node['node_id'] ])

         # ====== Give slice its own addresses, if requested ================
         sliceOwnAddresses = slice['slice_own_addresses']
         if sliceOwnAddresses != 0:
            # ====== Get slice node index ===================================
            sliceNodeIndex = _findPossibleSliceNodeIndex(fullSiteList, fullNodeList, fullSliceList, slice, node)
            if sliceNodeIndex == 0:
               print('WARNING: No possible slice node index available!\n')
               continue

            addedNodeIDs.append(node['node_id'])

            # ====== Create configuration ===================================
            site = getNorNetSiteOfNode(fullSiteList, node)
            if site == None:
               error('Site not found?!')

            _updateSliceNodeNetConfig(slice, node, site, sliceNodeIndex)

            # Now, the slice list needs to be reloaded in order to update the allocation!
            fullSliceList = fetchNorNetSliceList()


   # Remove not selected nodes from slice
   for node in fullNodeList:
      if not node['node_id'] in addedNodeIDs:
         #print('REM ' + node['node_name'])
         getPLCServer().DeleteSliceFromNodes(getPLCAuthentication(),
                                             slice['slice_id'], [ node['node_id'] ])


# ###### Add users to NorNet slice  #########################################
def addNorNetUsersToNorNetSlice(slice, usersList):
   for user in usersList:
      getPLCServer().AddPersonToSlice(getPLCAuthentication(),
                                      user['user_id'], slice['slice_id'])
