#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# NorNet Node Setup
# Copyright (C) 2012-2015 by Thomas Dreibholz
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
import socket;
import platform;

from ipaddress import ip_address, ip_interface, IPv4Address, IPv4Interface, IPv6Address, IPv6Interface;

# NorNet
from NorNetConfiguration import *;
from NorNetTools         import *;
from NorNetAPI           import *;
from NorNetProviderSetup import *;



# ###### Write Automatic Configuration Information ##########################
def writeAutoConfigInformation(outputFile, comment='#'):
   outputFile.write(comment + ' ################ AUTOMATICALLY-GENERATED FILE! ################\n')
   outputFile.write(comment + ' #### Changes will be overwritten by NorNet config scripts! ####\n')
   outputFile.write(comment + ' ################ AUTOMATICALLY-GENERATED FILE! ################\n\n')


# ###### Generate NFS daemon configuration ##################################
def makeAutoFSConfiguration(weAreOnFileServer, siteIndex, nodeIndex, addHeader):
   if platform.system() == 'FreeBSD':
      nfsOptions = 'nfsv4,tcp,rsize=32768,wsize=32768,soft,async,intr,noatime'
   else:
      nfsOptions = 'nfsvers=4,proto=tcp,rsize=32768,wsize=32768,soft,async,intr,noatime,nodiratime'

   outputFile = codecs.open('auto.master', 'w', 'utf-8')
   if addHeader == True:
      writeAutoConfigInformation(outputFile)
   if weAreOnFileServer == False:
      outputFile.write('/nfs\t/etc/auto.nfs\n')
   outputFile.close()

   outputFile = codecs.open('auto.nfs', 'w', 'utf-8')
   if addHeader == True:
      writeAutoConfigInformation(outputFile)
   if weAreOnFileServer == False:
      fileServer = 'nfs.' + getCentralSiteDomainName()
      outputFile.write('adm\t-fstype=nfs,' + nfsOptions + ',rw\t' + fileServer + ':/filesrv/adm\n')
      outputFile.write('pub\t-fstype=nfs,' + nfsOptions + ',rw\t' + fileServer + ':/filesrv/pub\n')
      outputFile.write('sys\t-fstype=nfs,' + nfsOptions + ',rw\t' + fileServer + ':/filesrv/sys\n')
      outputFile.write('node\t-fstype=nfs,' + nfsOptions + ',rw\t' + fileServer + ':/filesrv/sys/' + str(siteIndex) + '/' + str(nodeIndex) + '\n')
   outputFile.close()


# ##### Make collectd skeleton configuration ################################
def makeCollectdNetworkConfig(serverName,collectdNetworkConfigFileName='collectd-network-config'):
   collectdNetworkConfigFile = codecs.open(collectdNetworkConfigFileName, 'w', 'utf-8')
   collectdNetworkConfigFile.write('LoadPlugin network\n')
   collectdNetworkConfigFile.write('<Plugin network>\n')
   collectdNetworkConfigFile.write('<Server "' + serverName + '" "25826">\n')
   collectdNetworkConfigFile.write('SecurityLevel "Encrypt"\n')
   collectdNetworkConfigFile.write('Username "nnc"\n')
   collectdNetworkConfigFile.write('Password "NorN3t"\n')
   collectdNetworkConfigFile.write('</Server>"\n')
   collectdNetworkConfigFile.write('</Plugin>\n')


# ##### Make collectd skeleton configuration ################################
def makeCollectdGeneralConfig(collectdGeneralConfigFileName='collectd-general-config'):
   dot_d_dir = '/etc/collectd.d/'
   collectdNetworkConfigFile = codecs.open(collectdGeneralConfigFileName, 'w', 'utf-8')
   collectdNetworkConfigFile.write('LoadPlugin syslog\n')
   collectdNetworkConfigFile.write('<Plugin syslog>\nLogLevel info\n</Plugin>\nInclude "' + dot_d_dir + '*.conf"\n')
   collectdNetworkConfigFile.close()
