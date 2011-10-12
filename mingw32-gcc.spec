%global __os_install_post /usr/lib/rpm/brp-compress %{nil}

Name:           mingw32-gcc
Version:        4.6.1
Release:        3%{?dist}.1
Summary:        MinGW Windows cross-compiler (GCC) for C

License:        GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions
Group:          Development/Languages
URL:            http://gcc.gnu.org
Source0:        ftp://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.bz2
Patch0:         gcc-1-mingw-float.patch

BuildRequires:  texinfo
BuildRequires:  mingw32-filesystem >= 68
# Need mingw32-binutils which support %gnu_unique_object >= 2.19.51.0.14
BuildRequires:  mingw32-binutils >= 2.19.51.0.14
BuildRequires:  mingw32-runtime >= 3.18-4
BuildRequires:  mingw32-w32api
BuildRequires:  mingw32-pthreads
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  libmpc-devel
BuildRequires:  zlib-devel
BuildRequires:  libgomp
BuildRequires:  ppl-devel
BuildRequires:  cloog-ppl-devel
BuildRequires:  flex

# Need mingw32-binutils which support %gnu_unique_object
Requires:       mingw32-binutils >= 2.19.51.0.14
Requires:       mingw32-w32api
Requires:       mingw32-cpp

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
#Requires: mingw32-libobjc = %{version}-%{release}

%description objc
MinGW Windows cross-compiler support for Objective C.


%package objc++
Summary: MinGW Windows cross-compiler support for Objective C++
Group: Development/Languages
Requires: %{name}-c++ = %{version}-%{release}
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
%setup -q -n gcc-%{version}
%patch0 -p1 -b .float
echo 'Fedora MinGW %{version}-%{release}' > gcc/DEV-PHASE

# Install python files into _mingw32_datadir
sed -i -e '/^pythondir =/ s|$(datadir)|%{_mingw32_datadir}|' libstdc++-v3/python/Makefile.{am,in}


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
  --disable-plugin \
  --enable-libgomp \
  --with-ppl --with-cloog \
  --with-system-zlib \
  --disable-nls --without-included-gettext \
  --disable-win32-registry \
  --enable-version-specific-runtime-libs \
  --with-sysroot=%{_mingw32_sysroot} \
  --enable-languages="$languages" \
  --with-bugurl=http://bugzilla.redhat.com/bugzilla

make %{?_smp_mflags} all

popd


%install
pushd build
make DESTDIR=$RPM_BUILD_ROOT install

