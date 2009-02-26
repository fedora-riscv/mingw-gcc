%define __os_install_post /usr/lib/rpm/brp-compress %{nil}

%define DATE 20090216
%define SVNREV 144214

Name:           mingw32-gcc
Version:        4.4.0
Release:        0.5%{?dist}
Summary:        MinGW Windows cross-compiler (GCC) for C

License:        GPLv3+ and GPLv2+ with exceptions
Group:          Development/Languages

# We use the same source as Fedora's native gcc.
URL:            http://gcc.gnu.org
Source0:        gcc-%{version}-%{DATE}.tar.bz2
Source1:        libgcc_post_upgrade.c
Source2:        README.libgcjwebplugin.so
Source3:        protoize.1
Source5:        ftp://gcc.gnu.org/pub/gcc/infrastructure/cloog-ppl-0.15.tar.gz

# Patches from Fedora's native gcc.
Patch0:         gcc44-hack.patch
Patch1:         gcc44-build-id.patch
Patch2:         gcc44-c++-builtin-redecl.patch
Patch3:         gcc44-ia64-libunwind.patch
Patch4:         gcc44-java-nomulti.patch
Patch5:         gcc44-ppc32-retaddr.patch
Patch7:         gcc44-pr27898.patch
Patch8:         gcc44-pr32139.patch
Patch9:         gcc44-pr33763.patch
Patch10:        gcc44-rh330771.patch
Patch11:        gcc44-rh341221.patch
Patch12:        gcc44-java-debug-iface-type.patch
Patch13:        gcc44-i386-libgomp.patch
Patch15:        gcc44-sparc-config-detection.patch
Patch16:        gcc44-libgomp-omp_h-multilib.patch
Patch20:        gcc44-libtool-no-rpath.patch
Patch21:        gcc44-cloog-dl.patch
Patch22:        gcc44-raw-string.patch
Patch23:        gcc44-pr39175.patch
Patch24:        gcc44-diff.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  texinfo
BuildRequires:  mingw32-filesystem >= 49
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-runtime
BuildRequires:  mingw32-w32api
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  libgomp
BuildRequires:  flex

# NB: Explicit mingw32-filesystem dependency is REQUIRED here.
Requires:       mingw32-filesystem >= 48

Requires:       mingw32-binutils
Requires:       mingw32-runtime
Requires:       mingw32-w32api
Requires:       mingw32-cpp

# We don't run the automatic dependency scripts which would
# normally detect and provide the following DLL:
Provides:       mingw32(libgcc_s_sjlj-1.dll)


%description
MinGW Windows cross-compiler (GCC) for C.


%package -n mingw32-cpp
Summary: MinGW Windows cross-C Preprocessor
Group: Development/Languages

%description -n mingw32-cpp
MinGW Windows cross-C Preprocessor


%package c++
Summary: MinGW Windows cross-compiler for C++
Group: Development/Languages
Requires: %{name} = %{version}-%{release}

%description c++
MinGW Windows cross-compiler for C++.


%package objc
Summary: MinGW Windows cross-compiler support for Objective C
Group: Development/Languages
Requires: %{name} = %{version}-%{release}
Requires: mingw32-libobjc = %{version}-%{release}

%description objc
MinGW Windows cross-compiler support for Objective C.


%package objc++
Summary: MinGW Windows cross-compiler support for Objective C++
Group: Development/Languages
Requires: %{name}-g++ = %{version}-%{release}
Requires: %{name}-objc = %{version}-%{release}

%description objc++
MinGW Windows cross-compiler support for Objective C++.


%package gfortran
Summary: MinGW Windows cross-compiler for FORTRAN
Group: Development/Languages
Requires: %{name} = %{version}-%{release}

%description gfortran
MinGW Windows cross-compiler for FORTRAN.


