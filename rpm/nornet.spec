Name: nornet
Version: 1.3.5
Release: 1
Summary: NorNet Control
Group: Applications/Internet
License: GPLv3
URL: https://www.nntb.no/
Source: https://www.nntb.no/download/%{name}-%{version}.tar.xz

AutoReqProv: on
BuildRequires: cmake
BuildRequires: dejavu-sans-fonts
BuildRequires: dejavu-sans-mono-fonts
BuildRequires: dejavu-serif-fonts
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: ghostscript
BuildRequires: gimp
BuildRequires: google-noto-cjk-fonts
BuildRequires: google-noto-sans-fonts
BuildRequires: google-noto-serif-fonts
BuildRequires: GraphicsMagick
BuildRequires: perl-Image-ExifTool
BuildRequires: python3
BuildRequires: qt5-qtbase-devel
BuildRequires: texlive-epstopdf-bin
BuildRequires: urw-base35-fonts
BuildRoot: %{_tmppath}/%{name}-%{version}-build


# This package does not generate debug information (no executables):
%global debug_package %{nil}

# TEST ONLY:
%define _unpackaged_files_terminate_build 0


%description
NorNet is a testbed for multi-homed systems. This package
contains the management software for the testbed's
infrastructure management software.
See https://www.nntb.no for details on NorNet!

%prep
%setup -q

%build
%cmake -DCMAKE_INSTALL_PREFIX=/usr -DPYTHON_LIBRARY_PREFIX=%{buildroot}/usr -DFLAT_DIRECTORY_STRUCTURE=1 -DBUILD_BOOTSPLASH=1 .
make %{?_smp_mflags}

%install
make DESTDIR=%{buildroot} install
# ====== Relocate files =====================================================
mkdir -p %{buildroot}/sbin
mv %{buildroot}/usr/sbin/Interface-Setup %{buildroot}/sbin

mkdir -p %{buildroot}/var
mv %{buildroot}/usr/var/www %{buildroot}/var

