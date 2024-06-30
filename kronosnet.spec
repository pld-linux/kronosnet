#
# Conditional build:
%bcond_without	static_libs	# static libraries
%bcond_with	kronosnetd	# build daemon (broken as of 1.7)
#
Summary:	Multipoint-to-Multipoint VPN library
Summary(pl.UTF-8):	Biblioteka VPN wiele-do-wielu
Name:		kronosnet
Version:	1.29
Release:	2
License:	LGPL v2.1+ (libraries), GPL v2+ (applications)
Group:		Libraries
Source0:	https://kronosnet.org/releases/%{name}-%{version}.tar.xz
# Source0-md5:	d95a5870ce35ddd12e6cd7a783c0b202
Patch0:		x32.patch
URL:		https://kronosnet.org/
BuildRequires:	bzip2-devel
BuildRequires:	doxygen
BuildRequires:	gcc >= 5:3.2
BuildRequires:	libnl-devel >= 3.3
BuildRequires:	libqb-devel
BuildRequires:	libsctp-devel
BuildRequires:	libxml2-devel >= 2.0
BuildRequires:	lz4-devel
BuildRequires:	lzo-devel >= 2
BuildRequires:	nss-devel
BuildRequires:	openssl-devel >= 1.1
%{?with_kronosnetd:BuildRequires:	pam-devel}
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	xz-devel
BuildRequires:	zlib-devel
BuildRequires:	zstd-devel
Requires:	libnl >= 3.3
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Multipoint-to-Multipoint VPN library.

%description -l pl.UTF-8
Biblioteka VPN wiele-do-wielu.

%package devel
Summary:	Header files for kronosnet libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek kronosnet
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for kronosnet libraries.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek kronosnet.

%package static
Summary:	Static kronosnet libraries
Summary(pl.UTF-8):	Statyczne biblioteki kronosnet
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static kronosnet libraries.

%description static -l pl.UTF-8
Statyczne biblioteki kronosnet.

%package -n kronosnetd
Summary:	Multipoint-to-Multipoint VPN daemon
Summary(pl.UTF-8):	Demon VPN wiele-do-wielu
Group:		Networking/Daemons
Provides:	group(kronosnetadm)
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires(postun):	/usr/sbin/groupdel
Requires:	%{name} = %{version}-%{release}
Requires:	systemd-units >= 0.38

%description -n kronosnetd
The kronosnet daemon is a bridge between kronosnet switching engine
and kernel network tap devices, to create and administer a distributed
LAN over multipoint-to-multipoint VPNs. The daemon does a poor attempt
to provide a configure UI similar to other known network devices/tools
(Cisco, quagga). Beside looking horrific, it allows runtime changes
and reconfiguration of the kronosnet(s) without daemon reload or
service disruption.

NOTE: it's experminental and unfinished.

%description -n kronosnetd -l pl.UTF-8
Demon kronosnet to pomost między silnikiem przełącznika kronosnet i
urządzeniami sieciowym tap w jądrze, pozwalający na tworzenie i
administrowanie rozproszoną siecią LAN po VPN-ach wiele-do-wielu.
Demon (kiepsko) próbuje udostępniać interfejs konfiguracyjny podobny
do innych urządzeń/narzędzi sieciowych (Cisco, quagga). Poza
przerażającym wyglądem pozwala na modyfikowanie i rekonfigurację sieci
kronosnet bez przeładowywania demona czy przerwach w działaniu usługi.

UWAGA: to oprogramowanie jest eksperymentalne i nie dokończone.

%prep
%setup -q
%patch0 -p1

%build
%configure \
	%{?with_kronosnetd:--enable-kronosnetd} \
	%{!?with_static_libs:--disable-static} \
	--with-initddir=/etc/rc.d/init.d \
	--with-initdefaultdir=/etc/sysconfig \
	--with-systemddir=%{systemdunitdir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# obsoleted by pkg-config
%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la
# dlopened modules
%{__rm} $RPM_BUILD_ROOT%{_libdir}/kronosnet/*.la
%if %{with static_libs}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/kronosnet/*.a
%endif
# COPYING.* files are generic (GPL v2, LGPL v2.1 from common-licenses), the rest is packaged as %doc
%{__rm} $RPM_BUILD_ROOT%{_docdir}/kronosnet/{COPYING.*,COPYRIGHT,README*}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%pre	-n kronosnetd
# TODO: register GID, enter number here
%groupadd -g GID kronosnetadm

%post	-n kronosnetd
%systemd_post kronosnetd.service
/sbin/chkconfig --add kronosnetd
%service kronosnetd restart

%preun	-n kronosnetd
%systemd_preun kronosnetd.service
if [ "$1" = "0" ]; then
	%service -q kronosnetd stop
	/sbin/chkconfig --del kronosnetd
fi

%postun	-n kronosnetd
%systemd_reload
if [ "$1" = "0" ]; then
	%groupremove kronosnetadm
fi

%files
%defattr(644,root,root,755)
%doc COPYRIGHT ChangeLog README README.licence
%attr(755,root,root) %{_libdir}/libknet.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libknet.so.1
%attr(755,root,root) %{_libdir}/libnozzle.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libnozzle.so.1
%dir %{_libdir}/kronosnet
%attr(755,root,root) %{_libdir}/kronosnet/compress_bzip2.so
%attr(755,root,root) %{_libdir}/kronosnet/compress_lz4.so
%attr(755,root,root) %{_libdir}/kronosnet/compress_lz4hc.so
%attr(755,root,root) %{_libdir}/kronosnet/compress_lzma.so
%attr(755,root,root) %{_libdir}/kronosnet/compress_lzo2.so
%attr(755,root,root) %{_libdir}/kronosnet/compress_zlib.so
%attr(755,root,root) %{_libdir}/kronosnet/compress_zstd.so
%attr(755,root,root) %{_libdir}/kronosnet/crypto_nss.so
%attr(755,root,root) %{_libdir}/kronosnet/crypto_openssl.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libknet.so
%attr(755,root,root) %{_libdir}/libnozzle.so
%{_includedir}/libknet.h
%{_includedir}/libnozzle.h
%{_pkgconfigdir}/libknet.pc
%{_pkgconfigdir}/libnozzle.pc
%{_mandir}/man3/knet_*.3*
%{_mandir}/man3/nozzle_*.3*

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libknet.a
%{_libdir}/libnozzle.a
%endif

%if %{with kronosnetd}
%files -n kronosnetd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/kronosnetd
%dir %{_sysconfdir}/kronosnet
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/kronosnetd
%config(noreplace) %verify(not md5 mtime size) /etc/pam.d/kronosnetd
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/kronosnetd
%attr(754,root,root) /etc/rc.d/init.d/kronosnetd
%{systemdunitdir}/kronosnetd.service
%{_mandir}/man8/kronosnetd.8*
%endif
