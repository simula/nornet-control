#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NorNet Tools
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


# Needs package python-ipaddr (Fedora Core, Ubuntu, Debian)!
from ipaddr import IPAddress, IPNetwork, IPv4Address, IPv4Network, IPv6Address, IPv6Network;

from socket import getaddrinfo, AF_INET, AF_INET6;

import os;
import re;
import sys;
import datetime;


# ###### Print log message ##################################################
def log(logstring):
   print(datetime.datetime.utcnow().isoformat() + ' ' + logstring);


# ###### Abort with error ###################################################
def error(logstring):
   print(datetime.datetime.utcnow().isoformat() + \
         ' ===== ERROR: ' + logstring + " =====");
   sys.exit(1)


# ###### Get tag value or return a default ##################################
def getTagValue(tagList, tagName, default):
   for tag in tagList:
      if tag['tagname'] == tagName:
         return(tag['value'])
   return(default)


# ###### Create a configuration file ########################################
def makeConfigFile(type, configurationName, setInfoVariable):
   outputFile = open(configurationName, 'w')
   outputFile.write('# ===== ' + type + ' configuration ===============\n')
   now = datetime.datetime.utcnow().isoformat()
   info = str.replace(str.lower(configurationName), '-', '_')
   outputFile.write('# Generated on ' + now + '\n\n')
   if setInfoVariable == True:
      outputFile.write(info + '="' + now + '"\n\n')

   return outputFile


# ###### Obtain local addresses of host #####################################
def getLocalAddresses(version):
   addressList = []
   ipOption    = '-' + str(version)

   try:
      lines  = tuple(os.popen('/sbin/ip ' + ipOption + ' addr show'))
   except Exception as e:
      error('Unable to call /sbin/ip to obtain interface addresses: ' + str(e))

   for line in lines:
      match = re.search('(^[ \t]*inet6[ \t]*)([0-9a-zA-Z:]*)([ \t]*)', line)
      if match != None:
         v6Address = IPv6Address(match.group(2))
         if not v6Address.is_link_local:
            addressList.append(v6Address)
      else:
         match = re.search('(^[ \t]*inet[ \t]*)([0-9\.]*)([ \t]*)', line)
         if match != None:
            v4Address = IPv4Address(match.group(2))
            addressList.append(v4Address)

   return addressList


# ###### Resolve hostname and return first address ##########################
def resolveHostname(name, protocol=0):
   try:
      result = getaddrinfo(name, 123, protocol)
      print result
      return(IPAddress(result[0][4][0]))
   except:
      return None
