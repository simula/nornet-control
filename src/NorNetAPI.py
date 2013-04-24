#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet PLC API
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


import re;
import sys;
import pwd;
import codecs;
import getpass;

# XML-RPC
if sys.version_info < (3,0,0):
   import xmlrpclib;
else:
   import xmlrpc.client;

# Needs package python-ipaddr (Fedora Core, Ubuntu, Debian)!
from ipaddr import IPAddress, IPv4Address, IPv4Network, IPv6Address, IPv6Network;

# NorNet
from NorNetTools         import *;
from NorNetProviderSetup import *;



NorNetPLC_ConfigFile                   = '/etc/nornet/nornetapi-config'
NorNetPLC_FallbackConfigFile           = 'nornetapi-config'


NorNetPLC_Address                      = None
NorNetPLC_User                         = None
NorNetPLC_Password                     = None

NorNet_LocalSite_SiteIndex             = None
NorNet_LocalSite_DefaultProviderIndex  = None
NorNet_LocalSite_TBDefaultProviderIPv4 = None

NorNet_LocalNode_Hostname              = None
NorNet_LocalNode_Index                 = None
NorNet_LocalNode_NorNetInterface       = None
NorNet_LocalNode_NorNetUser            = None

NorNet_FileServ_RWSystems              = None
NorNet_LocalSite_DHCPServer_Dynamic    = None


# ###### Read configuration file ############################################
def loadNorNetConfiguration():
   log('Reading configuration from ' + NorNetPLC_ConfigFile + ' ...')
   try:
      inputFile = codecs.open(NorNetPLC_ConfigFile, 'r', 'utf-8')
   except:
      try:
         log('###### Cannot open ' + NorNetPLC_ConfigFile + ', trying fallback file ' + NorNetPLC_FallbackConfigFile + ' ... ######')
         inputFile = codecs.open(NorNetPLC_FallbackConfigFile, 'r', 'utf-8')

      except Exception as e:
         error('Configuration file ' + NorNetPLC_FallbackConfigFile + ' cannot be read: ' + str(e))

   lines = tuple(inputFile)
   for line in lines:
      if re.match('^[ \t]*[#\n]', line):
         continue
      elif re.match('^[a-zA-Z0-9_]*[ \t]*=', line):
         unicodeCommand = line.replace('=\'','=u\'')   # Interpret string as Unicode!
         # print unicodeCommand
         exec(unicodeCommand, globals())
      else:
         error('Bad configuration line: ' + line)

   if NorNetPLC_Address == None:
      error('NorNetPLC_Address has not been set in configuration file!')
   if NorNetPLC_User == None:
      error('NorNetPLC_User has not been set in configuration file!')
   if NorNetPLC_Password == None:
      error('NorNetPLC_Password has not been set in configuration file!')
   try:
      user = pwd.getpwnam(getLocalNodeNorNetUser())
   except:
      error('NorNet_LocalNode_NorNetUser has invalid user "' + str(getLocalNodeNorNetUser()) + '"!')

   sys.stdout = codecs.getwriter('utf8')(sys.stdout)
   sys.stderr = codecs.getwriter('utf8')(sys.stderr)
   sys.stdin  = codecs.getreader('utf8')(sys.stdin)


# ###### Log into PLC #######################################################
def loginToPLC(overrideUser = None):
   global plc_server
   global plc_authentication

   # ====== Obtain configuration from configuration file ====================
   loadNorNetConfiguration()

   # ====== Log into PLC ====================================================
   if overrideUser != None:
      user     = overrideUser
      password = getpass.getpass('Password for user ' + user + ': ')
   else:
      user     = NorNetPLC_User
      password = NorNetPLC_Password
   log('Logging into PLC ' + user + '/' + NorNetPLC_Address + ' ...')
   try:
      apiURL     = 'https://' + NorNetPLC_Address + '/PLCAPI/'
      if sys.version_info < (3,0,0):
         plc_server = xmlrpclib.ServerProxy(apiURL, allow_none=True)
      else:
         plc_server = xmlrpc.client.ServerProxy(apiURL, allow_none=True)

      plc_authentication = {}
      plc_authentication['AuthMethod'] = 'password'
      plc_authentication['Username']   = user
      plc_authentication['AuthString'] = password

      if plc_server.AuthCheck(plc_authentication) != 1:
         error('Authorization at PLC failed!')

   except:
      error('Unable to log into PLC!')


# ###### Get PLC address ####################################################
def getPLCAddress():
   return IPv4Address(NorNetPLC_Address)


# ###### Get PLC server object ##############################################
def getPLCServer():
   return plc_server


# ###### Get PLC authentication object ######################################
def getPLCAuthentication():
   return plc_authentication


# ###### Get local Site Index ###############################################
def getLocalSiteIndex():
   try:
      return int(NorNet_LocalSite_SiteIndex)
   except:
      return None


# ###### Get local Default Provider Index ###################################
def getLocalDefaultProviderIndex():
   try:
      return int(NorNet_LocalSite_DefaultProviderIndex)
   except:
      return None


