#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet Node Setup
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
import re;
import hashlib;
import datetime;
import codecs;

# Needs package python-ipaddr (Fedora Core, Ubuntu, Debian)!
from ipaddr import IPAddress, IPNetwork, IPv4Address, IPv4Network, IPv6Address, IPv6Network;

# NorNet
from NorNetTools         import *;
from NorNetAPI           import *;
from NorNetProviderSetup import *;


# ###### Generate provider configuration ####################################
def makeProviderConfiguration():
   configurationName = 'provider-config'
   outputFile = makeConfigFile('provider', configurationName, True)

   providers         = 0
   providerIndexSet  = []
   providerAbbrevSet = []
   for providerIndex in NorNet_ProviderList:
      providerName   = NorNet_ProviderList[providerIndex][0]
      providerAbbrev = NorNet_ProviderList[providerIndex][1]
      if not re.match(r"^[a-z][a-z0-9]*$", providerAbbrev):
         error('Bad provider abbreviation ' + providerAbbrev)
      if ((providerIndex < 0) or (providerIndex > 255)):
         error('Bad provider index ' + str(providerIndex))

      outputFile.write('provider' + str(providerIndex) + '_longname="'  + providerName   + '"\n')
      outputFile.write('provider' + str(providerIndex) + '_shortname="' + providerAbbrev + '"\n')
      outputFile.write('nnp_' + providerAbbrev + '=' + str(providerIndex) + '\n\n')

      providerIndexSet.append(providerIndex)
      providerAbbrevSet.append(providerAbbrev)
      providers=providers+1

   if len(providerIndexSet) != len(set(providerIndexSet)):
      error('Provider list contains non-unqiue index values')
   if len(providerAbbrevSet) != len(set(providerAbbrevSet)):
      error('Provider list contains non-unqiue abbreviation values')

   outputFile.close()
   return configurationName


# ###### Generate site configuration ########################################
def makeSiteConfiguration(fullSiteList, site, v4only):
   configurationName = 'site-' + site['site_short_name'] + '-config'
   outputFile = makeConfigFile('Site', configurationName, True)

   log('Making site configuration for ' + site['site_long_name'] + ' ...')

   siteIndex        = site['site_index']
   siteShortName    = str.lower(site['site_short_name'])
   siteProviderList = getNorNetProvidersForSite(site)
   defProvTbIPv4    = None
   for providerIndex in siteProviderList:
      provider            = siteProviderList[providerIndex]
      providerShortName   = provider['provider_short_name']
      providerNetworkIPv4 = makeNorNetIP(providerIndex, siteIndex, 0, 0, 4)
      providerNetworkIPv6 = makeNorNetIP(providerIndex, siteIndex, 0, 0, 6)
      outputFile.write(siteShortName + '_' + providerShortName + '_network_ipv4="' + str(providerNetworkIPv4) + '"\n')
      outputFile.write(siteShortName + '_' + providerShortName + '_network_ipv6="' + str(providerNetworkIPv6) + '"\n')
      if providerIndex == site['site_default_provider_index']:
         defProvTbIPv4 = provider['provider_tunnelbox_ipv4']

   if defProvTbIPv4 == None:
     error('Tunnelbox address of default provider has not been defined?!')

   makeTunnelBoxConfiguration(fullSiteList, site, None, v4only)
   makeTunnelboxBootstrap(siteIndex, site['site_default_provider_index'],
                          'xxxxx', defProvTbIPv4,
                          'tunnelbox-' +  site['site_short_name'])

   outputFile.close()
   return configurationName


# ###### Generate sites configuration #######################################
def makeNorNetConfiguration(v4only):
   configurationName = 'nornet-config'
   outputFile = makeConfigFile('nornet', configurationName, True)

   providerConfigurationName = makeProviderConfiguration()
   outputFile.write('. ./' + providerConfigurationName + '\n\n')

   fullSiteList = fetchNorNetSiteList()

   for localSiteIndex in fullSiteList:
      localSite = fullSiteList[localSiteIndex]

      siteConfigurationName = makeSiteConfiguration(fullSiteList, localSite, v4only)
      outputFile.write('. ./' + siteConfigurationName + '\n')

   outputFile.close()
   return configurationName


# ###### Get tunnel configuration ###########################################
def _getTunnel(localSite, localProvider, remoteSite, remoteProvider, version):
   localSiteIndex      = localSite['site_index']
   localProviderIndex  = localProvider['provider_index']
   remoteProviderIndex = remoteProvider['provider_index']
   remoteSiteIndex     = remoteSite['site_index']

   # ====== Get tunnel configuration ========================================
   tunnelOverIPv4 = False
   if (version != 4):
      localOuterAddress  = localProvider['provider_tunnelbox_ipv6']
      remoteOuterAddress = remoteProvider['provider_tunnelbox_ipv6']
      if ((localOuterAddress == IPv6Address('::')) or (remoteOuterAddress == IPv6Address('::'))):
         tunnelOverIPv4 = True
      else:
         tunnelInterface = 'seks' + str(remoteSiteIndex) + "-" + str(localProviderIndex) + '-' + str(remoteProviderIndex)
   if ((version == 4) or (tunnelOverIPv4 == True)):
      localOuterAddress  = localProvider['provider_tunnelbox_ipv4']
      remoteOuterAddress = remoteProvider['provider_tunnelbox_ipv4']
      tunnelInterface    = 'gre' + str(remoteSiteIndex) + "-" + str(localProviderIndex) + '-' + str(remoteProviderIndex)
   localInnerAddress     =  makeNorNetTunnelIP(localSiteIndex, localProviderIndex,
                                               remoteSiteIndex, remoteProviderIndex, version)
   remoteInnerAddress    =  makeNorNetTunnelIP(remoteSiteIndex, remoteProviderIndex,
                                               localSiteIndex, localProviderIndex, version)
   tunnelKey = makeNorNetTunnelKey(localSiteIndex, localProviderIndex,
                                   remoteSiteIndex, remoteProviderIndex)

   # ====== Create tunnel structure =========================================
   norNetTunnel = {
      'tunnel_interface'            : tunnelInterface,
      'tunnel_local_outer_address'  : localOuterAddress,
      'tunnel_remote_outer_address' : remoteOuterAddress,
      'tunnel_local_inner_address'  : localInnerAddress,
      'tunnel_remote_inner_address' : remoteInnerAddress,
      'tunnel_key'                  : tunnelKey,
      'tunnel_over_ipv4'            : tunnelOverIPv4
   }

   return norNetTunnel


