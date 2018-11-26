#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# NorNet PLC API
# Copyright (C) 2012-2019 by Thomas Dreibholz
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
import sys
import pwd
import getpass
import xmlrpc.client

from ipaddress import ip_address, IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

# NorNet
from NorNetConfiguration import *
from NorNetTools         import *
from NorNetProviderSetup import *



# ###### Log into PLC #######################################################
def loginToPLC(overrideUser = None, quietMode = False):
   global plc_server
   global plc_authentication

   # ====== Obtain configuration from configuration file ====================
   loadNorNetConfiguration(quietMode = quietMode)

   # ====== Log into PLC ====================================================
   plcAddress = getPLCAddress()
   if overrideUser != None:
      user     = overrideUser
      password = getpass.getpass('Password for user ' + user + ': ')
   else:
      user     = NorNet_Configuration['NorNetPLC_User']
      password = NorNet_Configuration['NorNetPLC_Password']

   if quietMode == False:
      log('Logging into PLC ' + user + '/' + str(plcAddress) + ' ...')
   try:
      apiURL = 'https://[' + str(plcAddress) + ']/PLCAPI/'
      plc_server = xmlrpc.client.ServerProxy(apiURL, allow_none=True)

      plc_authentication = {}
      plc_authentication['AuthMethod'] = 'password'
      plc_authentication['Username']   = user
      plc_authentication['AuthString'] = password

      if plc_server.AuthCheck(plc_authentication) != 1:
         raise Exception('Authorization at PLC failed!')

   except Exception as e:
      raise Exception('Unable to log into PLC: ' + str(e))


# ###### Get PLC address ####################################################
def getPLCAddress():
   return NorNet_Configuration['NorNetPLC_Address']


# ###### Get PLC server object ##############################################
def getPLCServer():
   return plc_server


# ###### Get PLC authentication object ######################################
def getPLCAuthentication():
   return plc_authentication


# ###### Find site ID #######################################################
def lookupSiteID(siteName):
   try:
      site = plc_server.GetSites(plc_authentication,
                                 {'name': siteName}, ['site_id'])
      siteID = int(site[0]['site_id'])
      return(siteID)

   except:
      return(0)


