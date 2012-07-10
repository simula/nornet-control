#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet PLC API
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


import re;
import xmlrpclib;

# Needs package python-ipaddr (Fedora Core, Ubuntu, Debian)!
from ipaddr import IPv4Address, IPv4Network, IPv6Address, IPv6Network;

# NorNet
from NorNetTools         import *;
from NorNetProviderSetup import *;



NorNetPLC_Name          = '132.252.156.21'
NorNetPLC_Root_User     = 'root@localhost.localdomain'
NorNetPLC_Root_Password = 'nntb-root'



# ###### Log into PLC #######################################################
def loginToPLC():
   global plc_server
   global plc_authentication

   log('Logging into PLC ...')
   try:
      apiURL     = 'https://' + NorNetPLC_Name + '/PLCAPI/'
      plc_server = xmlrpclib.ServerProxy(apiURL, allow_none=True)

      plc_authentication = {}
      plc_authentication['AuthMethod'] = 'password'
      plc_authentication['Username']   = NorNetPLC_Root_User
      plc_authentication['AuthString'] = NorNetPLC_Root_Password

      if plc_server.AuthCheck(plc_authentication) != 1:
         error('Authorization at PLC failed!')

   except:
      error('Unable to log into PLC!')


# ###### Get PLC server object ##############################################
def getPLCServer():
   return plc_server


# ###### Get PLC authentication object ######################################
def getPLCAuthentication():
   return plc_authentication


# ###### Find site ID #######################################################
def findSiteID(siteName):
   try:
      site = plc_server.GetSites(plc_authentication,
                                 {'name': siteName}, ['site_id'])
      siteID = int(site[0]['site_id'])
      return(siteID)

   except:
      return(0)


# ###### Get list of site tags ##############################################
def fetchSiteTagsList(siteID):
   global plc_server
   global plc_authentication

   try:
      siteTagsList = plc_server.GetSiteTags(plc_authentication,
                                            { 'site_id' : siteID },
                                            [ 'tagname', 'value' ])
      return(siteTagsList)

   except:
      error('Unable to fetch site tag list!')


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


# ###### Find node ID #######################################################
def lookupNodeID(nodeName):
   try:
      node = plc_server.GetNodes(plc_authentication,
                                 {'hostname': nodeName}, ['node_id'])
      nodeID = int(node[0]['node_id'])
      return(nodeID)

   except:
      return(0)


# ###### Fetch list of NorNet sites #########################################
def fetchNorNetSiteList():
   global plc_server
   global plc_authentication

   log('Fetching NorNet site list ...')
   try:
      filter = {'is_public': True,
                'enabled':   True}

      fullSiteList = plc_server.GetSites(plc_authentication, filter)

      norNetSiteList = dict([])
      for site in fullSiteList:
         siteID       = int(site['site_id']),
         siteTagsList = plc_server.GetSiteTags(plc_authentication,
                                               { 'site_id' : siteID },
                                               [ 'site_id', 'tagname', 'value' ])
         if int(getTagValue(siteTagsList, 'nornet_is_managed_site', '-1')) < 1:
            continue
         siteIndex    = int(getTagValue(siteTagsList, 'nornet_site_index', '-1'))
         siteName     = str(site['name'])
         siteAbbrev   = str(site['abbreviated_name'])
         if not re.match(r"^[a-zA-Z][a-zA-Z0-9]*$", siteAbbrev):
            error('Bad site abbreviation ' + siteAbbrev)
         if ((siteIndex < 0) or (siteIndex > 255)):
            error('Bad site index ' + str(siteIndex))

         norNetSite = {
            'site_id'         : siteID,
            'site_index'      : siteIndex,
            'site_short_name' : siteAbbrev,
            'site_long_name'  : str(site['name']),
            'site_tags'       : siteTagsList
         }

         norNetSiteList[siteIndex] = norNetSite

      return(norNetSiteList)

   except Exception as e:
      error('Unable to fetch NorNet site list: ' + str(e))


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
         providerInfo   = getNorNetProviderInfo(providerIndex)
         providerTbIPv4 = IPv4Address(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv4', '0.0.0.0'))
         providerTbIPv6 = IPv6Address(getTagValue(siteTagsList, 'nornet_site_tbp' + str(i) + '_address_ipv6', '::'))
         norNetProvider = {
            'provider_index'          : providerIndex,
            'provider_short_name'     : providerInfo[1],
            'provider_long_name'      : providerInfo[0],
            'provider_tunnelbox_ipv4' : providerTbIPv4,
            'provider_tunnelbox_ipv6' : providerTbIPv6
         }

         norNetProviderList[providerIndex] = norNetProvider

      return(norNetProviderList)

   except Exception as e:
      error('Unable to get NorNet providers for site ' + norNetSite['site_long_name'] + ': ' + str(e))


# ###### Get list of NorNet nodes ###########################################
def fetchNodeList():
   global plc_server
   global plc_authentication

   log('Fetching node list ...')
   try:
      nodeList = plc_server.GetNodes(plc_authentication)
      return(nodeList)

   except:
      error('Unable to fetch node list!')


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
