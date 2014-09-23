%global prog cfengine
%global cfdir %{_var}/%{prog}

Name:      cfengine
Version:   3.5.3
Release:   1%{?dist}
Summary:   CFEngine 3

Group:     Applications/System
License:   GPLv3
URL:       http://cfengine.com/source-code/download?file=

Source0:   %{prog}-%{version}.tar.gz
Source1:   cf-execd
Source2:   cf-execd.service
#Source3:   root-MD5=d6d7ced4347d09e7b89fad304dc2a51b.pub
#Source4:   root-MD5=d4daf8b22ab56fa0aab0e8c1dc698035.pub
#Source5:   failsafe.cf
#Source6:   only-one-cfexecd.cron
Source7:   cf-serverd
Source8:   cf-serverd.service
Source9:   cf-serverd.sysconfig
#Source10:  root-MD5=ef542846eaf45bb3511a0b0dfbd6e8bb.pub
#Source11:  cf-key
#Source12:  cf-key.service

%if 0%{?fedora} > 17 || 0%{?rhel} > 6
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
BuildRequires:    systemd
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
%endif

Requires:  redhat-lsb
Conflicts: cfengine

BuildRequires: tokyocabinet-devel
BuildRequires: openssl-devel
BuildRequires: bison
BuildRequires: flex
BuildRequires: m4
BuildRequires: libacl-devel
BuildRequires: tetex-dvips
BuildRequires: texinfo-tex
BuildRequires: pcre-devel
BuildRequires: libxml2-devel
BuildRequires: chrpath

#%global key1_ipv4 root-129.240.2.47.pub
#%global key1_ipv6 root-2001:700:100:425::47.pub
#%global key1_md5  root-MD5=d6d7ced4347d09e7b89fad304dc2a51b.pub

#%global key2_ipv4 root-129.240.2.78.pub
#%global key2_ipv6 root-2001:700:100:540::78.pub
#%global key2_md5  root-MD5=d4daf8b22ab56fa0aab0e8c1dc698035.pub

# TSD
#%global key3_ipv6 root-2001:700:111:1::cf01.pub
#%global key3_md5  root-MD5=ef542846eaf45bb3511a0b0dfbd6e8bb.pub

%description
CFEngine, or the configuration engine is an agent/software robot and a
very high level language for building expert systems to administrate
and configure large computer networks. CFEngine uses the idea of
classes and a primitive form of intelligence to define and automate
the configuration and maintenance of system state, for small to huge
configurations. CFEngine is designed to be a part of a computer immune
system. This package contains CFEngine and bootstrap files for UiO.


%package server
Summary:   Server component for CFEngine
Group:     Applications/System
Requires:  %{name} = %{version}-%{release}
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
%else
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig, /sbin/service
Requires(postun): /sbin/service
%endif
BuildArch: noarch

%description server
This package contains a SysV initscript or systemd unit file for
cf-serverd (CFEngine server daemon).

%package doc
Summary:   Documentation for CFEngine
Group:     Documentation
Requires:  %{name} = %{version}-%{release}
BuildArch: noarch

%description doc
This package contains the documentation for CFEngine.


%prep
%setup -q -n %{prog}-%{version}


%build
%configure --disable-shared
make %{?_smp_mflags}


%install
# Make install
make DESTDIR=%{buildroot} install

# Creating dirs
#mkdir -p %{buildroot}/opt/%{prog}/{sbin,inputs,ppkeys}
mkdir -p %{buildroot}/%{_defaultdocdir}/%{prog}

# Moving binaries
mv %{buildroot}/%{_bindir} %{buildroot}/%{_sbindir}