# ###### Fetch list of NorNet sites #########################################
def fetchNorNetSite(siteNameToFind, justEnabledSites = True):
   global plc_server
   global plc_authentication

   if siteNameToFind == None:   # Get full list
      filter = { }
   else:              # Only perform lookup for given name
      filter = { 'name' : siteNameToFind }

   try:
      norNetSiteList = dict([])
      fullSiteList   = plc_server.GetSites(plc_authentication, filter,
                                           ['site_id', 'enabled', 'abbreviated_name', 'name', 'url', 'latitude', 'longitude'])
      for site in fullSiteList:
         if ((justEnabledSites == True) and (site['enabled'] == False)):
            continue;

         siteID       = int(site['site_id'])
         siteTagsList = plc_server.GetSiteTags(plc_authentication,
                                               { 'site_id' : siteID },
                                               [ 'site_id', 'tagname', 'value' ])
         if ((int(getTagValue(siteTagsList, 'nornet_is_managed_site', '-1')) < 1) and (siteNameToFind == None)):
            continue
         siteName             = site['name']
         siteAbbrev           = site['abbreviated_name']
         siteIndex            = int(getTagValue(siteTagsList, 'nornet_site_index', '-1'))
         siteDomain           = getTagValue(siteTagsList, 'nornet_site_domain', '')
         siteDefProviderIndex = int(getTagValue(siteTagsList, 'nornet_site_default_provider_index', '-1'))
         if siteDefProviderIndex < 1:
            siteDefProviderIndex = 0
            # error('Site ' + siteName + ' has no NorNet Default Provider Index')
         if ((not re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", siteAbbrev)) and (siteNameToFind == None)):
            error('Bad site abbreviation ' + siteAbbrev)
         if (((siteIndex < NorNet_MinSiteIndex) or (siteIndex > NorNet_MaxSiteIndex)) and (siteNameToFind == None)):
            error('Bad site index ' + str(siteIndex))
         siteContacts = []
         for i in range(0, NorNet_MaxSiteContacts):
            contact = getTagValue(siteTagsList, 'nornet_site_contact' + str(i), '')
            if contact != '':
               siteContacts.append(contact)

         norNetSite = {
            'site_id'                     : siteID,
            'site_enabled'                : site['enabled'],
            'site_index'                  : siteIndex,
            'site_short_name'             : siteAbbrev,
            'site_long_name'              : site['name'],
            'site_utf8'                   : getTagValue(siteTagsList, 'nornet_site_utf8', str(site['name'])),
            'site_domain'                 : siteDomain,
            'site_latitude'               : site['latitude'],
            'site_longitude'              : site['longitude'],
            'site_altitude'               : float(getTagValue(siteTagsList, 'nornet_site_altitude', '0.0')),
            'site_contacts'               : siteContacts,
            'site_url'                    : site['url'],
            'site_tags'                   : siteTagsList,
            'site_default_provider_index' : siteDefProviderIndex
         }

         if siteNameToFind != None:
            return(norNetSite)

         norNetSiteList[siteIndex] = norNetSite

      if len(norNetSiteList) == 0:
         return None
      return(norNetSiteList)

   except Exception as e:
      error('Unable to fetch NorNet site list: ' + str(e))


# ###### Fetch list of NorNet sites #########################################
def fetchNorNetSiteList(justEnabledSites = True):
   log('Fetching NorNet site list ...')
   return fetchNorNetSite(None, justEnabledSites)


# ###### Get the providers a site is connected to ###########################
def getNorNetProvidersForSite(norNetSite):
   try:
      siteTagsList = norNetSite['site_tags']

      # ====== Get outgoing interfaces ======================================
      norNetProviderList = dict([])
      for i in range(0, NorNet_MaxProviders):
         providerIndex = int(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_index', '-1'))
         if providerIndex <= 0:
            continue
         providerInfo           = getNorNetProviderInfo(providerIndex)
         providerTbIPv4         = IPv4Interface(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv4', '0.0.0.0/0'))
         providerGwIPv4         = IPv4Address(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_gateway_ipv4', '0.0.0.0'))
         if not providerGwIPv4 in providerTbIPv4.network:
            error('Bad IPv4 network/gateway settings of provider ' + providerInfo[0] + \
                  ': ' + str(providerGwIPv4) + ' not in ' + str(providerGwIPv4))
         providerTbIPv6         = IPv6Interface(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv6', '::/0'))
         providerGwIPv6         = IPv6Address(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_gateway_ipv6', '::'))
         providerMTU            = int(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_mtu', 1500))
         if ((providerMTU < 1280) or (providerMTU > 9000)):
            error('Bad MTU for provider: ' + str(provider))
         try:
            providerType        = str(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_type', ''))
            providerDownstream  = int(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_downstream', 0))
            providerUpstream    = int(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_upstream', 0))
         except:
            providerType        = ''
            providerDownstream  = 0
            providerUpstream    = 0
         if not providerGwIPv6 in providerTbIPv6.network:
            error('Bad IPv6 network/gateway settings of provider ' + providerInfo[0] + \
                  ': ' + str(providerGwIPv6) + ' not in ' + str(providerGwIPv6))
         providerTbInterface = getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_interface', '')
         if not re.match(r"^[a-zA-Z0-9_-]*$", providerTbInterface):
            error('Bad interface name ' + providerTbInterface)
         norNetProvider = {
            'provider_index'               : providerIndex,
            'provider_long_name'           : providerInfo[0],
            'provider_short_name'          : providerInfo[1],
            'provider_tunnelbox_ipv4'      : providerTbIPv4,
            'provider_tunnelbox_ipv6'      : providerTbIPv6,
            'provider_tunnelbox_interface' : providerTbInterface,
            'provider_gateway_ipv4'        : providerGwIPv4,
            'provider_gateway_ipv6'        : providerGwIPv6,
            'provider_mtu'                 : providerMTU,
            'provider_type'                : providerType,
            'provider_downstream'          : providerDownstream,
            'provider_upstream'            : providerUpstream
         }

         norNetProviderList[providerIndex] = norNetProvider

      return(norNetProviderList)

   except Exception as e:
      error('Unable to get NorNet providers for site ' + norNetSite['site_long_name'] + ': ' + str(e))


# ###### Find PCU ID for node ID ############################################
def lookupPCUIDforNode(nodeID):
   try:
      pcu = plc_server.GetNodes(plc_authentication,
                                { 'node_id' : nodeID }, ['pcu_ids'])
      if len(pcu) > 0:
         pcuID = int(pcu[0]['pcu_ids'][0])
         return(pcuID)
      else:
         return(0)

   except:
      return(0)


# ###### Find PCU ID ########################################################
def lookupPCUID(pcuName):
   try:
      pcu = plc_server.GetPCUs(plc_authentication,
                               { 'hostname': pcuName }, ['pcu_id'])
      pcuID = int(pcu[0]['pcu_id'])
      return(pcuID)

   except:
      return(0)


# ###### Find node ID #######################################################
def lookupNodeID(nodeName):
   try:
      node = plc_server.GetNodes(plc_authentication,
                                 { 'hostname': nodeName }, ['node_id'])
      nodeID = int(node[0]['node_id'])
      return(nodeID)

   except:
      return(0)


# ###### Find interface ID ##################################################
def lookupPrimaryInterfaceID(node):
   try:
      interface = plc_server.GetInterfaces(plc_authentication,
                                           { 'node_id'     : node['node_id'],
                                             'is_primary'  : True },
                                           ['interface_id'])
      interfaceID = int(interface[0]['interface_id'])
      return(interfaceID)

   except:
      return(0)


# ###### Fetch list of NorNet nodes #########################################
def fetchNorNetNode(nodeNameToFind = None, site = None):
   global plc_server
   global plc_authentication

   filter = { }

   if nodeNameToFind != None:   # Only perform lookup for given name
      filter = { 'hostname':  nodeNameToFind }
   if site != None:
      filter.update( { 'site_id' : site['site_id'] } )

   try:
      norNetNodeList = []
      fullNodeList   = plc_server.GetNodes(plc_authentication, filter,
                                           ['node_id', 'site_id', 'hostname', 'model', 'boot_state', 'ssh_rsa_key'])
      for node in fullNodeList:
         nodeID       = int(node['node_id'])
         nodeSiteID   = int(node['site_id'])
         nodeTagsList = plc_server.GetNodeTags(plc_authentication,
                                               { 'node_id' : nodeID },
                                               [ 'node_id', 'tagname', 'value' ])
         if int(getTagValue(nodeTagsList, 'nornet_is_managed_node', '-1')) < 1:
            continue
         nodeIndex = int(getTagValue(nodeTagsList, 'nornet_node_index', '-1'))
         if nodeIndex < 1:
            error('Node ' + nodeNameToFind + ' has invalid NorNet Node Index')
         nodeInterface = getTagValue(nodeTagsList, 'nornet_node_interface', '')
         if nodeInterface == '':
            error('Node ' + nodeNameToFind + ' has invalid NorNet interface name')

         norNetNode = {
            'node_id'               : nodeID,
            'node_site_id'          : nodeSiteID,
            'node_index'            : nodeIndex,
            'node_name'             : node['hostname'],
            'node_utf8'             : getTagValue(nodeTagsList, 'nornet_node_utf8', str(node['hostname'])),
            'node_nornet_interface' : nodeInterface,
            'node_model'            : node['model'],
            'node_type'             : 'NorNet Managed Node',
            'node_state'            : node['boot_state'],
            'node_ssh_rsa_key'      : node['ssh_rsa_key'],
            'node_v4only'           : 0,
            'node_v6only'           : 0,
            'node_tags'             : nodeTagsList
         }

         if nodeNameToFind != None:
            return(norNetNode)

         norNetNodeList.append(norNetNode)

      if len(norNetNodeList) == 0:
         return None
      return(norNetNodeList)

   except Exception as e:
      error('Unable to fetch NorNet node list: ' + str(e))


# ###### Fetch list of NorNet nodes #########################################
def fetchNorNetNodeList():
   log('Fetching NorNet node list ...')
   return fetchNorNetNode(None, None)


# ###### Fetch list of NorNet nodes for given site ##########################
def fetchNorNetNodeListForSite(site):
   log('Fetching NorNet node list ...')
   return fetchNorNetNode(None, site)


# ###### Get NorNet Site for given domain ###################################
def getNorNetSiteOfDomain(fullSiteList, domain):
   for siteIndex in fullSiteList:
      if domain == fullSiteList[siteIndex]['site_domain']:
         return fullSiteList[siteIndex]
   return None


# ###### Get NorNet Site of NorNet node #####################################
def getNorNetSiteOfNode(fullSiteList, node):
   siteID = node['node_site_id']
   for siteIndex in fullSiteList:
      if siteID == fullSiteList[siteIndex]['site_id']:
         return fullSiteList[siteIndex]
   return None


# ###### Fetch list of NorNet users #########################################
def fetchNorNetUser(userNameToFind):
   global plc_server
   global plc_authentication

   if userNameToFind == None:   # Get full list
      filter = { 'enabled' : True }
   else:              # Only perform lookup for given name
      filter = { 'enabled' : True,
                 'email'   : userNameToFind }

   try:
      norNetUserList = dict([])
      fullUserList   = plc_server.GetPersons(plc_authentication, filter,
                                             [ 'person_id', 'title', 'first_name', 'last_name', 'email', 'phone', 'roles' ])
      for user in fullUserList:
         userID = int(user['person_id'])
         norNetUser = {
            'user_id'         : userID,
            'user_title'      : user['title'],
            'user_first_name' : user['first_name'],
            'user_last_name'  : user['last_name'],
            'user_email'      : user['email'],
            'user_phone'      : user['phone'],
            'user_roles'      : user['roles']
         }

         if userNameToFind != None:
            return(norNetUser)

         norNetUserList[userID] = norNetUser

      if len(norNetUserList) == 0:
         return None
      return(norNetUserList)

   except Exception as e:
      error('Unable to fetch NorNet user list: ' + str(e))


# ###### Fetch list of NorNet users #########################################
def fetchNorNetUserList():
   log('Fetching NorNet user list ...')
   return fetchNorNetUser(None)


# ###### Get users of NorNet Site ###########################################
def fetchUsersOfNorNetSite(fullUserList, site, role):
   filter = { 'site_id' : site['site_id'] }
   try:
      siteList = plc_server.GetSites(plc_authentication, filter,
                                     [ 'person_ids' ])
      userIDs = siteList[0]['person_ids']

      selectedUsers = []
      for userID in userIDs:
         try:
            if role == None:
               selectedUsers.append(fullUserList[userID])
            elif role in fullUserList[userID]['user_roles']:
               selectedUsers.append(fullUserList[userID])
         except Exception as e:
            continue

      if len(selectedUsers) == 0:
         return None
      return(selectedUsers)

   except Exception as e:
      error('Unable to fetch NorNet users list of site ' + site['site_long_name'] + ': ' + str(e))


# ###### Find person ID #####################################################
def lookupPersonID(eMail):
   try:
      person = plc_server.GetPersons(plc_authentication,
                                     {'email': eMail}, ['person_id'])
      personID = int(person[0]['person_id'])
      return(personID)

   except:
      return(0)


# ###### Fetch list of NorNet slices ########################################
def fetchNorNetSlice(sliceNameToFind):
   global plc_server
   global plc_authentication

   if sliceNameToFind == None:   # Get full list
      filter = { }
   else:              # Only perform lookup for given name
      filter = { 'name' : sliceNameToFind }

   try:
      norNetSliceList = []
      fullSliceList   = plc_server.GetSlices(plc_authentication, filter,
                                             [ 'slice_id', 'node_ids', 'name', 'description', 'url', 'initscript_code', 'expires' ])
      for slice in fullSliceList:
         sliceID = int(slice['slice_id'])

         sliceTagsList = plc_server.GetSliceTags(plc_authentication,
                                                 { 'slice_id' : sliceID },
                                                 [ 'slice_id', 'node_id', 'tagname', 'value' ])
         if int(getTagValue(sliceTagsList, 'nornet_is_managed_slice', '-1')) < 1:
            continue
         sliceOwnAddresses = int(getTagValue(sliceTagsList, 'nornet_slice_own_addresses', '0'))

         norNetSlice = {
            'slice_id'              : sliceID,
            'slice_name'            : slice['name'],
            'slice_description'     : slice['description'],
            'slice_url'             : slice['url'],
            'slice_initscript_code' : slice['initscript_code'],
            'slice_expires'         : slice['expires'],
            'slice_node_ids'        : slice['node_ids'],
            'slice_own_addresses'   : sliceOwnAddresses,
            'slice_tags'            : sliceTagsList
         }

         if sliceNameToFind != None:
            return(norNetSlice)

         norNetSliceList.append(norNetSlice)

      if len(norNetSliceList) == 0:
         return None
      return(norNetSliceList)

   except Exception as e:
      error('Unable to fetch NorNet slice list: ' + str(e))


# ###### Fetch list of NorNet slices ########################################
def fetchNorNetSliceList():
   log('Fetching NorNet slice list ...')
   return fetchNorNetSlice(None)


# ###### Find slice ID ######################################################
def lookupSliceID(sliceName):
   try:
      slice = plc_server.GetSlices(plc_authentication,
                                   { 'name' : sliceName }, [ 'slice_id' ])
      sliceID = int(slice[0]['slice_id'])
      return(sliceID)

   except:
      return(0)


# ###### Get slice node index of NorNet slice ###############################
def getSliceNodeIndexOfNorNetSlice(slice, node):
   for tag in slice['slice_tags']:
      if ((tag['node_id'] == node['node_id']) and
          (tag['tagname'] == 'nornet_slice_node_index')):
         return(int(tag['value']))
   return 0


# ###### Get list of node tags ##############################################
def fetchNodeTagsList(nodeID):
   global plc_server
   global plc_authentication

   try:
      nodeTagsList = plc_server.GetNodeTags(plc_authentication,
                                            { 'node_id' : nodeID },
                                            [ 'tagname', 'value' ])
      return(nodeTagsList)

   except:
      error('Unable to fetch node tag list!')