# ###### Get tunnel configuration for default tunnel to central site ########
def _getDefaultTunnel(fullSiteList, localSite, version):
   localSiteProviders          = getNorNetProvidersForSite(localSite)
   localDefaultProviderIndex   = localSite['site_default_provider_index']

   centralSite                 = fullSiteList[NorNet_SiteIndex_Central]
   centralSiteProviders        = getNorNetProvidersForSite(centralSite)
   centralDefaultProviderIndex = centralSite['site_default_provider_index']

   return _getTunnel(localSite, localSiteProviders[localDefaultProviderIndex],
                     centralSite, centralSiteProviders[centralDefaultProviderIndex],
                     version)


# ###### Get ID for routing table ###########################################
def _getTableID(opIndex):
   return 1000000 + opIndex


# ###### Get preference for routing table ###################################
def _getTablePref(opIndex, level):
   return 1000 + (1000 * level) + opIndex


# ###### Make IPv6 link-local address for GRE tunnel ########################
def _makeGRELinkLocal(a, b):
   result = IPv6Network('fe80::' + \
                        str.replace(hex((int(a) >> 16) & 0xffff), '0x', '') + ':' + \
                        str.replace(hex(int(a) & 0xffff),         '0x', '') + ':' + \
                        str.replace(hex((int(b) >> 16) & 0xffff), '0x', '') + ':' + \
                        str.replace(hex(int(b) & 0xffff),         '0x', '') + \
                        '/64')
   return(result)