# These files conflict with existing installed files.
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty*
rm -f $RPM_BUILD_ROOT%{_mandir}/man7/*

mkdir -p $RPM_BUILD_ROOT/lib
ln -sf ..%{_prefix}/bin/%{_mingw32_target}-cpp \
  $RPM_BUILD_ROOT/lib/%{_mingw32_target}-cpp

# Move runtime dll files to _mingw32_bindir.
mkdir -p $RPM_BUILD_ROOT%{_mingw32_bindir}
mv $RPM_BUILD_ROOT%{_libdir}/gcc/%{_mingw32_target}/%{version}/*.dll \
   $RPM_BUILD_ROOT%{_libdir}/gcc/%{_mingw32_target}/*.dll \
  $RPM_BUILD_ROOT%{_mingw32_bindir}

# Don't want the *.la files.
find $RPM_BUILD_ROOT -name '*.la' -delete

popd


%files
%{_bindir}/%{_mingw32_target}-gcc
%{_bindir}/%{_mingw32_target}-gcc-%{version}
%{_bindir}/%{_mingw32_target}-gcov
%{_prefix}/%{_mingw32_target}/lib/libiberty.a
%dir %{_libdir}/gcc/%{_mingw32_target}
%dir %{_libdir}/gcc/%{_mingw32_target}/%{version}
%{_libdir}/gcc/%{_mingw32_target}/%{version}/crtbegin.o
%{_libdir}/gcc/%{_mingw32_target}/%{version}/crtend.o
%{_libdir}/gcc/%{_mingw32_target}/%{version}/crtfastmath.o
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgcc.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgcc_eh.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgcc_s.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgcov.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgomp.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgomp.dll.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgomp.spec
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libssp.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libssp_nonshared.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libssp.dll.a
%dir %{_libdir}/gcc/%{_mingw32_target}/%{version}/include
%dir %{_libdir}/gcc/%{_mingw32_target}/%{version}/include-fixed
%dir %{_libdir}/gcc/%{_mingw32_target}/%{version}/include/ssp
%{_libdir}/gcc/%{_mingw32_target}/%{version}/include-fixed/README
%{_libdir}/gcc/%{_mingw32_target}/%{version}/include-fixed/*.h
%{_libdir}/gcc/%{_mingw32_target}/%{version}/include/*.h
%{_libdir}/gcc/%{_mingw32_target}/%{version}/include/ssp/*.h
%dir %{_libdir}/gcc/%{_mingw32_target}/%{version}/install-tools
%{_libdir}/gcc/%{_mingw32_target}/%{version}/install-tools/*
%dir %{_libexecdir}/gcc/%{_mingw32_target}/%{version}/install-tools
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/install-tools/*
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/lto-wrapper
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/lto1
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/liblto_plugin.so*
%{_mingw32_bindir}/libgcc_s_sjlj-1.dll
%{_mingw32_bindir}/libgomp-1.dll
%{_mingw32_bindir}/libssp-0.dll
%{_mandir}/man1/%{_mingw32_target}-gcc.1*
%{_mandir}/man1/%{_mingw32_target}-gcov.1*
%{_mingw32_datadir}/gcc-%{version}/


%files -n mingw32-cpp
/lib/%{_mingw32_target}-cpp
%{_bindir}/%{_mingw32_target}-cpp
%{_mandir}/man1/%{_mingw32_target}-cpp.1*
%dir %{_libdir}/gcc/%{_mingw32_target}
%dir %{_libdir}/gcc/%{_mingw32_target}/%{version}
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/cc1


%files c++
%{_bindir}/%{_mingw32_target}-g++
%{_bindir}/%{_mingw32_target}-c++
%{_mandir}/man1/%{_mingw32_target}-g++.1*
%{_libdir}/gcc/%{_mingw32_target}/%{version}/include/c++/
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libstdc++.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libstdc++.dll.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libstdc++.dll.a-gdb.py
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libsupc++.a
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/cc1plus
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/collect2
%{_mingw32_bindir}/libstdc++-6.dll


%files objc
%{_libdir}/gcc/%{_mingw32_target}/%{version}/include/objc/
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libobjc.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libobjc.dll.a
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/cc1obj
%{_mingw32_bindir}/libobjc-3.dll


%files objc++
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/cc1objplus


%files gfortran
%{_bindir}/%{_mingw32_target}-gfortran
%{_mandir}/man1/%{_mingw32_target}-gfortran.1*
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgfortran.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgfortran.dll.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgfortran.spec
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libgfortranbegin.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libquadmath.a
%{_libdir}/gcc/%{_mingw32_target}/%{version}/libquadmath.dll.a
%dir %{_libdir}/gcc/%{_mingw32_target}/%{version}/finclude
%{_libdir}/gcc/%{_mingw32_target}/%{version}/finclude/omp_lib.f90
%{_libdir}/gcc/%{_mingw32_target}/%{version}/finclude/omp_lib.h
%{_libdir}/gcc/%{_mingw32_target}/%{version}/finclude/omp_lib.mod
%{_libdir}/gcc/%{_mingw32_target}/%{version}/finclude/omp_lib_kinds.mod
%{_libexecdir}/gcc/%{_mingw32_target}/%{version}/f951
%{_mingw32_bindir}/libgfortran-3.dll
%{_mingw32_bindir}/libquadmath-0.dll


%changelog
* Wed Oct 12 2011 Peter Schiffer <pschiffe@redhat.com> - 4.6.1-3.1
- rebuild with new gmp

* Fri Aug 26 2011 Kalev Lember <kalevlember@gmail.com> - 4.6.1-3
- Fix float.h inclusion when gcc's headers precede mingrt in include path

* Fri Aug 19 2011 Erik van Pienbroek <epienbro@fedoraproject.org> - 4.6.1-2
- Build against ppl and cloog

* Mon Jun 27 2011 Kalev Lember <kalev@smartlink.ee> - 4.6.1-1
- Update to 4.6.1

* Sat May 21 2011 Kalev Lember <kalev@smartlink.ee> - 4.5.3-3
- Rebuilt with automatic dep extraction and removed all manual
  mingw32(...) provides / requires
- Cleaned up the spec file from cruft not needed with latest rpm

* Tue May 10 2011 Kalev Lember <kalev@smartlink.ee> - 4.5.3-2
- Disable plugin support with a configure option, instead of deleting
  the files in the install section
- Use the %%{_mingw32_target} macro in files section

* Sat Apr 30 2011 Kalev Lember <kalev@smartlink.ee> - 4.5.3-1
- Update to 4.5.3

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Thu Aug 05 2010 Kalev Lember <kalev@smartlink.ee> - 4.5.1-1
- Update to 4.5.1

* Thu May 13 2010 Kalev Lember <kalev@smartlink.ee> - 4.5.0-1
- Update to vanilla gcc 4.5.0
- Drop patches specific to Fedora native gcc.
- BuildRequires libmpc-devel and zlib-devel
- Added Provides for additional shared language runtime DLLs

* Thu Dec 17 2009 Chris Bagwell <chris@cnpbagwell.com> - 4.4.2-2
- Enable libgomp support.

* Sun Nov 22 2009 Kalev Lember <kalev@smartlink.ee> - 4.4.2-1
- Update to gcc 4.4.2 20091114 svn 154179, which includes
  VTA backport from 4.5 branch.
- Patches taken from native Fedora gcc-4.4.2-10.

* Fri Sep 18 2009 Kalev Lember <kalev@smartlink.ee> - 4.4.1-3
- Require mingw32-binutils >= 2.19.51.0.14 for %%gnu_unique_object support.

* Thu Sep 03 2009 Kalev Lember <kalev@smartlink.ee> - 4.4.1-2
- Update to gcc 4.4.1 20090902 svn 151328.
- Patches taken from native Fedora gcc-4.4.1-8.
- Another license update to keep it in sync with native gcc package.

* Sun Aug 23 2009 Kalev Lember <kalev@smartlink.ee> - 4.4.1-1
- Update to gcc 4.4.1 20090818 svn 150873.
- Patches taken from native Fedora gcc-4.4.1-6.
- Replaced %%define with %%global and updated %%defattr.
- Changed license to match native Fedora gcc package.

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.4.0-0.8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Mar 23 2009 Richard W.M. Jones <rjones@redhat.com> - 4.4.0-0.7
- New native Fedora version gcc 4.4.0 20090319 svn 144967.
- Enable _smp_mflags.

* Wed Mar  4 2009 Richard W.M. Jones <rjones@redhat.com> - 4.4.0-0.6
- Fix libobjc and consequently Objective C and Objective C++ compilers.

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
