#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# NorNet Tools
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


from ipaddress import ip_address, ip_network, IPv4Address, IPv4Network, IPv6Address, IPv6Network;
from socket    import getaddrinfo, AF_INET, AF_INET6;

import os;
import re;
import sys;
import errno;
import codecs;
import datetime;
import crypt;
import random;
import string;


# ###### Print log message ##################################################
def log(logstring):
   print(('\x1b[32m' + datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ': ' + logstring + '\x1b[0m'));


# ###### Abort with error ###################################################
def error(logstring):
   sys.stderr.write(datetime.datetime.now().isoformat() + \
                    ' ===== ERROR: ' + logstring + ' =====\n')
   sys.exit(1)


# ###### Fill string up with spaces up to given number of characters ########
def fill(string, characters):
   result = string
   i      = len(string)
   while i < characters:
      result = result + ' '
      i      = i + 1
   return result


# ###### Unquote a string ###################################################
def unquote(string):
   m = re.match(r'''^"(.*)"$''', string)
   if m != None:
      return m.group(1)
   m = re.match(r'''^\'(.*)\'$''', string)
   if m != None:
      return m.group(1)
   return string


# ###### Remove shell-style comment from input line #########################
def removeComment(line):
   quoteStack = []
   inEscape   = False

   for i, c in enumerate(line):
      if ((len(quoteStack) == 0) and (c == '#')):
         # '#' is comment => remove it.
         return line[:i].strip()
      elif inEscape:
         # Backslash => continue.
         inEscape = False
      elif ((len(quoteStack) > 0) and (c == '\\')):
         # In quote and next character is to be escaped.
         inEscape = True
      elif ((c == '"') or (c == '\'')):
         if ((len(quoteStack) > 0) and (c == quoteStack[len(quoteStack) - 1])):
            quoteStack.pop()
         else:
            quoteStack.append(c)

   return line


# ###### Filter for text ####################################################
def filterForTextOnly(s):
   return [x for x in s if x in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz,.:!? \t']


# ###### Get tag value or return a default ##################################
def getTagValue(tagList, tagName, default):
   for tag in tagList:
      if tag['tagname'] == tagName:
         return(tag['value'])
   return(default)


# ###### Create a configuration file ########################################
def makeConfigFile(type, configurationName, setInfoVariable):
   outputFile = codecs.open(configurationName, 'w', 'utf-8')
   outputFile.write('# ===== ' + type + ' configuration ===============\n')

   #now = datetime.datetime.now().isoformat()
   #info = str.replace(str.lower(configurationName), '-', '_')
   #outputFile.write('# Generated on ' + now + '\n\n')
   #if setInfoVariable == True:
   #   outputFile.write(info + '="' + now + '"\n\n')

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
      return(ip_address(result[0][4][0]))
   except:
      return None


# ###### Get hostname from FQDN #############################################
def getHostnameFromFQDN(fqdn):
   match = re.search('^([^\.]*)\.(.*)', fqdn)
   if match != None:
      return match.group(1)
   else:
      return fqdn


# ###### Get hostname from FQDN #############################################
def getDomainFromFQDN(fqdn):
   match = re.search('^([^\.]*)\.(.*)', fqdn)
   if match != None:
      return match.group(2)
   else:
      return ''


# ###### Make a crypted password ############################################
def makeUnixPassword(password):
   # Generate salt: 2-character random string
   salt = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(2))
   return crypt.crypt(password, salt)


# ###### Get reverse lookup zone for IP address #############################
def getZoneForAddress(addressObject, prefix):
   address = int(addressObject)
   result  = ''

   # ====== IPv4 ============================================================
   if addressObject.version == 4:
      if (prefix % 8) != 0:
         error('Bad prefix /' + str(prefix) + ' for IPv4 address reverse lookup!')

      address = address >> (32 - prefix)
      i = 0
      while i < prefix:
         n = (address & 0xff)
         result = result + str(n) + '.'
         address = address >> 8
         i = i + 8
      result = result + 'in-addr.arpa.'

   # ====== IPv6 ============================================================
   else:
      if (prefix % 4) != 0:
         error('Bad prefix /' + str(prefix) + ' for IPv6 address reverse lookup!')

      address = address >> (128 - prefix)
      i = 0
      while i < prefix:
         n = (address & 0xf)
         result = result + str.replace(hex(int(n)), '0x', '') + '.'
         address = address >> 4
         i = i + 4
      result = result + 'ip6.arpa.'

   # print result
   return result


