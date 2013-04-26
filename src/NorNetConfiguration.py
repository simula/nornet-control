#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet PLC Configuration
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
#import getpass;


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
   'NorNet_LocalNode_NorNetUser'               : 'nornetpp',
   'NorNet_LocalNode_NorNetInterface'          : None,

   'NorNet_Provider0'                          : '"UNKNOWN" "unknown" ""'
}

# The provider list
NorNet_ProviderList = { }

# ===========================================================================

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!! WARNING: Do not change unless you really know what you are doing! !!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# TOS Settings for provider selection
NorNet_TOSSettings = [ 0x00, 0x04, 0x08, 0x0C, 0x10, 0x14, 0x18, 0x1C ]

# Maximum number of external NTP servers
NorNet_MaxNTPServers = 8

# Maximum number of providers per site
NorNet_MaxProviders = 8

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

# ===========================================================================



# ###### Read configuration file ############################################
def loadNorNetConfiguration():
   sys.stdout = codecs.getwriter('utf8')(sys.stdout)
   sys.stderr = codecs.getwriter('utf8')(sys.stderr)
   sys.stdin  = codecs.getreader('utf8')(sys.stdin)

   # ====== Open constants file =============================================
   log('Reading constants from ' + NorNetPLC_ConfigFile + ' ...')   
   try:
      constantsFile = codecs.open(NorNetPLC_ConstantsFile, 'r', 'utf-8')
   except:
      try:
         log('###### Cannot open ' + NorNetPLC_ConstantsFile + ', trying fallback file ' + NorNetPLC_FallbackConstantsFile + ' ... ######')
         constantsFile = codecs.open(NorNetPLC_FallbackConstantsFile, 'r', 'utf-8')

      except Exception as e:
         error('Constantsuration file ' + NorNetPLC_FallbackConstantsFile + ' cannot be read: ' + str(e))
   
   # ====== Open configuration file =========================================
   log('Reading configuration from ' + NorNetPLC_ConfigFile + ' ...')   
   try:
      configFile = codecs.open(NorNetPLC_ConfigFile, 'r', 'utf-8')
   except:
      try:
         log('###### Cannot open ' + NorNetPLC_ConfigFile + ', trying fallback file ' + NorNetPLC_FallbackConfigFile + ' ... ######')
         configFile = codecs.open(NorNetPLC_FallbackConfigFile, 'r', 'utf-8')

      except Exception as e:
         error('Configuration file ' + NorNetPLC_FallbackConfigFile + ' cannot be read: ' + str(e))


   # ====== Build the configuration table ===================================
   lines = tuple(constantsFile) + tuple(configFile)
   for line in lines:
      if re.match('^[ \t]*[#\n]', line):
         continue
      elif re.match('^[a-zA-Z0-9_]*[ \t]*=', line):
         s = re.split('=',line,1)
         parameterName = s[0]
         parameterValue = unquote(removeComment(s[1].rstrip('\n')))
         NorNet_Configuration[parameterName] = parameterValue
         # print '<' + parameterName + '> = <' + parameterValue + '>'
      else:
         error('Bad configuration line: ' + line)


   # ====== Build provider table ============================================
   for providerIndex in range(0,256):
      try:
         provider = re.split(r'''[ ]*(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', NorNet_Configuration['NorNet_Provider' + str(providerIndex)])
      except:
         provider = None
      if provider != None:
         if len(provider) < 3:
            error('Bad configuration "' + NorNet_Configuration['NorNet_Provider' + str(providerIndex)] + '" for NorNet_Provider' + str(providerIndex))

         providerLongName  = unquote(provider[0])
         providerShortName = makeNameFromUnicode(unquote(provider[1]))['ascii']
         providerURL       = unquote(provider[2])
         
         NorNet_ProviderList[providerIndex] = [ providerLongName, providerShortName, providerURL ]


   # ====== Check some important contents ===================================
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
      
   try:
      NorNet_Configuration['NorNet_IPv4Prefix'] = IPv4Network(NorNet_Configuration['NorNet_IPv4Prefix'])
   except Exception as e:
      error('NorNet_IPv4Prefix setting "' + NorNet_Configuration['NorNet_IPv4Prefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv4Prefix'].prefixlen > 8:
      error('NorNet_IPv4Prefix must be at least a /8 network!')

   try:
      NorNet_Configuration['NorNet_IPv6Prefix'] = IPv6Network(NorNet_Configuration['NorNet_IPv6Prefix'])
   except Exception as e:
      error('NorNet_IPv6Prefix setting "' + NorNet_Configuration['NorNet_IPv6Prefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv6Prefix'].prefixlen > 48:
      error('NorNet_IPv6Prefix must be at least a /48 network!')

   try:
      NorNet_Configuration['NorNet_IPv4TunnelPrefix'] = IPv4Network(NorNet_Configuration['NorNet_IPv4TunnelPrefix'])
   except Exception as e:
      error('NorNet_IPv4TunnelPrefix setting "' + NorNet_Configuration['NorNet_IPv4TunnelPrefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv4TunnelPrefix'].prefixlen > 16:
      error('NorNet_IPv4TunnelPrefix must be at least a /16 network!')

   try:
      NorNet_Configuration['NorNet_IPv6TunnelPrefix'] = IPv6Network(NorNet_Configuration['NorNet_IPv6TunnelPrefix'])
   except Exception as e:
      error('NorNet_IPv6TunnelPrefix setting "' + NorNet_Configuration['NorNet_IPv6TunnelPrefix'] + ' is invalid: ' + str(e))
   if NorNet_Configuration['NorNet_IPv6TunnelPrefix'].prefixlen > 72:
      error('NorNet_IPv6TunnelPrefix must be at least a /72 network!')

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
      if ((NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'] < 1) or
          (NorNet_Configuration['NorNet_CentralSite_BootstrapProviderIndex'] > 255)):
         error('NorNet_IPv4Prefix NorNet_CentralSite_BootstrapProviderIndex must be in [1,255]!')

   if NorNet_Configuration['NorNet_LocalSite_SiteIndex'] != None:
      try:
         NorNet_Configuration['NorNet_LocalSite_SiteIndex'] = int(NorNet_Configuration['NorNet_LocalSite_SiteIndex'])
      except Exception as e:
         error('NorNet_IPv4Prefix NorNet_LocalSite_SiteIndex "' + NorNet_Configuration['NorNet_LocalSite_SiteIndex'] + ' is invalid: ' + str(e))
      if ((NorNet_Configuration['NorNet_LocalSite_SiteIndex'] < 1) or
            (NorNet_Configuration['NorNet_LocalSite_SiteIndex'] > 255)):
         error('NorNet_IPv4Prefix NorNet_LocalSite_SiteIndex must be in [1,255]!')
      
   if NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] != None:
      try:
         NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] = int(NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'])
      except Exception as e:
         error('NorNet_IPv4Prefix NorNet_LocalSite_DefaultProviderIndex "' + NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] + ' is invalid: ' + str(e))
      if ((NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] < 1) or
            (NorNet_Configuration['NorNet_LocalSite_DefaultProviderIndex'] > 255)):
         error('NorNet_IPv4Prefix NorNet_LocalSite_DefaultProviderIndex must be in [1,255]!')

   if NorNet_Configuration['NorNet_LocalNode_Index'] != None:
      try:
         NorNet_Configuration['NorNet_LocalNode_Index'] = int(NorNet_Configuration['NorNet_LocalNode_Index'])
      except Exception as e:
         error('NorNet_IPv4Prefix NorNet_LocalNode_Index "' + NorNet_Configuration['NorNet_LocalNode_Index'] + ' is invalid: ' + str(e))
      if ((NorNet_Configuration['NorNet_LocalNode_Index'] < 1) or
            (NorNet_Configuration['NorNet_LocalNode_Index'] > 255)):
         error('NorNet_IPv4Prefix NorNet_LocalNode_Index must be in [1,255]!')


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


# ###### Get local node hostname ############################################
def getLocalNodeNorNetInterface():
   return NorNet_Configuration['NorNet_LocalNode_NorNetInterface']


# ###### Get local node NorNet user #########################################
def getLocalNodeNorNetUser():
   return NorNet_Configuration['NorNet_LocalNode_NorNetUser']


# ###### Get NorNet provider information ####################################
def getNorNetProviderInfo(providerIndex):
   try:
      return NorNet_ProviderList[providerIndex]
   except:
      return NorNet_ProviderList[0]