mkdir -p %{buildroot}/boot/NorNet
mv %{buildroot}/usr/share/nornet-desktop/Splash/*-1024x768.jpeg %{buildroot}/boot/NorNet
mkdir -p %{buildroot}/etc/nornet
mv %{buildroot}/usr/share/nornet-desktop/Splash/nornet-version %{buildroot}/etc/nornet
mkdir -p %{buildroot}/usr/share/nornet/background

mv %{buildroot}/usr/share/nornet-desktop/Desktop-with-Logo/Background1-1600x1200-plain.png      %{buildroot}/usr/share/nornet/background/NorNet-Background1-4x3.png
mv %{buildroot}/usr/share/nornet-desktop/Desktop-with-Logo/Background1-1920x1200-plain.png      %{buildroot}/usr/share/nornet/background/NorNet-Background1-16x10.png
mv %{buildroot}/usr/share/nornet-desktop/Desktop-with-Logo/Background1-3840x2160-plain.png      %{buildroot}/usr/share/nornet/background/NorNet-Background1-16x9.png
mv %{buildroot}/usr/share/nornet-desktop/Desktop-without-Logo/Background1-1600x1200-plain.png   %{buildroot}/usr/share/nornet/background/NorNet-Background1-without-Logo-4x3.png
mv %{buildroot}/usr/share/nornet-desktop/Desktop-without-Logo/Background1-1920x1200-plain.png   %{buildroot}/usr/share/nornet/background/NorNet-Background1-without-Logo-16x10.png
mv %{buildroot}/usr/share/nornet-desktop/Desktop-without-Logo/Background1-3840x2160-plain.png   %{buildroot}/usr/share/nornet/background/NorNet-Background1-without-Logo-16x9.png
# ===========================================================================


%package management
Summary: NorNet Management
Group: Applications/Internet
BuildArch: noarch
Requires: bash-completion
Requires: bridge-utils
Requires: btrfs-progs
Requires: bc
Requires: bwm-ng
Requires: colordiff
Requires: cronie
Requires: ethtool
Requires: git
Requires: gpm
Requires: hping3
Requires: htop
Requires: ipsec-tools
Requires: joe
Requires: jq
Requires: libidn
Requires: lksctp-tools
Requires: mlocate
Requires: net-snmp-utils
Requires: net-tools
Requires: nmap
Requires: ntpdate
Requires: pxz
Requires: reiserfs-utils
Requires: reprepro
Requires: smartmontools
Requires: subnetcalc
Requires: tcpdump
Requires: tftp
Requires: traceroute
Requires: tree
Requires: vconfig
Requires: virt-what
Requires: whois
Requires: xmlstarlet
Recommends: grub2-tools
Recommends: netperfmeter
Recommends: rsplib-docs
Recommends: rsplib-services
Recommends: rsplib-tools
Recommends: wireshark-cli

%description management
This metapackage contains basic software nor NorNet node management. The
software installed provides a common working environment.
See https://www.nntb.no for details on NorNet!

%files management
/boot/NorNet/Management1-1024x768.jpeg
/etc/grub.d/??_nornet_management_theme
/etc/nornet/nornet-authorized_keys
/etc/nornet/nornet-version
/usr/bin/Auto-Update-Keys
/usr/bin/Check-Nodes
/usr/bin/Check-Nodes-Loop
/usr/bin/Clear-SSH-Node-Key
/usr/bin/Create-New-SSH-Node-Keys
/usr/bin/Fingerprint-SSH-Node-Keys
/usr/bin/Get-Nodes
/usr/bin/Get-NorNet-Configuration
/usr/bin/Get-Sites
/usr/bin/Get-Slice-Nodes
/usr/bin/Get-Slices
/usr/bin/Get-Users
/usr/bin/Node-Setup
/usr/bin/Probe-Endpoint-Setup
/usr/bin/Random-Sleep
/usr/bin/Reset-Networking
/usr/bin/Routing-Rule-Setup
/usr/bin/System-Backup
/usr/bin/System-Info
/usr/bin/System-Maintenance
/usr/bin/Test-NTP-Configuration
/usr/bin/Watchdog
/usr/share/nornet/grub-defaults
/usr/share/man/man1/Auto-Update-Keys.1.gz
/usr/share/man/man1/Check-Nodes-Loop.1.gz
/usr/share/man/man1/Check-Nodes.1.gz
/usr/share/man/man1/Clear-SSH-Node-Key.1.gz
/usr/share/man/man1/Create-New-SSH-Node-Keys.1.gz
/usr/share/man/man1/Fingerprint-SSH-Node-Keys.1.gz
/usr/share/man/man1/Get-Nodes.1.gz
/usr/share/man/man1/Get-NorNet-Configuration.1.gz
/usr/share/man/man1/Get-Sites.1.gz
/usr/share/man/man1/Get-Slice-Nodes.1.gz
/usr/share/man/man1/Get-Slices.1.gz
/usr/share/man/man1/Get-Users.1.gz
/usr/share/man/man1/Node-Setup.1.gz
/usr/share/man/man1/Probe-Endpoint-Setup.1.gz
/usr/share/man/man1/Random-Sleep.1.gz
/usr/share/man/man1/Reset-Networking.1.gz
/usr/share/man/man1/Routing-Rule-Setup.1.gz
/usr/share/man/man1/System-Backup.1.gz
/usr/share/man/man1/System-Info.1.gz
/usr/share/man/man1/System-Maintenance.1.gz
/usr/share/man/man1/Test-NTP-Configuration.1.gz
/usr/share/man/man1/Watchdog.1.gz
/usr/share/man/man8/Interface-Setup.8.gz
/sbin/Interface-Setup

%post management
echo "Updating /etc/default/grub with NorNet settings:"
echo "-----"
cat /usr/share/nornet/grub-defaults | \
   ( if grep "biosdevname=0" >/dev/null 2>&1 /proc/cmdline ; then sed "s/^GRUB_CMDLINE_LINUX=\"/GRUB_CMDLINE_LINUX=\"biosdevname=0 /g" ; else cat ; fi ) | \
   ( if grep "net.ifnames=0" >/dev/null 2>&1 /proc/cmdline ; then sed "s/^GRUB_CMDLINE_LINUX=\"/GRUB_CMDLINE_LINUX=\"net.ifnames=0 /g" ; else cat ; fi ) | tee /etc/default/grub.new && \
mv /etc/default/grub.new /etc/default/grub
echo "-----"
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun management
rm -f /etc/grub.d/??_nornet_management_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package development
Summary: NorNet Development
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: autoconf
Requires: automake
Requires: banner
Requires: bison
Requires: bzip2-devel
Requires: clang
Requires: cmake
Requires: createrepo
Requires: debhelper
Requires: dejavu-sans-fonts
Requires: dejavu-sans-mono-fonts
Requires: dejavu-serif-fonts
Requires: devscripts
Requires: flex
Requires: gcc
Requires: gcc-c++
Requires: gdb
Requires: ghostscript
Requires: gimp
Requires: glib2-devel
Requires: gnupg
Requires: gnuplot
Requires: google-noto-cjk-fonts
Requires: google-noto-sans-fonts
Requires: google-noto-serif-fonts
Requires: GraphicsMagick
Requires: libcurl-devel
Requires: libpcap-devel
Requires: libtool
Requires: lksctp-tools-devel
Requires: make
Requires: mock
Requires: openssl-devel
Requires: pbuilder
Requires: perl-Image-ExifTool
Requires: pkg-config
Requires: python3
Requires: python3-psycopg2
Requires: python3-pymongo
Requires: qt5-qtbase-devel
Requires: quilt
Requires: R-base
Requires: rpm
Requires: texlive-epstopdf-bin
Requires: urw-base35-fonts
Requires: valgrind

%description development
This metapackage contains basic software nor NorNet development. The
software installed provides a common working environment.
See https://www.nntb.no for details on NorNet!

%files development
/boot/NorNet/Development1-1024x768.jpeg
/etc/grub.d/??_nornet_development_theme
/usr/share/nornet/pbuilderrc

%post development
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun development
rm -f /etc/grub.d/??_nornet_development_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package api
Summary: NorNet API
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}

%description api
This package contains the NorNet Python API library. It contains functions
to communicate with the central server (MyPLC), based on XMLRPC.
See https://www.nntb.no for details on NorNet!

%files api
/usr/lib/python*/*-packages/NorNet*.egg-info
/usr/lib/python*/*-packages/NorNetAPI.py
/usr/lib/python*/*-packages/NorNetConfiguration.py
/usr/lib/python*/*-packages/NorNetExperimentToolbox.py
/usr/lib/python*/*-packages/NorNetNodeSetup.py
/usr/lib/python*/*-packages/NorNetProviderSetup.py
/usr/lib/python*/*-packages/NorNetSiteSetup.py
/usr/lib/python*/*-packages/NorNetTools.py
/usr/lib/python*/*-packages/SysSetupCommons.py
/usr/lib/python*/*-packages/__pycache__/NorNetAPI*.pyc
/usr/lib/python*/*-packages/__pycache__/NorNetConfiguration*.pyc
/usr/lib/python*/*-packages/__pycache__/NorNetExperimentToolbox*.pyc
/usr/lib/python*/*-packages/__pycache__/NorNetNodeSetup*.pyc
/usr/lib/python*/*-packages/__pycache__/NorNetProviderSetup*.pyc
/usr/lib/python*/*-packages/__pycache__/NorNetSiteSetup*.pyc
/usr/lib/python*/*-packages/__pycache__/NorNetTools*.pyc
/usr/lib/python*/*-packages/__pycache__/SysSetupCommons*.pyc
/usr/share/nornet-api/nornetapi-config.full
/usr/share/nornet-api/nornetapi-config.simple
/usr/share/nornet-api/nornetapi-constants