%prep
%setup -q -n gcc-%{version}-%{DATE}
%patch0 -p0 -b .hack~
%patch1 -p0 -b .build-id~
%patch2 -p0 -b .c++-builtin-redecl~
%patch3 -p0 -b .ia64-libunwind~
%patch4 -p0 -b .java-nomulti~
%patch5 -p0 -b .ppc32-retaddr~
%patch7 -p0 -b .pr27898~
%patch8 -p0 -b .pr32139~
%patch9 -p0 -b .pr33763~
%patch10 -p0 -b .rh330771~
%patch11 -p0 -b .rh341221~
%patch12 -p0 -b .java-debug-iface-type~
%patch13 -p0 -b .i386-libgomp~
%patch15 -p0 -b .sparc-config-detection~
%patch16 -p0 -b .libgomp-omp_h-multilib~
%patch20 -p0 -b .libtool-no-rpath~
%patch21 -p0 -b .cloog-dl~
%patch22 -p0 -b .raw-string~
%patch23 -p0 -b .pr39175~
%patch24 -p0 -b .diff~


%build
mkdir -p build
pushd build

# GNAT is required to build Ada.  Don't build GCJ.
#languages="c,c++,objc,obj-c++,java,fortran,ada"
languages="c,c++,objc,obj-c++,fortran"

CC="%{__cc} ${RPM_OPT_FLAGS}" \
../configure \
  --prefix=%{_prefix} \
  --bindir=%{_bindir} \
  --includedir=%{_includedir} \
  --libdir=%{_libdir} \
  --mandir=%{_mandir} \
  --infodir=%{_infodir} \
  --datadir=%{_datadir} \
  --build=%_build --host=%_host \
  --target=%{_mingw32_target} \
  --with-gnu-as --with-gnu-ld --verbose \
  --without-newlib \
  --disable-multilib \
  --with-system-zlib \
  --disable-nls --without-included-gettext \
  --disable-win32-registry \
  --enable-version-specific-runtime-libs \
  --with-sysroot=%{_mingw32_sysroot} \
  --enable-languages="$languages" \
  --with-bugurl=http://bugzilla.redhat.com/bugzilla

make all

popd


%install
rm -rf $RPM_BUILD_ROOT

pushd build
make DESTDIR=$RPM_BUILD_ROOT install

