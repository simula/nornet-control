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


import sys;
import datetime;


# ###### Print log message ==================================================
def log(logstring):
   print datetime.datetime.utcnow().isoformat() + ' ' + logstring;


# ###### Abort with error ===================================================
def error(logstring):
   print datetime.datetime.utcnow().isoformat() + ' ===== ERROR: ' + logstring + " =====";
   sys.exit(1)


# ###### Get tag value or return a default ==================================
def getTagValue(tagList, tagName, default):
   for tag in tagList:
      if tag['tagname'] == tagName:
         return(tag['value'])
   return(default)


# ###### Create a configuration file ########################################
def makeConfigFile(type, configurationName):
   outputFile = open(configurationName, 'w')
   outputFile.write('# ===== ' + type + ' configuration ===============\n')
   now = datetime.datetime.utcnow().isoformat()
   info = str.replace(str.lower(configurationName), '-', '_')
   outputFile.write('# Generated on ' + now + '\n\n')
   outputFile.write(info + '="' + now + '"\n\n')

   return outputFile
