#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# NorNet PLC Configuration
# Copyright (C) 2012-2023 by Thomas Dreibholz
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

import shlex
import sys
import pwd
import codecs
import configparser
import io
import xmlrpc.client

from ipaddress import ip_address, IPv4Address, IPv4Interface, IPv6Address, IPv6Interface

# NorNet
from NorNetTools         import *
from NorNetProviderSetup import *



# ====== Adapt if necessary =================================================

NorNetPLC_ConstantsFile         = '/etc/nornet/nornetapi-constants'
NorNetPLC_FallbackConstantsFile = 'nornetapi-constants'

NorNetPLC_ConfigFile            = '/etc/nornet/nornetapi-config'
NorNetPLC_FallbackConfigFile    = 'nornetapi-config'

# These are the configuration defaults: just the parameters that need
# some setting in order to process the reading of the configuration from file.
NorNet_Configuration = {
   'NorNetPLC_Address'                         : None,
   'NorNetPLC_User'                            : None,
   'NorNetPLC_Password'                        : None,

   'NorNet_IPv4Prefix'                         : 'BAD',
   'NorNet_IPv6Prefix'                         : 'BAD',
   'NorNet_IPv4TunnelPrefix'                   : 'BAD',
   'NorNet_IPv6TunnelPrefix'                   : 'BAD',

   'NorNet_CentralSite_DomainName'             : None,
   'NorNet_CentralSite_BootstrapTunnelbox'     : None,
   'NorNet_CentralSite_BootstrapProviderIndex' : None,

   'NorNet_LocalSite_SiteIndex'                : None,
   'NorNet_LocalSite_DefaultProviderIndex'     : None,

   'NorNet_LocalNode_Index'                    : 0,
   'NorNet_LocalNode_Hostname'                 : 'localhost.localdomain',
   'NorNet_LocalNode_NorNetUser'               : 'nornetpp',
   'NorNet_LocalNode_NorNetInterface'          : None,
   'NorNet_LocalNode_NorNetInterfaceMatch'     : None,
   'NorNet_LocalNode_ControlBox'               : False,

   'NorNet_Slice_NodeIndexRange'               : None,

   'NorNet_Provider0'                          : '"UNKNOWN" "unknown" ""'
}

# The provider list
NorNet_ProviderList = { }

# ===========================================================================

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!! WARNING: Do not change unless you really know what you are doing! !!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Minimum and maximum indices
NorNet_MinProviderIndex=1
NorNet_MaxProviderIndex=255
NorNet_MinSiteIndex=1
NorNet_MaxSiteIndex=255
NorNet_MinNodeIndex=1
NorNet_MaxNodeIndex=255
NorNet_MinSliceIndex=1
NorNet_MaxSliceIndex=255

# TOS Settings for provider selection
NorNet_TOSSettings = [ 0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C ]

# Maximum number of external NTP servers
NorNet_MaxNTPServers = 8

# Maximum number of providers per site
NorNet_MaxProviders = 8

# Maximum number of contacts per site
NorNet_MaxSiteContacts = 4

# NorNet Internet connection to/from outside world goes via Site 1!
NorNet_SiteIndex_Central = 1

# NorNet Tunnelbox is always Node 1!
NorNet_NodeIndex_Tunnelbox = 1

# PLC is Node 2 on the Central Site!
NorNet_SiteIndex_PLC = NorNet_SiteIndex_Central
NorNet_NodeIndex_PLC = 2

# NorNet Monitor is Node 3 on the Central Site!
NorNet_SiteIndex_Monitor  = NorNet_SiteIndex_Central
NorNet_NodeIndex_Monitor  = 3

# NorNet Monitor is Node 4 on the Central Site!
NorNet_SiteIndex_FileSrv  = NorNet_SiteIndex_Central
NorNet_NodeIndex_FileSrv  = 4

# Routing Metrics
NorNet_RoutingMetric_External           = 2
NorNet_RoutingMetric_DefaultProvider    = 5
NorNet_RoutingMetric_AdditionalProvider = 10   # for the first one; next is +1, etc.

# ===========================================================================


# ###### Check whether parameter is one of given valid choices ##############
def checkParameter(parameter, choices):
   try:
      value = NorNet_Configuration[parameter]
   except:
       return ''
   for choice in choices:
      if value == choice:
         return value
   error('Parameter ' + parameter + ' has invalid value: ' + value)


