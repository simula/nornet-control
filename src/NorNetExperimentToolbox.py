#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# NorNet Experiment Toolbox
# Copyright (C) 2016 by Thomas Dreibholz
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
import os
import subprocess

from NorNetAPI import *


# ###### Set global variable ################################################
def setGlobalVariable(variable, value):
   globals()[variable] = value


# ###### Invoke command #####################################################
def runLocal(cmdLine, async = False):
   print('\x1b[33m' + cmdLine + '\x1b[0m')
   if async == False:
      result = subprocess.call(cmdLine, shell=True)
      if result != 0:
         print('\x1b[31;1m========== WARNING: result=' + str(result) + ' ==========\x1b[0m')
      return result
   else:
      newProcess = subprocess.Popen(cmdLine, shell=True)
      return newProcess


# ###### Invoke command on node via SSH #####################################
def runOverSSH(sshPrivateKey, node, slice, cmdLine, async = False):
   if not os.access(sshPrivateKey, os.R_OK):
      sys.stderr.write('\n#####################################################\n')
      sys.stderr.write('Private key not found: ' + sshPrivateKey + '\n')
      sys.stderr.write('Check your measurement script settings!\n')
      sys.stderr.write('#####################################################\n')
      sys.exit(1)

   sshCall = [ '/usr/bin/ssh' , '-4', '-i', sshPrivateKey, slice['slice_name'] + '@' + node['node_name'] , '-oStrictHostKeyChecking=no', '-oVerifyHostKeyDNS=no', '-oConnectTimeout=30', '-oBatchMode=yes', cmdLine ]
   print('\x1b[34m' + slice['slice_name'] + '@' + node['node_name'] + '> ' + '\x1b[33m' + cmdLine + '\x1b[0m')
   if async == False:
      result = subprocess.call(sshCall, shell=False)
      if result != 0:
         print('\x1b[31;1m========== WARNING: result=' + str(result) + ' ==========\x1b[0m')
   else:
      newProcess = subprocess.Popen(sshCall)
      return newProcess


# ###### Copy directory with RSync from node ################################
def copyFromNodeOverRSync(sshPrivateKey, node, slice, directory):
   rsyncCall = [ '/usr/bin/rsync', '-e', 'ssh -4 -i ' + sshPrivateKey, '-av', '-q', slice['slice_name'] + '@' + node['node_name'] + ':' + directory + '/', directory + '/' ]
   print('\x1b[33m' + str(rsyncCall) + '\x1b[0m')
   result = subprocess.call(rsyncCall)
   if result != 0:
      print('\x1b[31;1m========== WARNING: result=' + str(result) + ' ==========\x1b[0m')


# ###### Make address #######################################################
# Gets slice's address, nor 0.0.0.0/:: if no provider is given
def makeAddress(site, node, provider, ipVersion, slice):
   if provider != None:
      if node['node_state'] != 'MANUAL':
         # This is a slice!
         sliceNodeIndex = getSliceNodeIndexOfNorNetSlice(slice, node)
      else:
         # The node is actually a pseudo-node, created with makePseudoNode()
         sliceNodeIndex = node['node_index']

      address = makeNorNetIP(provider['provider_index'], site['site_index'], node['node_index'],
                             ipVersion, sliceNodeIndex).ip
   else:
      if ipVersion == 4:
         address = IPv4Address('0.0.0.0')
      elif ((ipVersion == 6) or (ipVersion == 46)):
         address = IPv6Address('::')
      else:
         raise Exception('Invalid setting for ipVersion!')

   return address


# ###### Make port ##########################################################
def makePort(portBase, site, node, provider, ipVersion, slice):
   if provider != None:
      port = portBase + 10 * provider['provider_index']
   else:
      port = portBase

   if ipVersion == 46:
      port = port + 3000
   elif ipVersion == 6:
      port = port + 6000
   elif ipVersion != 4:
      raise Exception('Invalid setting for ipVersion!')

   if port > 65535:
      raise Exception('Port > 65535. Use a smaller port base setting!')

   return port


# ###### Create NorNetNode structure for non-NorNet node ####################
def makePseudoNode(fullSiteList,
                   fqdn      = getLocalNodeHostname(),
                   nodeIndex = getLocalNodeIndex()):
   hostName   = getHostnameFromFQDN(fqdn)
   siteDomain = getDomainFromFQDN(fqdn)
   site       = getNorNetSiteOfDomain(fullSiteList, siteDomain)
   if site == None:
      error('Domain ' + siteDomain + ' not found!')

   norNetNode = {
         'node_site_id'          : site['site_id'],
         'node_index'            : nodeIndex,
         'node_name'             : str.lower(hostName) + '.' + site['site_domain'],
         'node_utf8'             : str.lower(hostName) + '.' + site['site_domain'],
         'node_nornet_interface' : None,
         'node_model'            : 'Unknown',
         'node_type'             : 'Node',
         'node_state'            : 'MANUAL',
         'node_ssh_rsa_key'      : None,
         'node_tags'             : []
   }
   return norNetNode