# These files conflict with existing installed files.
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty*
rm -f $RPM_BUILD_ROOT%{_mandir}/man7/*

mkdir -p $RPM_BUILD_ROOT/lib
ln -sf ..%{_prefix}/bin/i686-pc-mingw32-cpp \
  $RPM_BUILD_ROOT/lib/i686-pc-mingw32-cpp

# Not sure why gcc puts this DLL into _bindir, but surely better if
# it goes into _mingw32_bindir.
mkdir -p $RPM_BUILD_ROOT%{_mingw32_bindir}
mv $RPM_BUILD_ROOT%{_bindir}/libgcc_s_sjlj-1.dll \
  $RPM_BUILD_ROOT%{_mingw32_bindir}

# Don't want the *.la files.
find $RPM_BUILD_ROOT -name '*.la' -delete

popd


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root)
%{_bindir}/i686-pc-mingw32-gcc
%{_bindir}/i686-pc-mingw32-gcc-%{version}
%{_bindir}/i686-pc-mingw32-gccbug
%{_bindir}/i686-pc-mingw32-gcov
%{_prefix}/i686-pc-mingw32/lib/libiberty.a
%dir %{_libdir}/gcc/i686-pc-mingw32
%dir %{_libdir}/gcc/i686-pc-mingw32/%{version}
%{_libdir}/gcc/i686-pc-mingw32/%{version}/crtbegin.o
%{_libdir}/gcc/i686-pc-mingw32/%{version}/crtend.o
%{_libdir}/gcc/i686-pc-mingw32/%{version}/crtfastmath.o
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libgcc.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libgcc_eh.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libgcc_s.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libgcov.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libssp.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libssp_nonshared.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libssp.dll.a
%dir %{_libdir}/gcc/i686-pc-mingw32/%{version}/include
%dir %{_libdir}/gcc/i686-pc-mingw32/%{version}/include-fixed
%dir %{_libdir}/gcc/i686-pc-mingw32/%{version}/include/ssp
%{_libdir}/gcc/i686-pc-mingw32/%{version}/include-fixed/README
%{_libdir}/gcc/i686-pc-mingw32/%{version}/include-fixed/*.h
%{_libdir}/gcc/i686-pc-mingw32/%{version}/include/*.h
%{_libdir}/gcc/i686-pc-mingw32/%{version}/include/ssp/*.h
%dir %{_libdir}/gcc/i686-pc-mingw32/%{version}/install-tools
%{_libdir}/gcc/i686-pc-mingw32/%{version}/install-tools/*
%dir %{_libdir}/gcc/i686-pc-mingw32/bin/
%{_libdir}/gcc/i686-pc-mingw32/bin/libssp-0.dll
%dir %{_libexecdir}/gcc/i686-pc-mingw32/%{version}/install-tools
%{_libexecdir}/gcc/i686-pc-mingw32/%{version}/install-tools/*
%{_mingw32_bindir}/libgcc_s_sjlj-1.dll
%{_mandir}/man1/i686-pc-mingw32-gcc.1*
%{_mandir}/man1/i686-pc-mingw32-gcov.1*


%files -n mingw32-cpp
%defattr(-,root,root)
/lib/i686-pc-mingw32-cpp
%{_bindir}/i686-pc-mingw32-cpp
%{_mandir}/man1/i686-pc-mingw32-cpp.1*
%dir %{_libdir}/gcc/i686-pc-mingw32
%dir %{_libdir}/gcc/i686-pc-mingw32/%{version}
%{_libexecdir}/gcc/i686-pc-mingw32/%{version}/cc1


%files c++
%defattr(-,root,root)
%{_bindir}/i686-pc-mingw32-g++
%{_bindir}/i686-pc-mingw32-c++
%{_mandir}/man1/i686-pc-mingw32-g++.1*
%{_libdir}/gcc/i686-pc-mingw32/%{version}/include/c++/
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libstdc++.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libsupc++.a
%{_libexecdir}/gcc/i686-pc-mingw32/%{version}/cc1plus
%{_libexecdir}/gcc/i686-pc-mingw32/%{version}/collect2


%files objc
%defattr(-,root,root)
%{_libdir}/gcc/i686-pc-mingw32/%{version}/include/objc/
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libobjc.a
%{_libexecdir}/gcc/i686-pc-mingw32/%{version}/cc1obj


%files objc++
%defattr(-,root,root)
%{_libexecdir}/gcc/i686-pc-mingw32/%{version}/cc1objplus


%files gfortran
%defattr(-,root,root)
%{_bindir}/i686-pc-mingw32-gfortran
%{_mandir}/man1/i686-pc-mingw32-gfortran.1*
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libgfortran.a
%{_libdir}/gcc/i686-pc-mingw32/%{version}/libgfortranbegin.a
%{_libexecdir}/gcc/i686-pc-mingw32/%{version}/f951


%changelog
* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.4.0-0.5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 20 2009 Richard W.M. Jones <rjones@redhat.com> - 4.4.0-0.4
- Rebuild for mingw32-gcc 4.4

* Thu Feb 19 2009 Richard W.M. Jones <rjones@redhat.com> - 4.4.0-0.2
- Move to upstream version 4.4.0-20090216 (same as Fedora native version).
- Added FORTRAN support.
- Added Objective C support.
- Added Objective C++ support.

* Mon Nov 24 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-12
- Rebuild against latest filesystem package.

* Fri Nov 21 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-11
- Remove obsoletes for a long dead package.

* Wed Nov 19 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-10
- Rebuild against mingw32-filesystem 37

* Wed Nov 19 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-9
- Rebuild against mingw32-filesystem 36

* Thu Oct 30 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-8
- Don't BR mpfr-devel for RHEL/EPEL-5 (Levente Farkas).

* Thu Sep  4 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-7
- Rename mingw -> mingw32.

* Thu Sep  4 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-6
- Use RPM macros from mingw-filesystem.

* Mon Jul  7 2008 Richard W.M. Jones <rjones@redhat.com> - 4.3.2-3
- Initial RPM release, largely based on earlier work from several sources.
