#/usr/bin/python
#
# Python Setup
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
#

from distutils.core import setup


setup(name='NorNet',
      maintainer='Thomas Dreibholz',
      maintainer_email='dreibh@simula.no',
      version='1.0.0',
      author='Thomas Dreibholz',
      author_email='dreibh@simula.no',
      url='http://www.nntb.no/',
      license='GPL, Version 3.0',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet',
          'Topic :: Software Development :: Libraries',
          'Topic :: System :: Networking'],
      py_modules=['NorNetTools', 'NorNetConfiguration', 'NorNetAPI', 'NorNetProviderSetup', 'NorNetSiteSetup', 'NorNetNodeSetup', 'SysSetupCommons'])