# ###### Convert name to unicode, ASCII and punycode representations ########
def makeNameFromUnicode(name, isDNSName = True):
   if isDNSName == True:
      unicodeName = str(name).lower()
   else:
      unicodeName = str(name)
   punycodeName = unicodeName.encode("idna")
   asciiName    = ''
   for i in range(0, len(unicodeName)):
      if ( ((unicodeName[i] >= 'a') and
            (unicodeName[i] <= 'z')) or
           ((unicodeName[i] >= 'A') and
            (unicodeName[i] <= 'Z')) or
           ((unicodeName[i] >= '0') and
            (unicodeName[i] <= '9')) or
           ((isDNSName == False) and (unicodeName[i] == ' ')) or
           (unicodeName[i] == '-') or
           (unicodeName[i] == '.')):
         asciiName = asciiName + unicodeName[i]
      elif ((unicodeName[i] == 'ä') or (unicodeName[i] == 'æ')):
         asciiName = asciiName + 'ae'
      elif ((unicodeName[i] == 'ö') or (unicodeName[i] == 'ø')):
         asciiName = asciiName + 'oe'
      elif (unicodeName[i] == 'ü'):
         asciiName = asciiName + 'ue'
      elif (unicodeName[i] == 'ß'):
         asciiName = asciiName + 'ss'
      elif (unicodeName[i] == 'å'):
         asciiName = asciiName + 'aa'
      elif (unicodeName[i] == 'ã'):
         asciiName = asciiName + 'a'
      elif (unicodeName[i] == 'ô'):
         asciiName = asciiName + 'o'
      elif (unicodeName[i] == 'ñ'):
         asciiName = asciiName + 'n'
      elif (unicodeName[i] == 'ž'):
         asciiName = asciiName + 'z'
      elif (unicodeName[i] == 'š'):
         asciiName = asciiName + 's'
      elif (unicodeName[i] == 'ū'):
         asciiName = asciiName + 'u'
      elif ( (unicodeName[i] == 'č') or (unicodeName[i] == 'ć') or (unicodeName[i] == 'ç')):
         asciiName = asciiName + 'c'
      elif ( (unicodeName[i] == 'é') or (unicodeName[i] == 'è') or \
             (unicodeName[i] == 'ê') or (unicodeName[i] == 'ë')) :
         asciiName = asciiName + 'e'
      else:
         error('Unhandled character "' + unicodeName[i] + '" in name ' + unicodeName)

   dnsName = {
      'utf8'     : unicodeName,
      'ascii'    : str(asciiName),
      'punycode' : punycodeName
   }
   return dnsName


# ###### Make directory, if it is not yet existing ##########################
def makeDir(path):
   try:
      os.mkdir(path, 0o755)
   except OSError as e:
      if e.errno == errno.EEXIST and os.path.isdir(path):
         pass
      else:
         raise


# ###### Change current directory, return previous one ######################
def changeDir(path):
   oldDirectory = os.getcwd()
   os.chdir(path)
   return oldDirectory


# ###### Create, or update existing, symlink ################################
def makeSymlink(linkName, newLinkTarget):
   existingLinkTarget = None
   try:
      existingLinkTarget = os.readlink(linkName)
   except:
      existingLinkTarget = None

   if existingLinkTarget != newLinkTarget:
      try:
         os.unlink(linkName)
      except Exception as e:
         pass
      try:
         os.symlink(newLinkTarget, linkName)
      except Exception as e:
         pass