%post api
mkdir -p /etc/nornet
if [ ! -e /etc/nornet/nornetapi-constants ] ; then
   cp /usr/share/nornet-api/nornetapi-constants /etc/nornet/nornetapi-constants
fi

if [ ! -e /etc/nornet/nornetapi-config ] ; then
   cp /usr/share/nornet-api/nornetapi-config.simple /etc/nornet/nornetapi-config.EXAMPLE
fi


%package node
Summary: NorNet Node
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: fail2ban
Requires: grub2
Requires: libvirt-client
Requires: nfs-utils
Requires: ntp
Requires: openssh-server
Requires: xorg-x11-xauth
Recommends: rsplib-services
Recommends: open-vm-tools
Recommends: virtualbox-guest-additions

%description node
This package contains the scripts to configure a generic node on a NorNet
site.
See https://www.nntb.no for details on NorNet!

%files node
/boot/NorNet/Node1-1024x768.jpeg
/etc/grub.d/??_nornet_node_theme
/usr/bin/Make-Node-Configuration
/usr/share/man/man1/Make-Node-Configuration.1.gz

%post node
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun node
rm -f /etc/grub.d/??_nornet_node_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%package tunnelbox
Summary: NorNet Tunnelbox
Group: Applications/Internet
BuildArch: noarch
Requires: (%{name}-node = %{version}-%{release} or %{name}-server = %{version}-%{release})
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: arpwatch
Requires: bind
Requires: conntrack-tools
Requires: dhcp-server
Requires: iptables
Requires: iputils
Requires: net-snmp
Requires: netstat-nat
Requires: ntp
Requires: radvd
Requires: squid
Requires: traceroute