# ###### Start server instances #############################################
# Different instances (with different ports) for:
# - ANY address (0.0.0.0/::)
# - Each provider separately (only if fullSiteList is provided, i.e. not None)
def startServer(fullSiteList, portBase, measurementName, sshPrivateKey, node, slice, pathMgr):
   if fullSiteList != None:
      localSite          = getNorNetSiteOfNode(fullSiteList, node)
      localProviderList  = getNorNetProvidersForSite(localSite)
   else:
      localSite         = None
      localProviderList = None

   cmdLine = 'pkill netperfmeter ; rm -rf ' + measurementName + ' ; mkdir ' + measurementName

   # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   # !!! Setting initial rcvbuf/sndbuf here! !!!
   # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   passiveSideOptions = \
      '-rcvbuf=16000000 -sndbuf=16000000 ' + \
      '-verbosity=0 ' + \
      '-pathmgr='     + pathMgr

   # ------ Bind to ANY address ---------------------------------------------
   for ipVersion in [ 4, 46, 6 ]:
      localAddress = makeAddress(localSite, node, None, ipVersion, slice)
      localPort    = makePort(portBase, localSite, node, None, ipVersion, slice)

      if ipVersion != 6:
         v6Options = ''
      else:
         v6Options = '-v6only '

      cmdLine = cmdLine + ' ; \\\n( nohup netperfmeter ' + str(localPort) + ' ' + \
         '-controllocal=[::] ' + \
         '-local=[' + str(localAddress) + '] ' + \
         v6Options + passiveSideOptions + ' '  + \
         '>>' + measurementName + '/NetPerfMeter-' + node['node_name'] + '.log 2>&1 & )'

   # ------ Bind to specific address ----------------------------------------
   if localProviderList != None:
      for localProviderIndex in localProviderList:
         localProvider = localProviderList[localProviderIndex]
         for ipVersion in [ 4, 46, 6 ]:
            localAddress = makeAddress(localSite, node, localProvider, ipVersion, slice)
            localPort    = makePort(portBase, localSite, node, localProvider, ipVersion, slice)

            if ipVersion != 6:
               v6Options = ''
            else:
               v6Options = '-v6only '

            cmdLine = cmdLine + ' ; \\\n( nohup netperfmeter ' + str(localPort) + ' ' + \
               '-controllocal=[::] ' + \
               '-local=[' + str(localAddress) + '] ' + \
               v6Options + passiveSideOptions + ' '  + \
               '>>' + measurementName + '/NetPerfMeter-' + node['node_name'] + '.log 2>&1 & )'

   result = runOverSSH(sshPrivateKey, node, slice, cmdLine, True)
   return result


# ###### Clean up passive side ##############################################
def stopServer(measurementName, sshPrivateKey, node, slice):
   cmdLine = 'pkill netperfmeter && hostname && cat ' + measurementName + '/NetPerfMeter-' + node['node_name'] + '.log'
   return runOverSSH(sshPrivateKey, node, slice, cmdLine, True)


# ###### Test installation of custom NetPerfMeter ###########################
def testCustomNetPerfMeter(sshPrivateKey, nodes, slice):
   for node in nodes:
      sys.stderr.write(node['node_name'] + "-> ")
      cmdLine = 'uname -a && cd src/netperfmeter && git pull'
      newProcess = runOverSSH(sshPrivateKey, node, slice, cmdLine, True)
      if newProcess != None:
         newProcess.wait()


# ###### Install custom NetPerfMeter from Git sources #######################
def installCustomNetPerfMeter(sshPrivateKey, nodes, slice, nodeType = "nornet"):
   processes = []
   for node in nodes:
      sys.stderr.write(node['node_name'] + "-> ")

      # ====== NorNet Fedora Core node ======================================
      if nodeType == "nornet":
         cmdLine = """
sudo dnf install -y cmake gcc-c++ make git glib2-devel bzip2-devel lksctp-tools-devel valgrind-devel ; \\
sudo dnf upgrade -y --exclude=kernel* ; \\
git config --global http.proxy proxy.`hostname -d`:3128 ; """

      # ====== Fedora Core machine ==========================================
      elif nodeType == "fedora":
         cmdLine = """
sudo dnf install -y cmake gcc-c++ make git glib2-devel bzip2-devel lksctp-tools-devel valgrind-devel ; \\
sudo dnf upgrade -y --exclude=kernel* ; """

      # ====== Ubuntu machine ==============================================
      elif nodeType == "ubuntu":
         cmdLine = """
sudo apt-get update ; \\
sudo apt-get install -y cmake g++ make git libbz2-dev libsctp-dev ; \\
sudo apt-get dist-upgrade -y ; """

      # ====== Invalid node type ============================================
      else:
         error('Invalid node type "' + nodeType + '"')


      # ====== Fetch, compile and install NetPerfMeter ======================
      cmdLine = cmdLine + """
sudo -u """ + slice['slice_name'] + """ mkdir -p ~/src && cd src/ && \\
if [ -e netperfmeter ] ; then
   cd netperfmeter && git pull
else
   git clone https://github.com/dreibh/netperfmeter.git && \\
   cd netperfmeter
fi && \
./autogen.sh && sudo make install"""


      newProcess = runOverSSH(sshPrivateKey, node, slice, cmdLine, True)
      if newProcess != None:
         # newProcess.wait()
         processes.append(newProcess)

   for process in processes:
      process.wait()