# Remove RPATH from binaries
chrpath -d %{buildroot}/%{_sbindir}/*

# Moving things around
mv %{buildroot}/%{_defaultdocdir}/examples %{buildroot}/%{_defaultdocdir}/%{prog}
mv %{buildroot}/%{_datadir}/CoreBase %{buildroot}/%{_defaultdocdir}/%{prog}

# Remove other installed items
rm -rf %{buildroot}/%{_var}

# Putting binaries in /var
mkdir -p %{buildroot}/var/%{prog}/bin
cp -a %{buildroot}/%{_sbindir}/* %{buildroot}/var/%{prog}/bin

# Server public keys
#install -p -m 0600 %{SOURCE3} %{buildroot}/opt/%{prog}/ppkeys/%{key1_md5}
#install -p -m 0600 %{SOURCE3} %{buildroot}/opt/%{prog}/ppkeys/%{key1_ipv4}
#install -p -m 0600 %{SOURCE3} %{buildroot}/opt/%{prog}/ppkeys/%{key1_ipv6}
#install -p -m 0600 %{SOURCE4} %{buildroot}/opt/%{prog}/ppkeys/%{key2_md5}
#install -p -m 0600 %{SOURCE4} %{buildroot}/opt/%{prog}/ppkeys/%{key2_ipv4}
#install -p -m 0600 %{SOURCE4} %{buildroot}/opt/%{prog}/ppkeys/%{key2_ipv6}
#install -p -m 0600 %{SOURCE10} %{buildroot}/opt/%{prog}/ppkeys/%{key3_md5}
#install -p -m 0600 %{SOURCE10} %{buildroot}/opt/%{prog}/ppkeys/%{key3_ipv6}

# Failsafe config
#install -p -m 0600 %{SOURCE5} %{buildroot}/opt/%{prog}/inputs/

# Remove some stuff we don't want
rm -f %{buildroot}/%{_defaultdocdir}/{ChangeLog,README.md}
rm -rf %{buildroot}/usr/lib

# Init script
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
mkdir -p %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE2} %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE8} %{buildroot}%{_unitdir}
#install -p -m 0644 %{SOURCE12} %{buildroot}%{_unitdir}
%else
mkdir -p %{buildroot}%{_initddir}
install -p -m 0755 %{SOURCE1} %{buildroot}%{_initddir}
install -p -m 0755 %{SOURCE7} %{buildroot}%{_initddir}
#install -p -m 0755 %{SOURCE11} %{buildroot}%{_initddir}
%endif

# Sysconfig file for cf-serverd
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 0644 %{SOURCE9} %{buildroot}%{_sysconfdir}/sysconfig/cf-serverd

# Cron job
#mkdir -p %{buildroot}%{_sysconfdir}/cron.hourly
#install -p -m 0755 %{SOURCE6} %{buildroot}%{_sysconfdir}/cron.hourly

# 3.5.2 man pages BUG!
install -d -m 0755 %{buildroot}/%{_mandir}/man8
for i in cf-agent cf-execd cf-key cf-monitord cf-promises cf-runagent cf-serverd; do
    %{buildroot}/%{_sbindir}/$i -M > %{buildroot}/%{_mandir}/man8/$i.8
done


%post
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
# The services should be enabled by default
/usr/bin/systemctl daemon-reload >/dev/null 2>&1 || :
/usr/bin/systemctl enable cf-execd.service >/dev/null 2>&1 || :
#/usr/bin/systemctl enable cf-key.service >/dev/null 2>&1 || :
%else
# The services should be enabled by default
if [ $1 -eq 1 ] ; then
    # Initial installation
    # This adds the proper /etc/rc*.d links for the script
    /sbin/chkconfig --add cf-execd
#    /sbin/chkconfig --add cf-key
fi
# This turns on the service
/sbin/chkconfig cf-execd on >/dev/null 2>&1 || :
#/sbin/chkconfig cf-key on >/dev/null 2>&1 || :
%endif

# Remove obsolete/unused keys
#rm %{cfdir}/ppkeys/root-{,129.240.2.19}.pub >/dev/null 2>&1 || :

# Copy keys if needed
#mkdir -p %{cfdir}/ppkeys >/dev/null 2>&1 || :
#CLEAN_TCDB_FILES=0
#for KEY in $(ls /opt/%{prog}/ppkeys); do
#    if [ ! -f %{cfdir}/ppkeys/$KEY ]; then
#        cp /opt/%{prog}/ppkeys/$KEY %{cfdir}/ppkeys
#        CLEAN_TCDB_FILES=1
#    fi
#done

# Clean tcdb files if keys changed
#if [ $CLEAN_TCDB_FILES -eq 1 ]; then
#    rm %{cfdir}/*.tcdb >/dev/null 2>&1 || :
#fi

# Clean old db4 cache files
#rm %{cfdir}/*.db >/dev/null 2>&1 || :
#rm %{cfdir}/state/*.db >/dev/null 2>&1 || :

%preun
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%systemd_preun cf-execd.service
#%systemd_preun cf-key.service
%else
if [ $1 = 0 ] ; then
    # Actual deinstallation of package (not upgrade)
    /sbin/service cf-execd stop >/dev/null 2>&1
    /sbin/chkconfig --del cf-execd
#    /sbin/service cf-key stop >/dev/null 2>&1
#    /sbin/chkconfig --del cf-key
fi
%endif

%postun
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%systemd_postun_with_restart cf-execd.service
#%systemd_postun cf-key.service
%else
if [ "$1" -ge "1" ] ; then
    # Upgrade of package
    /sbin/service cf-execd condrestart >/dev/null 2>&1 || :
fi
%endif


%post server
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%systemd_post cf-serverd.service
%else
if [ $1 -eq 1 ] ; then
    # This adds the proper /etc/rc*.d links for the script
    /sbin/chkconfig --add cf-serverd
fi
%endif

%preun server
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%systemd_preun cf-serverd.service
%else
if [ $1 = 0 ] ; then
    # Actual deinstallation of package (not upgrade)
    /sbin/service cf-serverd stop >/dev/null 2>&1
    /sbin/chkconfig --del cf-serverd
fi
%endif

%postun server
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%systemd_postun_with_restart cf-serverd.service
%else
if [ "$1" -ge "1" ] ; then
    # Upgrade of package
    /sbin/service cf-serverd condrestart >/dev/null 2>&1 || :
fi
%endif


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog README.md
#%dir /opt/%{prog}
%dir /var/%{prog}/bin
/var/%{prog}/bin/*
%{_sbindir}/*
%{_mandir}/man8/*
#/opt/%{prog}/sbin/*
#/opt/%{prog}/ppkeys/*.pub
#/opt/%{prog}/inputs/*.cf
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%{_unitdir}/cf-execd.service
#%{_unitdir}/cf-key.service
%else
%{_initddir}/cf-execd
#%{_initddir}/cf-key
%endif
#%{_sysconfdir}/cron.hourly/only-one-cfexecd.cron

%files server
%config(noreplace) %{_sysconfdir}/sysconfig/cf-serverd
%if 0%{?fedora} > 17 || 0%{?rhel} > 6
%{_unitdir}/cf-serverd.service
%else
%{_initddir}/cf-serverd
%endif

%files doc
%defattr(-,root,root,-)
%{_defaultdocdir}/%{prog}


%changelog
* Mon Jan 06 2014 Jarle Bjørgeengen <jarle@simula.no> - 3.5.2
  - Initial upstream package