# ###### Generate tunnelbox configuration for given provider ################
def _makeTunnelboxProvider(fullSiteList, localSite, localProviderList, localProvider, pathNumber, configNamePrefix, v4only):
   if configNamePrefix == None:
      configNamePrefix = 'tunnelbox-' + localSite['site_short_name']
   configurationName = configNamePrefix + '-' + localProvider['provider_short_name'] + '-config'
   outputFile = makeConfigFile('Tunnelbox-Provider', configurationName, True)
   log('Making tunnelbox provider configuration for ' + \
       localSite['site_long_name'] + '/' + localProvider['provider_long_name'] + ' ...')

   localSiteIndex     = localSite['site_index']
   localProviderIndex = localProvider['provider_index']
   stateList          = [ 'stop', 'start', 'status' ]
   for state in stateList:
      if ((state == 'start') or (state == 'stop')):
         outputFile.write('if [ "$state" = "' + state + '" -o "$state" = "restart" ] ; then\n')
         if state == 'start':
            outputFile.write('   if [ "$state" = "restart" ] ; then\n')
            outputFile.write('      log-summary\n')
            outputFile.write('   fi\n')
      else:
         outputFile.write('if [ "$state" = "' + state + '" ] ; then\n')

      # ====== Create provider-specific routing table =======================
      action = ''
      if (state == 'start'):
         action = 'Setting up'
      elif (state == 'stop'):
         action = 'Tearing down'
      elif (state == 'status'):
         action = 'Checking'
      outputFile.write('   log "' + action + ' connectivity for provider ' + \
                       localProvider['provider_long_name'] + ' ..."\n')

      routingTableID         = _getTableID(localProviderIndex)
      routingTableDestPref   = _getTablePref(localProviderIndex, 0)
      routingTableTOSPref    = _getTablePref(localProviderIndex, 1)
      routingTableSourcePref = _getTablePref(localProviderIndex, 2)

      if (state == 'start'):
         if pathNumber + 1 < len(NorNet_TOSSettings):
            routingTableTOS = NorNet_TOSSettings[pathNumber + 1]
         else:
            routingTableTOS = 0x00

         outputFile.write('   log-action "Creating rules and tables for provider ' + \
                          localProvider['provider_long_name'] + ' ..."\n')
         outputFile.write('   make-table ' + str(routingTableID) + '   # ' + \
                          localProvider['provider_long_name'] + ' table   && \\\n')

         # ====== Destination rules =========================================
         # For directly connected NorNet networks, skip further rules and go
         # to "main" table instead!
         providerList = getNorNetProvidersForSite(localSite)
         for version in [ 4, 6 ]:
            if ((version == 6) and (v4only == True)):
               continue
            fullNorNetNetwork    = makeNorNetIP(0, 0, 0, 0, version)
            localProviderNetwork = makeNorNetIP(localProviderIndex, localSiteIndex, 0, 0, version)
            outputFile.write('   add-table-selector main ' + str(routingTableDestPref) + \
                             ' to ' + str(localProviderNetwork) + '   && \\\n')

            # ====== TOS rule ===============================================
            # If TOS is set, select outgoing provider accordingly
            if routingTableTOS != 0x00:
               outputFile.write('   add-table-selector ' + str(routingTableID) + ' ' + str(routingTableTOSPref) + \
                                ' from ' + str(fullNorNetNetwork) + \
                                ' tos ' + hex(routingTableTOS) + \
                                ' to ' + str(fullNorNetNetwork) + '   && \\\n')

         # ====== Source rules ==============================================
         # Otherwise, use source address to determine the outgoing provider.
         for version in [ 4, 6 ]:
            if ((version == 6) and (v4only == True)):
               continue
            fullNorNetNetwork    = makeNorNetIP(0, 0, 0, 0, version)
            localProviderNetwork = makeNorNetIP(localProviderIndex, 0, 0, 0, version)
            outputFile.write('   add-table-selector ' + str(routingTableID) + ' ' + str(routingTableSourcePref) + \
                             ' from ' + str(localProviderNetwork) + \
                             ' to ' + str(fullNorNetNetwork) + '   && \\\n')

      elif (state == 'stop'):
         outputFile.write('   log-action "Removing rules and tables for provider ' + \
                          localProvider['provider_long_name'] + ' ..."\n')
         outputFile.write('   remove-table ' + str(routingTableID) + '   && \\\n')
         for version in [ 4, 6 ]:
            if ((version == 6) and (v4only == True)):
               continue
            localProviderNetwork = makeNorNetIP(localProviderIndex, localSiteIndex, 0, 0, version)
            outputFile.write('   remove-table-selector main ' + str(routingTableDestPref) + \
                             ' to ' + str(localProviderNetwork) + '   && \\\n')

      if ((state == 'start') or (state == 'stop')):
         outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')


      # ====== Create provider-specific tunnels and routes ==================
      for remoteSiteIndex in fullSiteList:
         if remoteSiteIndex == localSiteIndex:
            continue
         remoteSite         = fullSiteList[remoteSiteIndex]
         remoteProviderList = getNorNetProvidersForSite(remoteSite)
         outputFile.write('   # ------ ' + localSite['site_long_name'] + \
                          ' (' + str(localSite['site_index']) + ') <-> ' + \
                          remoteSite['site_long_name'] + \
                          ' (' + str(remoteSite['site_index']) + ') ------\n')

         for remoteProviderIndex in remoteProviderList:
            remoteProvider = remoteProviderList[remoteProviderIndex]
            outputFile.write('   # ~~~~~~ ' + remoteProvider['provider_long_name'] + \
                             ' (' + str(remoteProvider['provider_index']) + ') ~~~~~~\n')
            if ((state == 'start') or (state == 'stop') or (state == 'status')):
               outputFile.write('   log "' + action + ' tunnels with ' + \
                                remoteSite['site_long_name'] + ' via [' + \
                                localProvider['provider_long_name'] + ' <--> ' + \
                                remoteProvider['provider_long_name'] + ']:"\n')

            for version in [ 4, 6 ]:
               if ((version == 6) and (v4only == True)):
                  continue
               tunnel        = _getTunnel(localSite, localProvider, remoteSite, remoteProvider, version)
               remoteNetwork = makeNorNetIP(remoteProviderIndex, remoteSiteIndex, 0, 0, version)

               outputFile.write('   log-action "Tunnel ' + tunnel['tunnel_interface'] + ': ' + \
                                str(tunnel['tunnel_local_inner_address'])  + ' <--> ' + \
                                str(tunnel['tunnel_remote_inner_address']) + '"\n')

               # ====== Create tunnels ======================================
               if (state == 'start'):
                  options = ''
                  if ((version == 6) and (tunnel['tunnel_over_ipv4'] == True)):
                     options = '--add-to-existing-tunnel'
                  elif ((v4only == False) and (version == 4) and (re.match('^gre', tunnel['tunnel_interface']))):
                     options = '--v6-linklocal ' + str(_makeGRELinkLocal(tunnel['tunnel_local_outer_address'],
                                                                         tunnel['tunnel_remote_outer_address']))
                  outputFile.write('   make-tunnel ' + \
                                   tunnel['tunnel_interface']                 + ' ' + \
                                   hex(tunnel['tunnel_key'])                  + ' ' + \
                                   str(tunnel['tunnel_local_outer_address'])  + ' ' + \
                                   str(tunnel['tunnel_remote_outer_address']) + ' ' + \
                                   str(tunnel['tunnel_local_inner_address'])  + ' ' + \
                                   str(tunnel['tunnel_remote_inner_address']) + ' ' + \
                                   '"' + options + '" && \\\n')
               elif (state == 'stop'):
                  if not ((version == 6) and (tunnel['tunnel_over_ipv4'] == True)):
                     outputFile.write('   remove-tunnel ' + \
                                      tunnel['tunnel_interface'] + ' ' + \
                                      hex(tunnel['tunnel_key'])  + '   && \\\n')
               elif (state == 'status'):
                  outputFile.write('   show-tunnel ' + \
                                   tunnel['tunnel_interface'] + ' ' + \
                                   str(tunnel['tunnel_local_inner_address']) + ' ' + \
                                   str(tunnel['tunnel_remote_inner_address']) + ' "' + \
                                   localSite['site_long_name'] + \
                                   str(localSite['site_index']) + ' <-> ' + \
                                   remoteSite['site_long_name'] + \
                                   ' (' + str(remoteSite['site_index']) + ') via [' + \
                                   remoteProvider['provider_long_name'] + \
                                   ' (' + str(remoteProvider['provider_index']) + ') <--> ' + \
                                   localProvider['provider_long_name'] + \
                                   ' (' + str(localProvider['provider_index']) + ')]"   && \\\n')


               # ====== Create routing table entries ========================
               if (state == 'start'):
                  # ====== Entry into provider-specific routing table =======
                  outputFile.write('   make-route ' + \
                                   str(routingTableID) + ' ' +
                                   str(remoteNetwork) + ' ' +
                                   tunnel['tunnel_interface'] + ' ' + \
                                   str(tunnel['tunnel_remote_inner_address']) + '   && \\\n')

                  # ====== Entry into global routing table ==================
                  metric = 10 + pathNumber
                  if remoteProviderIndex == localProviderIndex:
                     metric = 5
                  outputFile.write('   make-route ' + \
                                   'main ' +
                                   str(remoteNetwork) + ' ' +
                                   tunnel['tunnel_interface'] + ' ' + \
                                   str(tunnel['tunnel_remote_inner_address']) + ' ' + \
                                   'metric ' + str(metric) + '   && \\\n')

               outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')


      ## ====== Default route to central site ================================
      if ((localSiteIndex != NorNet_SiteIndex_Central) and
          (localProviderIndex == localSite['site_default_provider_index'])):
         routingTableID       = _getTableID(256)
         routingTableDestPref = _getTablePref(256, 4)
         if (state == 'start'):
            outputFile.write('   log "Setting up DEFAULT route to central site"\n')
            outputFile.write('   make-table ' + str(routingTableID) + '   # DEFAULT to CENTRAL SITE\n')
            for version in [ 4, 6 ]:
               if ((version == 6) and (v4only == True)):
                  continue
               defaultTunnel     = _getDefaultTunnel(fullSiteList, localSite, version)
               fullNorNetNetwork = makeNorNetIP(0, 0, 0, 0, version)

               outputFile.write('   add-table-selector ' + str(routingTableID) + ' ' + str(routingTableDestPref) + \
                                ' from ' + str(fullNorNetNetwork) + '\n')
               outputFile.write('   make-route ' + \
                                str(routingTableID) + ' ' +
                                'default ' +
                                defaultTunnel['tunnel_interface'] + ' ' + \
                                str(defaultTunnel['tunnel_remote_inner_address']) + '\n')

         elif (state == 'stop'):
            outputFile.write('   log "Tearing down DEFAULT route to central site"\n')
            outputFile.write('   remove-table ' + str(routingTableID) + '\n')


      outputFile.write('   log-action "' + action + ' connectivity for provider ' + \
                       localProvider['provider_long_name'] + ' finished"\n')

      outputFile.write('fi\n\n')
      pathNumber = pathNumber + 1


   outputFile.write('log-summary-and-return-result\n')
   pathNumber = pathNumber + 1

   outputFile.close()
   return configurationName


# ###### Generate tunnelbox configuration for local network #################
def _makeTunnelboxNetwork(outputFile, state, localInterface,
                          localProvider, localSiteIndex, v4only):
   localProviderIndex = localProvider['provider_index']

   action = ''
   if (state == 'start'):
      action = 'Setting up'
   elif (state == 'stop'):
      action = 'Tearing down'
   outputFile.write('\n      log-action "' + action + ' local networks for ' + \
                    localProvider['provider_long_name'] + ' ..."\n')

   for version in [ 4, 6 ]:
      if ((version == 6) and (v4only == True)):
         continue

      localAddress = makeNorNetIP(localProviderIndex, localSiteIndex, NorNet_NodeIndex_Tunnelbox, -1, version)
      if state == 'start':
         outputFile.write('      make-address ' + localInterface + ' ' + str(localAddress) + '   && \\\n')
      elif state == 'stop':
         outputFile.write('      remove-address ' + localInterface + ' ' + str(localAddress) + '   && \\\n')

   outputFile.write('      log-result $RESULT_GOOD || log-result $RESULT_BAD\n')


