How to Set Up a NorNet Test Environment in VMs
==============================================

1. Prepare Template VM.

Base: Ubuntu 22.04 from <URL>

 a. Set new password
 b. 
 c. Prepare sources:
   cd src
   git clone ...

2. Run configure-vms to create the VMs of the test environment.

 The VM TestSetup-Crossconnect connects the 4 test sites to the Internet.
 It performs NAT for the IPv6 unique local range of the NorNet environment!
 It also performs NAT for the IPv4 ISP networks of TestSetup-Crossconnect.
 The tunnelboxes already perform IPv4 NAT from the local range of the NorNet
 environment to these addresses of TestSetup-Crossconnect.

3. Prepare PLC.

4. Prepare tunnelboxes.

5. Prepare non-tunnelbox VMs.