# ###### Get local tunnelbox's outer IPv4 address ###########################
def getLocalTunnelboxDefaultProviderIPv4():
   return NorNet_LocalSite_TBDefaultProviderIPv4


# ###### Get local node hostname ############################################
def getLocalNodeHostname():
   return NorNet_LocalNode_Hostname


# ###### Get local node index ###############################################
def getLocalNodeIndex():
   try:
      return int(NorNet_LocalNode_Index)
   except:
      return None


# ###### Get local node hostname ############################################
def getLocalNodeNorNetInterface():
   return NorNet_LocalNode_NorNetInterface


# ###### Get local node NorNet user #########################################
def getLocalNodeNorNetUser():
   if NorNet_LocalNode_NorNetUser == None:
      return 'nornetpp'
   else:
      return NorNet_LocalNode_NorNetUser


# ###### Get local node configuration string ################################
def getLocalNodeConfigurationString(nodeIndex):
   try:
      return unicode(eval('NorNet_LocalSite_Node' + str(nodeIndex)))
   except:
      return u''


# ###### Get local node configuration string ################################
def getFileServRWSystemsConfigurationString():
   try:
      return eval('NorNet_FileServ_RWSystems')
   except:
      return ''


# ###### Get DHCPD node configuration string ################################
def getLocalSiteDHCPServerDynamicConfigurationString():
   try:
      return eval('NorNet_LocalSite_DHCPServer_Dynamic')
   except:
      return u''


# ###### Get DHCPD node configuration string ################################
def getLocalSiteDHCPServerStaticConfigurationString(nodeIndex):
   try:
      return unicode(eval('NorNet_LocalSite_DHCPServer_Static' + str(nodeIndex)))
   except:
      return u''


# ###### Get NAT range ######################################################
def getLocalSiteNATRangeString():
   try:
      return unicode(eval('NorNet_LocalSite_NAT_Range'))
   except:
      return u''


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
         if (((siteIndex < 0) or (siteIndex > 255)) and (siteNameToFind == None)):
            error('Bad site index ' + str(siteIndex))

         norNetSite = {
            'site_id'                     : siteID,
            'site_enabled'                : site['enabled'],
            'site_index'                  : siteIndex,
            'site_short_name'             : siteAbbrev,
            'site_long_name'              : site['name'],
            'site_utf8'                   : getTagValue(siteTagsList, 'nornet_site_utf8', unicode(site['name'])),
            'site_domain'                 : siteDomain,
            'site_latitude'               : site['latitude'],
            'site_longitude'              : site['longitude'],
            'site_altitude'               : float(getTagValue(siteTagsList, 'nornet_site_altitude', '0.0')),
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
      for i in range(0, NorNet_MaxProviders - 1):
         providerIndex = int(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_index', '-1'))
         if providerIndex <= 0:
            continue
         providerInfo        = getNorNetProviderInfo(providerIndex)
         providerTbIPv4      = IPv4Network(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv4', '0.0.0.0/0'))
         providerGwIPv4      = IPv4Address(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_gateway_ipv4', '0.0.0.0'))
# ???? FIXME!
         #if not providerGwIPv4 in providerTbIPv4:
            #error('Bad IPv4 network/gateway settings of provider ' + providerInfo[0] + \
                  #': ' + str(providerGwIPv4) + ' not in ' + str(providerGwIPv4))
         providerTbIPv6      = IPv6Network(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv6', '::/0'))         
         providerGwIPv6      = IPv6Address(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_gateway_ipv6', '::'))
# ???? FIXME!
         #if not providerGwIPv6 in providerTbIPv6:
            #error('Bad IPv6 network/gateway settings of provider ' + providerInfo[0])
                  #': ' + str(providerGwIPv6) + ' not in ' + str(providerGwIPv6))
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
            'provider_gateway_ipv6'        : providerGwIPv6
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
                               {'hostname': pcuName}, ['pcu_id'])
      pcuID = int(pcu[0]['pcu_id'])
      return(pcuID)

   except:
      return(0)


# ###### Find node ID #######################################################
def lookupNodeID(nodeName):
   try:
      node = plc_server.GetNodes(plc_authentication,
                                 {'hostname': nodeName}, ['node_id'])
      nodeID = int(node[0]['node_id'])
      return(nodeID)

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
                                           ['node_id', 'site_id', 'hostname', 'model', 'boot_state'])
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
            'node_utf8'             : getTagValue(nodeTagsList, 'nornet_node_utf8', unicode(node['hostname'])),
            'node_nornet_interface' : nodeInterface,
            'node_model'            : node['model'],
            'node_type'             : 'NorNet Managed Node',
            'node_state'            : node['boot_state'],
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


# ###### Find slice ID ######################################################
def lookupSliceID(sliceName):
   try:
      slice = plc_server.GetSlices(plc_authentication,
                                   {'name': sliceName}, ['slice_id'])
      sliceID = int(slice[0]['slice_id'])
      return(sliceID)

   except:
      return(0)


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