# ###### Read configuration file ############################################
def loadNorNetConfiguration(includeAPIConfiguration = True, quietMode = False):
   iniString  = '[root]\n'

   # ====== Open constants file =============================================
   if quietMode == False:
      log('Reading constants from ' + NorNetPLC_ConstantsFile + ' ...')
   try:
      constantsFile = codecs.open(NorNetPLC_ConstantsFile, 'r', 'utf-8')
   except:
      try:
         if quietMode == False:
            log('###### Cannot open ' + NorNetPLC_ConstantsFile + ', trying fallback file ' + NorNetPLC_FallbackConstantsFile + ' ... ######')
         constantsFile = codecs.open(NorNetPLC_FallbackConstantsFile, 'r', 'utf-8')
      except Exception as e:
         error('Constantsuration file ' + NorNetPLC_FallbackConstantsFile + ' cannot be read: ' + str(e))

   iniString = iniString + constantsFile.read()


   # ====== Open configuration file =========================================
   if includeAPIConfiguration == True:
      if quietMode == False:
         log('Reading configuration from ' + NorNetPLC_ConfigFile + ' ...')
      try:
         configFile = codecs.open(NorNetPLC_ConfigFile, 'r', 'utf-8')
      except:
         try:
            if quietMode == False:
               log('###### Cannot open ' + NorNetPLC_ConfigFile + ', trying fallback file ' + NorNetPLC_FallbackConfigFile + ' ... ######')
            configFile = codecs.open(NorNetPLC_FallbackConfigFile, 'r', 'utf-8')
         except Exception as e:
            error('Configuration file ' + NorNetPLC_FallbackConfigFile + ' cannot be read: ' + str(e))

      iniString  = iniString + configFile.read()


   # ====== Build the configuration table ===================================
   parsedConfigFile = configparser.RawConfigParser()
   parsedConfigFile.optionxform = str   # Make it case-sensitive!
   parsedConfigFile.readfp(io.StringIO(iniString))
   for parameterName in parsedConfigFile.options('root'):
      parameterValue = parsedConfigFile.get('root', parameterName)
      if parameterValue.find('\n'):
         parameterValue = str.strip(unquote(removeComment(str.replace(parameterValue, '\n', ' '))))
      else:
         parameterValue = removeComment(parameterValue.rstrip('\n'))
      # print('<' + parameterName + '> = <' + parameterValue + '>')
      NorNet_Configuration[parameterName] = parameterValue

   # print NorNet_Configuration


   # ====== Build provider table ============================================
   for providerIndex in range(NorNet_MinProviderIndex - 1, NorNet_MaxProviderIndex + 1):
      try:
         providerConfig = NorNet_Configuration['NorNet_Provider' + str(providerIndex)]
         provider = shlex.split(providerConfig)
      except:
         provider = None
      if provider != None:
         if len(provider) < 3:
            error('Bad configuration "' + NorNet_Configuration['NorNet_Provider' + str(providerIndex)] + '" for NorNet_Provider' + str(providerIndex))

         providerLongName  = unquote(provider[0])
         providerShortName = makeNameFromUnicode(unquote(provider[1]), False)['ascii']
         providerURL       = unquote(provider[2])

         NorNet_ProviderList[providerIndex] = [ providerLongName, providerShortName, providerURL ]


   # ====== Check some important contents ===================================
   try:
      NorNet_Configuration['NorNet_IPv4Prefix'] = IPv4Interface(NorNet_Configuration['NorNet_IPv4Prefix'])
   except Exception as e:
      error('NorNet_IPv4Prefix setting "' + NorNet_Configuration['NorNet_IPv4Prefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv4Prefix'].network.prefixlen > 8:
      error('NorNet_IPv4Prefix must be at least a /8 network!')

   try:
      NorNet_Configuration['NorNet_IPv6Prefix'] = IPv6Interface(NorNet_Configuration['NorNet_IPv6Prefix'])
   except Exception as e:
      error('NorNet_IPv6Prefix setting "' + NorNet_Configuration['NorNet_IPv6Prefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv6Prefix'].network.prefixlen > 48:
      error('NorNet_IPv6Prefix must be at least a /48 network!')

   try:
      NorNet_Configuration['NorNet_IPv4TunnelPrefix'] = IPv4Interface(NorNet_Configuration['NorNet_IPv4TunnelPrefix'])
   except Exception as e:
      error('NorNet_IPv4TunnelPrefix setting "' + NorNet_Configuration['NorNet_IPv4TunnelPrefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv4TunnelPrefix'].network.prefixlen > 16:
      error('NorNet_IPv4TunnelPrefix must be at least a /16 network!')

   try:
      NorNet_Configuration['NorNet_IPv6TunnelPrefix'] = IPv6Interface(NorNet_Configuration['NorNet_IPv6TunnelPrefix'])
   except Exception as e:
      error('NorNet_IPv6TunnelPrefix setting "' + NorNet_Configuration['NorNet_IPv6TunnelPrefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv6TunnelPrefix'].network.prefixlen > 80:
      error('NorNet_IPv6TunnelPrefix must be at least a /80 network!')

   if includeAPIConfiguration == True:
      if NorNet_Configuration['NorNetPLC_Address'] == None:
         error('NorNetPLC_Address has not been set in configuration file!')
      if NorNet_Configuration['NorNetPLC_User'] == None:
         error('NorNetPLC_User has not been set in configuration file!')
      if NorNet_Configuration['NorNetPLC_Password'] == None:
         error('NorNetPLC_Password has not been set in configuration file!')
      if NorNet_Configuration['NorNet_CentralSite_DomainName'] == None:
         error('NorNet_CentralSite_DomainName has not been set!')

      try:
         user = pwd.getpwnam(getLocalNodeNorNetUser())
      except Exception as e:
         error('NorNet_LocalNode_NorNetUser has invalid user "' + str(getLocalNodeNorNetUser()) + '": ' + str(e))

      if NorNet_Configuration['NorNet_CentralSite_BootstrapTunnelbox'] != None:
         try:
            NorNet_Configuration['NorNet_CentralSite_BootstrapTunnelbox'] = IPv4Address(NorNet_Configuration['NorNet_CentralSite_BootstrapTunnelbox'])
         except Exception as e:
            error('NorNet_IPv4Prefix NorNet_CentralSite_BootstrapTunnelbox "' + NorNet_Configuration['NorNet_CentralSite_BootstrapTunnelbox'] + ' is invalid: ' + str(e))

      if NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'] != None:
         try:
            NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'] = int(NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'])
         except Exception as e:
            error('NorNet_IPv4Prefix NorNet_CentralSite_BootstrapProviderIndex "' + NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'] + ' is invalid: ' + str(e))
         if ((NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'] < NorNet_MinSiteIndex) or
             (NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'] > NorNet_MaxSiteIndex)):
            error('NorNet_IPv4Prefix NorNet_CentralSite_BootstrapProviderIndex must be in [' + str(NorNet_MinSiteIndex) + '-' + str(NorNet_MaxSiteIndex) + ']!')

      if NorNet_Configuration['NorNet_LocalSite_SiteIndex'] != None:
         try:
            NorNet_Configuration['NorNet_LocalSite_SiteIndex'] = int(NorNet_Configuration['NorNet_LocalSite_SiteIndex'])
         except Exception as e:
            error('NorNet_IPv4Prefix NorNet_LocalSite_SiteIndex "' + NorNet_Configuration['NorNet_LocalSite_SiteIndex'] + ' is invalid: ' + str(e))
         if ((NorNet_Configuration['NorNet_LocalSite_SiteIndex'] < NorNet_MinSiteIndex) or
               (NorNet_Configuration['NorNet_LocalSite_SiteIndex'] > NorNet_MaxSiteIndex)):
            error('NorNet_IPv4Prefix NorNet_LocalSite_SiteIndex must be in [' + str(NorNet_MinSiteIndex) + '-' + str(NorNet_MaxSiteIndex) + ']!')

      if NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] != None:
         try:
            NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] = int(NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'])
         except Exception as e:
            error('NorNet_IPv4Prefix NorNet_LocalSite_DefaultProviderIndex "' + NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] + ' is invalid: ' + str(e))
         if ((NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] < NorNet_MinProviderIndex) or
               (NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] > NorNet_MaxProviderIndex)):
            error('NorNet_IPv4Prefix NorNet_LocalSite_DefaultProviderIndex must be in [' + str(NorNet_MinProviderIndex) + '-' + str(NorNet_MaxProviderIndex) + ']!')

      if isinstance(NorNet_Configuration['NorNet_LocalNode_ControlBox'], str):
         if NorNet_Configuration['NorNet_LocalNode_ControlBox'] == 'yes':
            NorNet_Configuration['NorNet_LocalNode_ControlBox'] = True
         elif NorNet_Configuration['NorNet_LocalNode_ControlBox'] == 'no':
            NorNet_Configuration['NorNet_LocalNode_ControlBox'] = False
      if not isinstance(NorNet_Configuration['NorNet_LocalNode_ControlBox'], bool):
            error('NorNet_IPv4Prefix NorNet_LocalNode_ControlBox must be "yes" or "no"!')

      if NorNet_Configuration['NorNet_LocalNode_Index'] != None:
         try:
            NorNet_Configuration['NorNet_LocalNode_Index'] = int(NorNet_Configuration['NorNet_LocalNode_Index'])
         except Exception as e:
            error('NorNet_IPv4Prefix NorNet_LocalNode_Index "' + NorNet_Configuration['NorNet_LocalNode_Index'] + ' is invalid: ' + str(e))
         if ((NorNet_Configuration['NorNet_LocalNode_Index'] < NorNet_MinNodeIndex) or
               (NorNet_Configuration['NorNet_LocalNode_Index'] > NorNet_MaxNodeIndex)):
            error('NorNet_IPv4Prefix NorNet_LocalNode_Index must be in [' + str(NorNet_MinNodeIndex) + '-' + str(NorNet_MinNodeIndex) + ']!')

      if NorNet_Configuration['NorNet_Slice_NodeIndexRange'] != None:
         try:
            NorNet_Configuration['NorNet_Slice_NodeIndexRange'] = \
               parseNumberSetFromRangesString(NorNet_Configuration['NorNet_Slice_NodeIndexRange'],
                                              NorNet_MinSliceIndex, NorNet_MaxSliceIndex)
            # print(NorNet_Configuration['NorNet_Slice_NodeIndexRange'])
         except Exception as e:
            error('Bad configuration "' + NorNet_Configuration['NorNet_Slice_NodeIndexRange'] + '" for NorNet_Slice_NodeIndexRange: ' + str(e))


# ###### Get central site's domain name #####################################
def getCentralSiteDomainName():
   return NorNet_Configuration['NorNet_CentralSite_DomainName']


# ###### Get central site's bootstrap tunnelbox address (IPv4) ##############
def getCentralSiteBootstrapTunnelbox():
   return NorNet_Configuration['NorNet_CentralSite_BootstrapTunnelbox']


# ###### Get central site's bootstrap provider index ########################
def getCentralSiteBootstrapProviderIndex():
   return NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex']


# ###### Get local Site Index ###############################################
def getLocalSiteIndex():
   return NorNet_Configuration['NorNet_LocalSite_SiteIndex']


# ###### Get local Default Provider Index ###################################
def getLocalSiteDefaultProviderIndex():
   return NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex']


# ###### Get local tunnelbox's outer IPv4 address ###########################
def getLocalSiteTunnelboxDefaultProviderIPv4():
   return NorNet_Configuration['NorNet_LocalSite_TBDefaultProviderIPv4']


# ###### Get local node index ###############################################
def getLocalNodeIndex():
   return NorNet_Configuration['NorNet_LocalNode_Index']


# ###### Get local node hostname ############################################
def getLocalNodeHostname():
   return NorNet_Configuration['NorNet_LocalNode_Hostname']


# ###### Get NorNet interface name ##########################################
def getLocalNodeNorNetInterface():
   return NorNet_Configuration['NorNet_LocalNode_NorNetInterface']


# ###### Get NorNet interface match string ##################################
def getLocalNodeNorNetInterfaceMatch():
   return NorNet_Configuration['NorNet_LocalNode_NorNetInterfaceMatch']


# ###### Get local node NorNet user #########################################
def getLocalNodeNorNetUser():
   return NorNet_Configuration['NorNet_LocalNode_NorNetUser']


# ###### Get NorNet provider information ####################################
def getNorNetProviderInfo(providerIndex):
   try:
      return NorNet_ProviderList[providerIndex]
   except:
      return NorNet_ProviderList[0]
