Name: nornet
Version: 1.3.0
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
Requires: netperfmeter
Requires: net-snmp-utils
Requires: net-tools
Requires: nmap
Requires: ntpdate
Requires: pxz
Requires: reiserfs-utils
Requires: reprepro
Requires: smartmontools
Requires: sslscan
Requires: subnetcalc
Requires: tcpdump
Requires: tftp
Requires: traceroute
Requires: tree
Requires: vconfig
Requires: virt-what
Requires: whois
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
/etc/grub.d/??_nornet_development_theme
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
/sbin/Interface-Setup

%post management
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun management
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package development
Summary: NorNet Development
Group: Applications/Internet
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
/etc/pbuilderrc

%post development
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun development
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package api
Summary: NorNet API
Group: Applications/Internet
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
/usr/share/doc/nornet-api/examples/nornetapi-config.full
/usr/share/doc/nornet-api/examples/nornetapi-config.simple
/usr/share/doc/nornet-api/examples/nornetapi-constants

%post api
mkdir -p /etc/nornet
if [ ! -e /etc/nornet/nornetapi-constants ] ; then
   cp /usr/share/doc/nornet-api/examples/nornetapi-constants /etc/nornet/nornetapi-constants
fi

if [ ! -e /etc/nornet/nornetapi-config ] ; then
   cp /usr/share/doc/nornet-api/examples/nornetapi-config.simple /etc/nornet/nornetapi-config.EXAMPLE
fi


%package node
Summary: NorNet Node
Group: Applications/Internet
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: fail2ban
Requires: grub2
Requires: libvirt-bin
Requires: nfs-utils
Requires: ntp
Requires: openssh-server
Requires: rsplib-services
Requires: xorg-x11-xauth
Recommends: open-vm-tools
Recommends: virtualbox-guest-additions
Conflicts: %{name}-server

%description node
This package contains the scripts to configure a generic node on a NorNet
site.
See https://www.nntb.no for details on NorNet!

%files node
/boot/NorNet/Node1-1024x768.jpeg
/etc/grub.d/??_nornet_node_theme
/usr/bin/Make-Node-Configuration
/usr/share/nornet/grub-defaults

%post node
cp /etc/nornet/grub-defaults /etc/default/grub
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun node
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package artwork
Summary: NorNet Artwork
Group: Applications/Internet

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


%package display
Summary: NorNet Display
Group: Applications/Internet
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
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun display
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package gatekeeper
Summary: NorNet Gatekeeper
Group: Applications/Internet
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
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun gatekeeper
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package websrv
Summary: NorNet WebSrv
Group: Applications/Internet
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: awstats
Requires: GeoIP-GeoLite-data
Requires: GeoIP-GeoLite-data-extra
Requires: httpd
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
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun websrv
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package wikisrv
Summary: NorNet WikiSrv
Group: Applications/Internet
Requires: %{name}-websrv = %{version}-%{release}
Requires: postfix

%description wikisrv
This package contains the packages to set up a wiki station for the
user-contributed documentation. It is in fact just a node with a
dependency on the MediaWiki packages.
See https://www.nntb.no for details on NorNet!

%files wikisrv
/boot/NorNet/WikiSrv1-1024x768.jpeg
/etc/grub.d/??_nornet_wikisrv_theme

%post wikisrv
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun wikisrv
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package timesrv
Summary: NorNet TimeSrv
Group: Applications/Internet
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
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun timesrv
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package database
Summary: NorNet Database
Group: Applications/Internet
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
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun database
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package plc
Summary: NorNet PLC
Group: Applications/Internet
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
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun plc
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%package server
Summary: NorNet Server
Group: Applications/Internet
Requires: %{name}-management = %{version}-%{release}
Requires: %{name}-api = %{version}-%{release}
Requires: fail2ban
Requires: grub2
Requires: libvirt-bin
Requires: nfs-utils
Requires: ntp
Requires: openssh-server
Requires: qemu-kvm
Requires: virt-manager
Requires: virt-install
Requires: xorg-x11-xauth
Conflicts: %{name}-node

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
/usr/share/nornet-server/watchdog-config.example
/usr/share/nornet/grub-defaults

%post server
cp /etc/nornet/grub-defaults /etc/default/grub
cp /usr/share/nornet/grub-defaults /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg

%postun server
rm -f /etc/grub.d/??_nornet_desktop_theme
grub2-mkconfig -o /boot/grub2/grub.cfg


%changelog
* Fri Nov 16 2018 Thomas Dreibholz <dreibh@iem.uni-due.de> - 0.0.0
- Created RPM package.