# ###### Generate tunnelbox bootstrap configuration for local network #######
def makeTunnelboxBootstrap(localSiteIndex, localProviderIndex, localInterface, localAddress, configNamePrefix):
   localSite = {
      'site_index'              : localSiteIndex,
      'site_long_name'          : 'My Site',
      'site_short_name'         : 'MS'
   }
   localProvider = {
      'provider_index'          : localProviderIndex,
      'provider_long_name'      : 'Local Provider',
      'provider_short_name'     : 'local',
      'provider_tunnelbox_ipv4' : localAddress
   }
   remoteSite = {
      'site_index'              : NorNet_SiteIndex_Central,
      'site_long_name'          : 'Central Site',
      'site_short_name'         : 'NN'
   }
   remoteProvider = {
      'provider_index'          : NorNet_CentralSite_BootstrapProviderIndex,
      'provider_long_name'      : 'Local Provider',
      'provider_short_name'     : 'local',
      'provider_tunnelbox_ipv4' : NorNet_CentralSite_BootstrapTunnelbox
   }

   if configNamePrefix == None:
      configNamePrefix = 'tunnelbox-' + localSite['site_short_name']
   configurationName = configNamePrefix + '-bootstrap'
   outputFile = makeConfigFile('Tunnelbox', configurationName, True)
   log('Making tunnelbox bootstrap for site ' + str(localSiteIndex) + ' ...')


   # ====== Non-Central Site tunnelbox ======================================
   if localSiteIndex != NorNet_SiteIndex_Central:
      tunnel         = _getTunnel(localSite, localProvider, remoteSite, remoteProvider, 4)
      remoteNetwork  = makeNorNetIP(remoteProvider['provider_index'], remoteSite['site_index'], 0, 0, 4)
      interfaceToPLC = tunnel['tunnel_interface']

      outputFile.write('\nif [ "$state" = "stop" -o "$state" = "restart" ] ; then\n')
      outputFile.write('   log-action "Tearing down tunnel to central site ..."\n')
      outputFile.write('   remove-tunnel ' + \
                       tunnel['tunnel_interface'] + ' ' + \
                       hex(tunnel['tunnel_key'])  + '   && \\\n')
      outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
      outputFile.write('fi\n')

      outputFile.write('\nif [ "$state" = "start" -o "$state" = "restart" ] ; then\n')
      outputFile.write('   log-action "Setting up tunnel to central site ..."\n')
      outputFile.write('   make-tunnel ' + \
                       tunnel['tunnel_interface']                 + ' ' + \
                       hex(tunnel['tunnel_key'])                  + ' ' + \
                       str(tunnel['tunnel_local_outer_address'])  + ' ' + \
                       str(tunnel['tunnel_remote_outer_address']) + ' ' + \
                       str(tunnel['tunnel_local_inner_address'])  + ' ' + \
                       str(tunnel['tunnel_remote_inner_address']) + '  && \\\n')
      outputFile.write('   make-route main ' + \
                       str(remoteNetwork) + ' ' +
                       tunnel['tunnel_interface'] + ' ' + \
                       str(tunnel['tunnel_remote_inner_address']) + ' ' + \
                       'metric 5   && \\\n')
      outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
      outputFile.write('fi\n')

   # ====== Central-Site tunnelbox ==========================================
   else:
      interfaceToPLC = localInterface
      outputFile.write('\nif [ "$state" = "stop" -o "$state" = "restart" ] ; then\n')
      for version in [ 4, 6 ]:
         localAddress = makeNorNetIP(localProviderIndex, localSiteIndex, NorNet_NodeIndex_Tunnelbox, -1, version)
         outputFile.write('   remove-address ' + localInterface + ' ' + str(localAddress) + '   && \\\n')
      outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
      outputFile.write('fi\n')
      outputFile.write('\nif [ "$state" = "start" -o "$state" = "restart" ] ; then\n')
      for version in [ 4, 6 ]:
         localAddress = makeNorNetIP(localProviderIndex, localSiteIndex, NorNet_NodeIndex_Tunnelbox, -1, version)
         outputFile.write('   make-address ' + localInterface + ' ' + str(localAddress) + '   && \\\n')
      outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
      outputFile.write('fi\n')


   outputFile.write('\nif [ "$state" = "stop" -o "$state" = "start" -o "$state" = "restart" ] ; then\n')
   outputFile.write('   log-action "Flushing route cache ..."\n')
   outputFile.write('   ip route flush cache && \\\n')
   outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
   outputFile.write('fi\n')


   outputFile.write('\nif [ "$state" = "start" -o "$state" = "restart" -o  "$state" = "status" ] ; then\n')
   outputFile.write('   log-action "Trying to contact PLC at ' + str(getPLCAddress()) + ' ..."\n')
   outputFile.write('   show-tunnel ' + interfaceToPLC + ' ' + \
                    '0.0.0.0 ' + str(getPLCAddress()) + ' ""   && \\\n')
   outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
   outputFile.write('fi\n\n')

   outputFile.write('\nif [ $_BadResults -gt 0 ] ; then\n')
   outputFile.write('   return 1\n')
   outputFile.write('fi\n')


