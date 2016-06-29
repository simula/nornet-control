#!/usr/bin/python3 -u
# -*- python3 -*-
# -*- coding: utf-8 -*-
#
# /=========================================================================\
# =             #     #                 #     #                             =
# =             ##    #   ####   #####  ##    #  ######   #####             =
# =             # #   #  #    #  #    # # #   #  #          #               =
# =             #  #  #  #    #  #    # #  #  #  #####      #               =
# =             #   # #  #    #  #####  #   # #  #          #               =
# =             #    ##  #    #  #   #  #    ##  #          #               =
# =             #     #   ####   #    # #     #  ######     #               =
# =                                                                         =
# =             A Real-World, Large-Scale Multi-Homing Testbed              =
# =                          https://www.nntb.no/                           =
# =                                                                         =
# = Contact: Thomas Dreibholz                                               =
# =          dreibh@simula.no, https://www.simula.no/people/dreibh          =
# \=========================================================================/
#
# this is only an example file
# the actual file is installed in your testmaster box as /root/LocalTestResources.py
#

if __name__ == '__main__':
   import sys, os.path
   sys.path.append(os.path.expanduser("~/git-tests/system"))

from Substrate import Substrate

# domain name .pl.sophia.inria.fr is implicit on our network
class OnelabSubstrate (Substrate):

   def test_box_spec (self):
      return 'earnslaw'

   # the experimental lxc-based build box
   def build_lxc_boxes_spec (self):
      return [ 'queenstown', 'arrowtown', 'cromwell' ]

   # the lxc-capable box for PLCs
   def plc_lxc_boxes_spec (self):
      return [ ('wakatipu', 4) ]

   # vplc01 to vplc10
   def vplc_ips (self):
      return [  ( 'vplc{:02d}.simula.nornet'
                      .format(i),               # DNS name
                  'unused')                     # MAC address
                for i in range(1, 9) ]

   # kvm boxes for nodes
   def qemu_boxes_spec (self):
      return [ ('bjordammen', 8) ]

   # vnode01 to 20
   # the nodes IP pool has a MAC address as user-data (3rd elt in tuple)
   def vnode_ips (self):
      return [ ( 'vnode{:02d}'.format(i),            # DNS name
                 '02:34:56:00:00:{:02d}'.format(i))  # MAC address
               for i in range(1, 17) ]

   # local network settings
   def domain (self):
      return 'simula.nornet'

   def network_settings (self):
      return { 'interface_fields:gateway':      '10.1.1.1',
               'route_fields:next_hop':         '10.1.1.1',
               'interface_fields:network':      '10.1.1.0',
               'interface_fields:broadcast':    '10.1.1.255',
               'interface_fields:netmask':      '255.255.255.0',
               'interface_fields:dns1':         '10.1.1.1',
               'interface_fields:dns2':         '10.1.1.1',
               'node_fields_nint:dns':          '10.1.1.1,10.1.1.1',
               'ipaddress_fields:netmask':      '255.255.255.0',
               }

# the hostname for the testmaster - in case we'd like to run this remotely
   def testmaster (self):
      return 'earnslaw'

local_substrate = OnelabSubstrate ()

if __name__ == '__main__':
   local_substrate.main()