%description tunnelbox
This package contains the scripts to configure the tunnelboxes of NorNet
sites.
See https://www.nntb.no for details on NorNet!

%files tunnelbox
/boot/NorNet/Tunnelbox1-1024x768.jpeg
/etc/grub.d/??_nornet_tunnelbox_theme
/usr/bin/Flush-Squid-Cache
/usr/bin/Make-Tunnelbox-Configuration
/usr/bin/Probe-Interface-Setup
/usr/bin/Tunnelbox-Bootstrap-Helper
/usr/bin/Tunnelbox-NAT-Helper
/usr/bin/Tunnelbox-Setup
/usr/share/man/man1/Make-Tunnelbox-Configuration.1.gz
/usr/share/man/man1/Probe-Interface-Setup.1.gz
/usr/share/man/man1/Tunnelbox-Bootstrap-Helper.1.gz
/usr/share/man/man1/Tunnelbox-NAT-Helper.1.gz
/usr/share/man/man1/Tunnelbox-Setup.1.gz
/usr/share/man/man1/Flush-Squid-Cache.1.gz


%post tunnelbox
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun tunnelbox
rm -f /etc/grub.d/??_nornet_tunnelbox_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%package artwork
Summary: NorNet Artwork
Group: Applications/Internet
BuildArch: noarch

%description artwork
This package contains some images for the monitor server
on a NorNet central site.
See https://www.nntb.no for details on NorNet!