# ###### Generate tunnelbox configuration ###################################
def makeTunnelBoxConfiguration(fullSiteList, localSite, configNamePrefix, v4only):
   if configNamePrefix == None:
      configNamePrefix = 'tunnelbox-' + localSite['site_short_name']
   configurationName = configNamePrefix + '-config'
   outputFile = makeConfigFile('Tunnelbox', configurationName, True)
   log('Making tunnelbox configuration for ' + localSite['site_long_name'] + ' ...')

   localSiteIndex    = localSite['site_index']
   localProviderList = getNorNetProvidersForSite(localSite)
   localInterface    = getTagValue(localSite['site_tags'], 'nornet_site_tb_internal_interface', '')
   if not re.match(r"^[a-z][a-z0-9-\.]*$", localInterface):
      error('Bad local interface setting for site ' + localSite['site_long_name'])
   sourceNatRange    = getTagValue(localSite['site_tags'], 'nornet_site_tb_nat_range_ipv4', '')
   fullNorNetIPv4    = makeNorNetIP(0, 0, 0, 0, 4)


   # ====== Remove local setup ==============================================
   outputFile.write('if [ "$selectedProviders" == "" ] ; then\n')
   outputFile.write('   if [ "$state" = "stop" -o "$state" = "restart" ] ; then\n')
   outputFile.write('      log "Tearing down local networks ..."\n')
   # outputFile.write('      log-action "Turning off IP forwarding ..."\n')
   # outputFile.write('      sysctl -q net.ipv4.ip_forward=0   && \\\n')
   # outputFile.write('      sysctl -q net.ipv6.conf.all.forwarding=0   && \\\n')
   outputFile.write('      log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
   for localProviderIndex in localProviderList:
      _makeTunnelboxNetwork(outputFile, 'stop', localInterface,
                            localProviderList[localProviderIndex], localSiteIndex, v4only)
   if localSiteIndex == NorNet_SiteIndex_Central:
      outputFile.write('\n      log-action "Turning off IPv4 NAT ..."\n')
      outputFile.write('      remove-nat ' + str(fullNorNetIPv4) + ' "' + sourceNatRange + '"   && \\\n')
      outputFile.write('      log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
   outputFile.write('   fi\n')
   outputFile.write('fi\n\n')

   # ====== Configure tunnels and routing ===================================
   outputFile.write('availableProviders="')
   providerList   = []
   configFileList = []
   pathNumber     = 0
   for onlyDefault in [ True, False ]:
      for localProviderIndex in localProviderList:
         if ( ((onlyDefault == True)  and (localProviderIndex == localSite['site_default_provider_index'])) or \
              ((onlyDefault == False) and (localProviderIndex != localSite['site_default_provider_index'])) ):
            localProvider = localProviderList[localProviderIndex]
            tbpName = _makeTunnelboxProvider(fullSiteList, localSite,
                                             localProviderList, localProvider,
                                             pathNumber, configNamePrefix, v4only)
            providerList.append(localProvider['provider_short_name'])
            configFileList.append(tbpName)
            if pathNumber > 0:
               outputFile.write(',')
            outputFile.write(localProvider['provider_short_name'])
            pathNumber = pathNumber + 1
   outputFile.write('"\n')

   outputFile.write('checkProviders "$availableProviders" "$selectedProviders"\n')

   outputFile.write('tbc_success=1\n')
   i = 0
   for provider in providerList:
      outputFile.write('if [[ "$selectedProviders" =~ ^\\*$|^' + provider + '$|^' + provider + ',|,' + provider + ',|,' + provider + '$ ]] ; then\n')
      outputFile.write('   echo "Configuring ' + configFileList[i] + '"\n')
      outputFile.write('   . ./' + configFileList[i] + ' || tbc_success=0\n')
      outputFile.write('else\n')
      outputFile.write('   echo "Skipping ' + configFileList[i] + '"\n')
      outputFile.write('fi\n')
      i = i + 1


   # ====== Make local setup ================================================
   outputFile.write('\nif [ "$selectedProviders" == "" ] ; then\n')
   outputFile.write('   if [ "$state" = "start" -o "$state" = "restart" ] ; then\n')
   outputFile.write('      log "Setting up local networks ..."\n')

   outputFile.write('      log-action "Deactivating reverse path filtering ..."\n')
   outputFile.write('      INTERFACES=`ip link show | awk \'/^([0-9]*:) ([a-zA-Z0-9\-]+):/ { print $2 }\' | sed -e "s/:$//"`\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.default.rp_filter=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.all.rp_filter=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.default.accept_redirects=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.all.accept_redirects=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv6.conf.default.accept_redirects=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv6.conf.all.accept_redirects=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.default.send_redirects=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.all.secure_redirects=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.default.secure_redirects=0 || true\n')
   outputFile.write('      sysctl -q -w net.ipv4.conf.all.send_redirects=0 || true\n')
   outputFile.write('      for interface in $INTERFACES ; do\n')
   outputFile.write('         sysctl -q -w net.ipv4.conf.$interface.rp_filter=0 || true\n')
   outputFile.write('         sysctl -q -w net.ipv4.conf.$interface.accept_redirects=0 || true\n')
   outputFile.write('         sysctl -q -w net.ipv4.conf.$interface.send_redirects=0 || true\n')
   outputFile.write('         sysctl -q -w net.ipv4.conf.$interface.secure_redirects=0 || true\n')
   outputFile.write('         sysctl -q -w net.ipv6.conf.$interface.accept_redirects=0 || true\n')
   outputFile.write('      done\n')
   outputFile.write('      log-result $RESULT_GOOD\n')

   outputFile.write('      log-action "Turning on ECN ..."\n')
   outputFile.write('      sysctl -q -w net.ipv4.tcp_ecn=1 && \\\n')
   outputFile.write('      log-result $RESULT_GOOD || log-result $RESULT_BAD\n')

   outputFile.write('      log-action "Turning on Forwarding ..."\n')
   outputFile.write('      sysctl -q -w net.ipv4.ip_forward=1 && \\\n')
   outputFile.write('      sysctl -q -w net.ipv6.conf.all.forwarding=1 && \\\n')
   outputFile.write('      log-result $RESULT_GOOD || log-result $RESULT_BAD\n')

   for localProviderIndex in localProviderList:
      _makeTunnelboxNetwork(outputFile, 'start', localInterface,
                            localProviderList[localProviderIndex], localSiteIndex, v4only)
   if localSiteIndex == NorNet_SiteIndex_Central:
      outputFile.write('\n      log-action "Turning on IPv4 NAT ..."\n')
      outputFile.write('      make-nat ' + str(fullNorNetIPv4) + ' "' + sourceNatRange + '" && \\\n')
      outputFile.write('      log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
   outputFile.write('   fi\n')
   outputFile.write('fi\n')


   outputFile.write('\nif [ "$state" = "stop" -o "$state" = "start" -o "$state" = "restart" ] ; then\n')
   outputFile.write('   log-action "Flushing route cache ..."\n')
   outputFile.write('   ip route flush cache && \\\n')
   outputFile.write('   log-result $RESULT_GOOD || log-result $RESULT_BAD\n')
   outputFile.write('fi\n\n')

   outputFile.write('if [ $tbc_success -eq 0 ] ; then\n')
   outputFile.write('  return 1\n')
   outputFile.write('fi\n')

   outputFile.close()
   return configurationName


# ###### Generate node configuration ########################################
def _makeNodeConfigurationForGivenNode(fullSiteList, site, nodeName, nodeIndex, interfaceName,
                                      variant, configNamePrefix):
   log('Making node configuration for ' + nodeName + ' ...')

   # ====== Debian /etc/network/interfaces ==================================
   debianFile = None
   if variant == 'Debian':
      if configNamePrefix == None:
         configNamePrefix = 'node-' + nodeName + '-'
      configurationName = configNamePrefix + 'interfaces'
      debianFile = makeConfigFile('Node', configurationName, False)

      debianFile.write('# ====== Loopback ======\n')
      debianFile.write('auto lo\n')
      debianFile.write('iface lo inet loopback\n\n')


   # ====== Fedora /etc/sysconfig/network-scripts/ifcfg-* ===================
   if variant == 'Fedora':
      if(configNamePrefix == None):
         configNamePrefix = 'node-' + nodeName + '-'
      for i in range(0, 256):
         configurationName = configNamePrefix + 'ifcfg-' + interfaceName + ':' + str(i)
         try:
            os.unlink(configurationName)
         except OSError:
            continue


   # ====== Get node information ============================================
   siteIndex       = site['site_index']
   providerList    = getNorNetProvidersForSite(site)
   ipv6Secondaries = []
   for onlyDefault in [ False, True  ]:   # NOTE: non-default providers first!
      for providerIndex in providerList:
         if ( ((onlyDefault == True)  and (providerIndex == site['site_default_provider_index'])) or \
              ((onlyDefault == False) and (providerIndex != site['site_default_provider_index'])) ):
            provider = providerList[providerIndex]
            if providerIndex == site['site_default_provider_index']:
               interface = interfaceName
            else:
               interface = interfaceName + ':' + str(providerIndex)

            # ====== Debian /etc/network/interfaces =========================
            if variant == 'Debian':
               debianFile.write('\n# ====== ' + provider['provider_long_name'] + ' (' + \
                                str(provider['provider_index']) + ') ======\n')
               debianFile.write('auto ' + interface + '\n')

            # ====== Fedora /etc/sysconfig/network-scripts/ifcfg-* ==========
            if variant == 'Fedora':
               if configNamePrefix == None:
                  configNamePrefix = 'node-' + nodeName + '-'
               configurationName = configNamePrefix + 'ifcfg-' + interface
               fedoraFile = makeConfigFile('Node', configurationName, False)
               fedoraFile.write('# ====== ' + provider['provider_long_name'] + ' (' + \
                                str(provider['provider_index']) + ') ======\n')
               fedoraFile.write('DEVICE=' + interface + '\n')
               fedoraFile.write('ONBOOT=yes\n')
               fedoraFile.write('BOOTPROTO=static\n\n')

            fedoraDnsServer = 1

            # ====== Generate IP configuration ==============================
            for version in [ 4, 6 ]:
               address = makeNorNetIP(providerIndex, siteIndex, nodeIndex,                  -1, version)
               gateway = makeNorNetIP(providerIndex, siteIndex, NorNet_NodeIndex_Tunnelbox, -1, version)

               # ====== Debian /etc/network/interfaces ======================
               if variant == 'Debian':
                  if version == 4:
                     debianFile.write('iface ' + interface + ' inet static\n')
                     debianFile.write('   address ' + str(address.ip) + '\n')
                     debianFile.write('   netmask ' + str(address.netmask) + '\n')
                  else:
                     if providerIndex != site['site_default_provider_index']:   # NOTE: Work-around for buggy Ubuntu ifupdown!
                        debianFile.write('   up   /sbin/ip -6 addr add ' + str(address) + ' dev ' + interface + '\n')
                        debianFile.write('   down /sbin/ip -6 addr del ' + str(address) + ' dev ' + interface + '\n')
                     else:
                        debianFile.write('\niface ' + interface + ' inet6 static\n')
                        debianFile.write('   address ' + str(address.ip) + '\n')
                        debianFile.write('   netmask ' + str(address.prefixlen) + '\n')

                  if providerIndex == site['site_default_provider_index']:
                     debianFile.write('   gateway ' + str(gateway.ip) + '\n')

                     dnsList = ''
                     for i in range(0, NorNet_MaxDNSServers - 1):
                        dns = IPAddress(getTagValue(site['site_tags'], 'nornet_site_dns' + str(1 + i), '0.0.0.0'))
                        if ((dns != IPv4Address('0.0.0.0')) and (dns.version == version)):
                           dnsList = dnsList + ' ' + str(dns)
                     if dnsList != '':
                        debianFile.write('   dns-nameservers' + dnsList + '\n')
                        debianFile.write('   dns-search ' + site['site_domain'] + '\n')

                     debianFile.write('\n')

               # ====== Fedora /etc/sysconfig/network-scripts/ifcfg-* =======
               if variant == 'Fedora':
                  if version == 4:
                     fedoraFile.write('IPADDR=' + str(address.ip) + '\n')
                     fedoraFile.write('NETMASK=' + str(address.netmask) + '\n')
                     if providerIndex == site['site_default_provider_index']:
                        fedoraFile.write('GATEWAY=' + str(gateway.ip) + '\n')
                  else:
                     if providerIndex != site['site_default_provider_index']:
                        ipv6Secondaries.append(address)

                     else:
                        fedoraFile.write('\nIPV6INIT=yes\n')
                        fedoraFile.write('IPV6_AUTOCONF=no\n')
                        fedoraFile.write('IPV6ADDR=' + str(address) + '\n')
                        fedoraFile.write('IPV6_DEFAULTGW=' + str(gateway.ip) + '\n')
                        fedoraFile.write('IPV6ADDR_SECONDARIES="')
                        i = 0
                        for secondaryAddress in ipv6Secondaries:
                           if i > 0:
                              fedoraFile.write(' ')
                           fedoraFile.write(str(secondaryAddress))
                           i = i + +1
                        fedoraFile.write('"\n')

                  for i in range(0, NorNet_MaxDNSServers - 1):
                     dns = IPAddress(getTagValue(site['site_tags'], 'nornet_site_dns' + str(1 + i), '0.0.0.0'))
                     if ((dns != IPv4Address('0.0.0.0')) and (dns.version == version)):
                        if ((providerIndex == site['site_default_provider_index']) or
                            (version == 4)):
                           fedoraFile.write('DNS' + str(fedoraDnsServer) + '=' + str(dns) + '\n')
                           fedoraDnsServer = fedoraDnsServer + 1


   # ====== Debian /etc/network/interfaces ==================================
   if variant == 'Debian':
      debianFile.close()
   return True


# ###### Generate node configuration ########################################
def makeNodeConfiguration(fullSiteList, node, interfaceOverride, variant, configNamePrefix):
   if int(node['node_index']) == NorNet_NodeIndex_Tunnelbox:
      return True

   if interfaceOverride == None:
      interface = node['node_nornet_interface']
   else:
      interface = interfaceOverride

   site = getNorNetSiteOfNode(fullSiteList, node)
   if site == None:
      error('Node ' + nodeName + ' does not belong to a NorNet site')

   return(_makeNodeConfigurationForGivenNode(fullSiteList, site, node['node_name'], node['node_index'],
                                             interface, variant, configNamePrefix))


# ###### Write Automatic Configuration Information ##########################
def _writeAutoConfigInformation(outputFile):
   outputFile.write('# ################ AUTOMATICALLY-GENERATED FILE! ################\n')
   outputFile.write('# #### Changes will be overwritten by NorNet config scripts! ####\n')
   outputFile.write('# ################ AUTOMATICALLY-GENERATED FILE! ################\n\n')


# ###### Generate NTP configuration #########################################
def makeNTPConfiguration(fullSiteList, localSite, configNamePrefix):
   if configNamePrefix == None:
      configNamePrefix = 'ntp-' + localSite['site_short_name']
   configurationName = configNamePrefix + '-config'
   outputFile = codecs.open(configurationName, 'w', 'utf-8')
   _writeAutoConfigInformation(outputFile)

   ntpServerList = []
   if localSite != None:
      for i in range(0, NorNet_MaxNTPServers - 1):
         ntpServer = IPAddress(getTagValue(localSite['site_tags'], 'nornet_site_ntp' + str(1 + i), '0.0.0.0'))
         if ntpServer != IPv4Address('0.0.0.0'):
            ntpServerList.append(ntpServer)

   outputFile.write('# ====== Drift File ======\n')
   outputFile.write('driftfile /var/lib/ntp/ntp.drift\n\n')

   outputFile.write('# ====== Statistics ======\n')
   outputFile.write('statsdir /var/log/ntpstats/\n')
   outputFile.write('filegen loopstats file loopstats type day enable\n')
   outputFile.write('filegen peerstats file peerstats type day enable\n')
   outputFile.write('filegen clockstats file clockstats type day enable\n\n')

   outputFile.write('# ====== Generic Access Restrictions ======\n')
   outputFile.write('restrict default ignore\n')
   for version in [ 4, 6 ]:
      fullNorNetNetwork = makeNorNetIP(0, 0, 0, 0, version)
      outputFile.write('restrict ' + str(fullNorNetNetwork.ip) + ' mask ' + str(fullNorNetNetwork.netmask) + ' nomodify\n')
   outputFile.write('restrict 127.0.0.1\n')
   outputFile.write('restrict ::1\n')
   outputFile.write('\n')

   if ((localSite == None) or (localSite['site_index'] != NorNet_SiteIndex_Central)):
      if fullSiteList != None:
         outputFile.write('# ====== NorNet Central Site NTP ======\n')
         centralSite  = fullSiteList[NorNet_SiteIndex_Central]
         providerList = getNorNetProvidersForSite(centralSite)
         for providerIndex in providerList:
            provider = providerList[providerIndex]
            if providerIndex == centralSite['site_default_provider_index']:
               for version in [ 4, 6 ]:
                  centralSiteTB = makeNorNetIP(providerIndex, NorNet_SiteIndex_Central, NorNet_NodeIndex_Tunnelbox, -1, version)
                  outputFile.write('server ' + str(centralSiteTB.ip) + '   # CENTRAL SITE\n')
                  outputFile.write('restrict ' + str(centralSiteTB.ip) + '\n')
         outputFile.write('\n')

   outputFile.write('# ====== NorNet Peers ======\n')
   for remoteSiteIndex in fullSiteList:
      if ( ((localSite == None) or (remoteSiteIndex != localSite['site_index'])) and
           (remoteSiteIndex != NorNet_SiteIndex_Central) ):
         for version in [ 4, 6 ]:
            remoteSite = fullSiteList[remoteSiteIndex]
            peerTB = makeNorNetIP(remoteSite['site_default_provider_index'], remoteSiteIndex, NorNet_NodeIndex_Tunnelbox, -1, version)
            outputFile.write('peer ' + str(peerTB.ip) + '   # ' + remoteSite['site_long_name'] + '\n')
            outputFile.write('restrict ' + str(peerTB.ip) + '\n')
   outputFile.write('\n')

   outputFile.write('# ====== External NTP Servers ======\n')
   for ntpServer in ntpServerList:
      outputFile.write('server ' + str(ntpServer) + '\n')
      outputFile.write('restrict ' + str(ntpServer) + '\n')

   outputFile.write('\n# ====== Fudge Clock ======\n')
   outputFile.write('server 127.127.1.0\n')
   outputFile.write('fudge 127.127.1.0 stratum 10\n')

   outputFile.close()


# ###### Generate SNMP configuration ########################################
def makeSNMPConfiguration(fullSiteList, fullUserList, localSite, configNamePrefix, name, description):
   if configNamePrefix == None:
      configNamePrefix = 'snmpd-' + localSite['site_short_name']
   configurationName = configNamePrefix + '-config'
   outputFile = codecs.open(configurationName, 'w', 'utf-8')
   _writeAutoConfigInformation(outputFile)


   outputFile.write('# ====== Agent ======\n')
   outputFile.write('agentAddress udp:161,udp6:[::1]:161\n\n')


   outputFile.write('# ====== System Information ======\n')
   country      = getTagValue(localSite['site_tags'], 'nornet_site_country', '???')
   province     = getTagValue(localSite['site_tags'], 'nornet_site_province', None)
   city         = getTagValue(localSite['site_tags'], 'nornet_site_city',    '???')
   outputFile.write('sysName     ' + name + '.' + localSite['site_domain'] + '\n')
   outputFile.write('sysDescr    ' + localSite['site_long_name'] + ' ' + description + '\n')
   outputFile.write('sysLocation ' + city)
   if province !=  None:
      outputFile.write(', ' + province)
   outputFile.write('/' + country + '\n')
   techUsers = fetchUsersOfNorNetSite(fullUserList, localSite, 'tech')
   if techUsers != None:
      outputFile.write('sysContact  ' +
                       techUsers[0]['user_title'] + ' ' +
                       techUsers[0]['user_first_name'] + ' ' +
                       techUsers[0]['user_last_name'] + ' ' +
                       '<' + techUsers[0]['user_email'] + '>\n')
   outputFile.write('sysServices 72\n\n')


   outputFile.write('# ====== Access Control ======\n')
   outputFile.write('rocommunity public 127.0.0.1\n')
   outputFile.write('rocommunity public ' + str(makeNorNetIP(0, 0, 0, 0, 4)) + '\n')
   outputFile.write('rocommunity6 public ::1\n')
   outputFile.write('rocommunity6 public ' + str(makeNorNetIP(0, 0, 0, 0, 6)) + '\n\n')

   outputFile.write('# ====== Active Monitoring ======\n')
   outputFile.write('trapcommunity           public\n')
   outputFile.write('trapsink                ' + str(makeNorNetIP(localSite['site_default_provider_index'],
                                                     NorNet_SiteIndex_Monitor,
                                                     NorNet_NodeIndex_Monitor, -1, 4).ip) + '\n')
   outputFile.write('iquerySecName           internalUser\n')
   outputFile.write('rouser                  internalUser\n')
   outputFile.write('# defaultMonitors         yes\n')
   outputFile.write('# linkUpDownNotifications yes\n\n')

   outputFile.write('# ====== Disk Monitoring (UCD-SNMP-MIB::dskTable) ======\n')
   outputFile.write('includeAllDisks 10%\n\n')

   outputFile.write('# ====== Load Monitoring (UCD-SNMP-MIB::laTable) ======\n')
   outputFile.write('load 12 10 5\n')

   outputFile.close()


# ###### Generate hostname configuration ####################################
def makeHostnameConfiguration(fullSiteList, fullUserList, localSite, configNamePrefix, name):
   if configNamePrefix == None:
      configNamePrefix = 'hostname-' + localSite['site_short_name']
   configurationName = configNamePrefix + '-config'
   outputFile = codecs.open(configurationName, 'w', 'utf-8')
   outputFile.write(name + '.' + localSite['site_domain'] + '\n')
   outputFile.close()


# ###### Generate hosts configuration #######################################
def makeHostsConfiguration(fullSiteList, fullUserList, localSite, localNode, configNamePrefix, name):
   if configNamePrefix == None:
      configNamePrefix = 'hosts-' + localSite['site_domain']
   configurationName = configNamePrefix + '-config'
   outputFile = codecs.open(configurationName, 'w', 'utf-8')

   _writeAutoConfigInformation(outputFile)

   outputFile.write('127.0.0.1\tlocalhost\n')
   outputFile.write('127.0.0.1\t' + name + '\n')
   outputFile.write('127.0.0.1\t' + name + '.' + localSite['site_domain'] + '\n\n')

   outputFile.write('::1\tip6-localhost ip6-loopback\n')
   outputFile.write('fe00::0\tip6-localnet\n')
   outputFile.write('ff00::0\tip6-mcastprefix\n')
   outputFile.write('ff02::1\tip6-allnodes\n')
   outputFile.write('ff02::2\tip6-allrouters\n\n')

   outputFile.close()


# ###### Generate Nagios configuration ######################################
def makeNagiosConfiguration(fullSiteList, fullNodeList, configNamePrefix):
   if configNamePrefix == None:
      configNamePrefix = 'nagios-' + localSite['site_short_name']
   configurationName = configNamePrefix + '-config'
   outputFile = codecs.open(configurationName, 'w', 'utf-8')
   _writeAutoConfigInformation(outputFile)

   if fullSiteList != None:
      try:
         centralSite = fullSiteList[NorNet_SiteIndex_Central]
      except:
         centralSite = None   # Some test state.

      for onlyDefault in [ True, False ]:
         for localSiteIndex in fullSiteList:
            if ( ((onlyDefault == True)  and (localSiteIndex == NorNet_SiteIndex_Central)) or \
                 ((onlyDefault == False) and (localSiteIndex != NorNet_SiteIndex_Central)) ):

               # ====== Site ================================================
               localSite         = fullSiteList[localSiteIndex]
               localProviderList = getNorNetProvidersForSite(localSite)
               country           = getTagValue(localSite['site_tags'], 'nornet_site_country', '???')
               province          = getTagValue(localSite['site_tags'], 'nornet_site_province', None)
               city              = getTagValue(localSite['site_tags'], 'nornet_site_city',    '???')
               tunnelboxIP       = makeNorNetIP(localSite['site_default_provider_index'], localSiteIndex, NorNet_NodeIndex_Tunnelbox, -1, 4)

               outputFile.write('# ====== ' + localSite['site_long_name'] + ' ======\n')
               outputFile.write('define host {\n')
               outputFile.write('   use           generic-host\n')
               outputFile.write('   host_name     ' + localSite['site_long_name'] + '\n')
               outputFile.write('   alias         ' + localSite['site_long_name'] + ' (' + city)
               if province !=  None:
                  outputFile.write(', ' + province)
               outputFile.write('/' + country + ')\n')
               outputFile.write('   address       ' + str(tunnelboxIP.ip) + '\n')
               outputFile.write('   notes         latlng: ' + str(localSite['site_latitude']) + ',' + str(localSite['site_longitude']) + '\n')
               outputFile.write('   check_command check_ping!100.0,20%!500.0,60%\n')
               if ((localSiteIndex != NorNet_SiteIndex_Central) and (centralSite != None)):
                  outputFile.write('   parents       ' + centralSite['site_long_name'] + '\n')
               outputFile.write('}\n')

               # ====== Addresses ===========================================
               for localProviderIndex in localProviderList:
                  localProvider = localProviderList[localProviderIndex]
                  for version in [ 4, 6 ]:
                     localAddress = makeNorNetIP(localProviderIndex, localSiteIndex, NorNet_NodeIndex_Tunnelbox, -1, version)
                     outputFile.write('# local: ' + str(localAddress) + ' ' + \
                                      localSite['site_short_name'] + ' via ' + localProvider['provider_long_name'] + '\n')

                     outputFile.write('service {\n')
                     outputFile.write('}\n')
                                      

               # ====== Tunnels =============================================
               for localProviderIndex in localProviderList:
                  localProvider = localProviderList[localProviderIndex]
                  for remoteSiteIndex in fullSiteList:
                     if remoteSiteIndex == localSiteIndex:
                        continue
                     remoteSite         = fullSiteList[remoteSiteIndex]
                     remoteProviderList = getNorNetProvidersForSite(remoteSite)
                     for remoteProviderIndex in remoteProviderList:
                        remoteProvider = remoteProviderList[remoteProviderIndex]
                        for version in [ 4, 6 ]:
                           tunnel        = _getTunnel(localSite, localProvider, remoteSite, remoteProvider, version)
                           remoteNetwork = makeNorNetIP(remoteProviderIndex, remoteSiteIndex, 0, 0, version)

                           outputFile.write('# ' + tunnel['tunnel_interface'] + ' ' + \
                                            str(tunnel['tunnel_local_inner_address']) + ' ' + \
                                            str(tunnel['tunnel_remote_inner_address']) + '\n')


               outputFile.write('\n')

   outputFile.close()