%files artwork
/var/www/Artwork/Graphics/Backgrounds/*.png
/var/www/Artwork/Graphics/Control/*.png
/var/www/Artwork/Graphics/Flags/*.png
/var/www/Artwork/Graphics/Flags/*.svg
/var/www/Artwork/Graphics/Icons/*.png
/var/www/Artwork/Graphics/Markers/*.svg
/var/www/Artwork/Sites/Large/*.jpeg
/var/www/Artwork/Sites/Small/*.jpeg


%package monitor
Summary: NorNet Monitor
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-api = %{version}-%{release}
Requires: %{name}-artwork = %{version}-%{release}
Requires: %{name}-management = %{version}-%{release}
Requires: httpd
Requires: mod_php
Requires: nagios
Requires: postfix

%description monitor
This package contains the scripts to configure a generic monitoring station
on a NorNet central site.
See https://www.nntb.no for details on NorNet!

%files monitor
/boot/NorNet/Monitor1-1024x768.jpeg
/etc/grub.d/??_nornet_monitor_theme
/etc/nornet/nornet-commands.cfg
/etc/nornet/nornet-services.cfg
/usr/bin/Make-Monitor-Configuration
/usr/bin/check_site
/usr/bin/check_tunnel
/usr/share/man/man1/Make-Monitor-Configuration.1.gz
/usr/share/man/man1/check_site.1.gz
/var/www/Kontrollsenter/*
/var/www/Kontrollsenter/Clock/*
/var/www/Kontrollsenter/UnifrakturCook/*
/var/www/Kontrollsenter/UnifrakturCook/sources/*

%post monitor
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun monitor
rm -f /etc/grub.d/??_nornet_monitor_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%package display
Summary: NorNet Display
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Recommends: xorg-x11-drv-vmware

%description display
This package contains the packages to set up a display station for the
results of the monitoring station. It is in fact just a node with a web
browser and the necessary GUI.
See https://www.nntb.no for details on NorNet!

%files display
/boot/NorNet/Display1-1024x768.jpeg
/etc/grub.d/??_nornet_display_theme
/usr/share/nornet-desktop/Desktop-with-Logo/*
/usr/share/nornet-desktop/Desktop-without-Logo/*
/usr/share/nornet-desktop/NorNet-A4.pdf

%post display
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun display
rm -f /etc/grub.d/??_nornet_display_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package gatekeeper
Summary: NorNet Gatekeeper
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: fail2ban

%description gatekeeper
This package contains the packages to set up a gatekeeper station for the
project presentation. It is in fact just a node with a dependency on the
additional packages.
See https://www.nntb.no for details on NorNet!

%files gatekeeper
/boot/NorNet/Gatekeeper1-1024x768.jpeg
/etc/grub.d/??_nornet_gatekeeper_theme

%post gatekeeper
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun gatekeeper
rm -f /etc/grub.d/??_nornet_gatekeeper_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package websrv
Summary: NorNet WebSrv
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: awstats
Requires: geoipupdate-cron
Requires: geoipupdate-cron6
Requires: GeoIP-GeoLite-data
Requires: GeoIP-GeoLite-data-extra
Requires: httpd
Requires: mod_php
Requires: oxygen-icon-theme

%description websrv
This package contains the packages to set up a web server station for the
project presentation. It is in fact just a node with a dependency on the
Apache packages.
See https://www.nntb.no for details on NorNet!

%files websrv
/boot/NorNet/WebSrv1-1024x768.jpeg
/etc/grub.d/??_nornet_websrv_theme
/usr/share/nornet-websrv/*

%post websrv
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun websrv
rm -f /etc/grub.d/??_nornet_websrv_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package wikisrv
Summary: NorNet WikiSrv
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-websrv = %{version}-%{release}
Requires: postfix
Requires: php-mysqlnd

%description wikisrv
This package contains the packages to set up a wiki station for the
user-contributed documentation. It is in fact just a node with a
dependency on the MediaWiki packages.
See https://www.nntb.no for details on NorNet!

%files wikisrv
/boot/NorNet/WikiSrv1-1024x768.jpeg
/etc/grub.d/??_nornet_wikisrv_theme

%post wikisrv
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun wikisrv
rm -f /etc/grub.d/??_nornet_wikisrv_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package timesrv
Summary: NorNet TimeSrv
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: ntp

%description timesrv
This package contains the packages to set up an NTP server.
See https://www.nntb.no for details on NorNet!

%files timesrv
/boot/NorNet/TimeSrv1-1024x768.jpeg
/etc/grub.d/??_nornet_timesrv_theme

%post timesrv
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun timesrv
rm -f /etc/grub.d/??_nornet_timesrv_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package database
Summary: NorNet Database
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: postgresql-server
Requires: postgresql-contrib

%description database
This package contains the packages to set up a database station for
experiment results collection. It is in fact just a node with a
dependency on the PostgreSQL packages.
See https://www.nntb.no for details on NorNet!

%files database
/boot/NorNet/Database1-1024x768.jpeg
/etc/grub.d/??_nornet_database_theme

%post database
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun database
rm -f /etc/grub.d/??_nornet_database_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package plc
Summary: NorNet PLC
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Recommends: myplc

%description plc
This package contains the packages to set up a PLC server.
See https://www.nntb.no for details on NorNet!

%files plc
/boot/NorNet/PLC1-1024x768.jpeg
/etc/grub.d/??_nornet_plc_theme

%post plc
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun plc
rm -f /etc/grub.d/??_nornet_plc_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%package server
Summary: NorNet Server
Group: Applications/Internet
BuildArch: noarch
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: fail2ban
Requires: grub2
Requires: libvirt-client
Requires: nfs-utils
Requires: ntp
Requires: openssh-server
Requires: qemu-kvm
Requires: virt-manager
Requires: virt-install
Requires: xorg-x11-xauth

%description server
This package contains the scripts to configure a generic server system
to host NorNet virtual machines.
See https://www.nntb.no for details on NorNet!

%files server
/boot/NorNet/Server1-1024x768.jpeg
/etc/nornet/vsystems/EXAMPLE-99-VirtualServer
/etc/grub.d/??_nornet_server_theme
/usr/bin/Auto-Update-BootCD
/usr/bin/Backup-All-VSystems
/usr/bin/Backup-VSystem
/usr/bin/Change-VSystem-CDImage
/usr/bin/Check-Research-Node
/usr/bin/Check-VSystem
/usr/bin/Convert-HDD-Images
/usr/bin/Make-Server-Configuration
/usr/bin/Make-VSystem-Template
/usr/bin/Reset-VSystem
/usr/bin/Server-Setup
/usr/bin/Server-Watchdog
/usr/bin/Set-OVF-Type
/usr/bin/Show-VSystems
/usr/bin/Start-VSystem
/usr/bin/Stop-VSystem
/usr/share/man/man1/Auto-Update-BootCD.1.gz
/usr/share/man/man1/Backup-All-VSystems.1.gz
/usr/share/man/man1/Backup-VSystem.1.gz
/usr/share/man/man1/Change-VSystem-CDImage.1.gz
/usr/share/man/man1/Check-Research-Node.1.gz
/usr/share/man/man1/Check-VSystem.1.gz
/usr/share/man/man1/Convert-HDD-Images.1.gz
/usr/share/man/man1/Make-Server-Configuration.1.gz
/usr/share/man/man1/Make-VSystem-Template.1.gz
/usr/share/man/man1/Reset-VSystem.1.gz
/usr/share/man/man1/Server-Setup.1.gz
/usr/share/man/man1/Server-Watchdog.1.gz
/usr/share/man/man1/Set-OVF-Type.1.gz
/usr/share/man/man1/Show-VSystems.1.gz
/usr/share/man/man1/Start-VSystem.1.gz
/usr/share/man/man1/Stop-VSystem.1.gz
/usr/share/nornet-server/watchdog-config.example

%post server
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi


%postun server
rm -f /etc/grub.d/??_nornet_server_theme
if [ -e /usr/sbin/grub2-mkconfig ] ; then /usr/sbin/grub2-mkconfig -o /boot/grub2/grub.cfg || true ; fi



%changelog
* Fri Nov 16 2018 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.0.0
- Created RPM package.
