%global __os_install_post /usr/lib/rpm/brp-compress %{nil}
%global snapshot_date 20120224

# Set this to one when mingw-crt isn't built yet
%global bootstrap 0

# Libgomp requires pthreads so this can only be enabled once pthreads is built
%global enable_libgomp 1

Name:           mingw-gcc
Version:        4.7.0
Release:        0.6.%{snapshot_date}%{?dist}
Summary:        MinGW Windows cross-compiler (GCC) for C

License:        GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions
Group:          Development/Languages
URL:            http://gcc.gnu.org
# The source for this package was pulled from upstream's vcs.  Use the
# following commands to generate the tarball:
# svn export svn://gcc.gnu.org/svn/gcc/branches/redhat/gcc-4_7-branch@%{SVNREV} gcc-%{version}-%{snapshot_date}
# tar cf - gcc-%{version}-%{DATE} | bzip2 -9 > gcc-%{version}-%{snapshot_date}.tar.bz2
Source0:        gcc-%{version}-%{snapshot_date}.tar.bz2
#Source0:        ftp://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.bz2

# Recommended by upstream mingw-w64
# Already upstreamed in gcc r184560
Patch0:         gcc-r184560.patch

# Fix float128 soft-float for mingw targets
# http://gcc.gnu.org/ml/gcc-patches/2012-02/msg01309.html
Patch1:         gcc-4.7-fix-float128-soft-float.patch

BuildRequires:  texinfo
BuildRequires:  mingw32-filesystem >= 95
BuildRequires:  mingw32-binutils
BuildRequires:  mingw32-headers
%if 0%{bootstrap} == 0
BuildRequires:  mingw32-crt
%if 0%{enable_libgomp}
BuildRequires:  mingw32-pthreads
%endif
%endif
BuildRequires:  gmp-devel
BuildRequires:  mpfr-devel
BuildRequires:  libmpc-devel
BuildRequires:  zlib-devel
BuildRequires:  libgomp
BuildRequires:  ppl-devel
BuildRequires:  cloog-ppl-devel
BuildRequires:  flex

Requires:       mingw32-binutils
Requires:       mingw32-headers
Requires:       mingw32-cpp
%if 0%{bootstrap} == 0
Requires:       mingw32-crt
%endif

%description
MinGW Windows cross-compiler (GCC) for C.


%package -n mingw32-gcc
Summary:         MinGW Windows cross-compiler (GCC) for C

%description -n mingw32-gcc
MinGW Windows cross-compiler (GCC) for C.

%package -n mingw32-cpp
Summary: MinGW Windows cross-C Preprocessor
Group: Development/Languages

%description -n mingw32-cpp
MinGW Windows cross-C Preprocessor


%package -n mingw32-gcc-c++
Summary: MinGW Windows cross-compiler for C++
Group: Development/Languages
Requires: mingw32-gcc = %{version}-%{release}

%description -n mingw32-gcc-c++
MinGW Windows cross-compiler for C++.


%package -n mingw32-gcc-objc
Summary: MinGW Windows cross-compiler support for Objective C
Group: Development/Languages
Requires: mingw32-gcc = %{version}-%{release}
#Requires: mingw32-libobjc = %{version}-%{release}

%description -n mingw32-gcc-objc
MinGW Windows cross-compiler support for Objective C.


%package -n mingw32-gcc-objc++
Summary: MinGW Windows cross-compiler support for Objective C++
Group: Development/Languages
Requires: mingw32-gcc-c++ = %{version}-%{release}
Requires: mingw32-gcc-objc = %{version}-%{release}

%description -n mingw32-gcc-objc++
MinGW Windows cross-compiler support for Objective C++.


%package -n mingw32-gcc-gfortran
Summary: MinGW Windows cross-compiler for FORTRAN
Group: Development/Languages
Requires: mingw32-gcc = %{version}-%{release}

%description -n mingw32-gcc-gfortran
MinGW Windows cross-compiler for FORTRAN.


%prep
%setup -q -n gcc-%{version}-%{snapshot_date}
%patch0 -p0
pushd libgcc
%patch1 -p0
popd
echo 'Fedora MinGW %{version}-%{release}' > gcc/DEV-PHASE

# Install python files into _mingw32_datadir
sed -i -e '/^pythondir =/ s|$(datadir)|%{mingw32_datadir}|' libstdc++-v3/python/Makefile.{am,in}


%build
# Default configure arguments
configure_args="\
    --prefix=%{_prefix} \
    --bindir=%{_bindir} \
    --includedir=%{_includedir} \
    --libdir=%{_libdir} \
    --mandir=%{_mandir} \
    --infodir=%{_infodir} \
    --datadir=%{_datadir} \
    --build=%_build --host=%_host \
    --with-gnu-as --with-gnu-ld --verbose \
    --without-newlib \
    --disable-multilib \
    --disable-plugin \
    --with-system-zlib \
    --disable-nls --without-included-gettext \
    --disable-win32-registry \
    --target=%{mingw32_target} \
    --with-sysroot=%{mingw32_sysroot} \
    --with-gxx-include-dir=%{mingw32_includedir}/c++ \
    --enable-languages="c,c++,objc,obj-c++,fortran" \
    --with-bugurl=http://bugzilla.redhat.com/bugzilla"

# PPL/CLOOG optimalisations are only available on Fedora
%if 0%{?fedora}
configure_args="$configure_args --with-ppl --with-cloog"
%endif

# When bootstrapping, disable LTO support as it causes errors while building any binary
# $ i686-pc-mingw32-gcc -o conftest    conftest.c  >&5
# i686-pc-mingw32-gcc: fatal error: -fuse-linker-plugin, but liblto_plugin.so not found
%if 0%{bootstrap}
configure_args="$configure_args --disable-lto"
%endif

%if 0%{enable_libgomp}
configure_args="$configure_args --enable-libgomp"
%endif

# As we can't use the %%configure macro for out of source builds
# we've got to set the right compiler flags here
export CC="%{__cc} ${RPM_OPT_FLAGS}"

mkdir build
pushd build
  ../configure $configure_args

  # If we're bootstrapping, only build the GCC core
  %if 0%{bootstrap}
  make %{?_smp_mflags} all-gcc
  %else
  make %{?_smp_mflags} all
  %endif
popd


%install
pushd build
%if 0%{bootstrap}
make DESTDIR=$RPM_BUILD_ROOT install-gcc
%else
make DESTDIR=$RPM_BUILD_ROOT install
%endif

# These files conflict with existing installed files.
rm -rf $RPM_BUILD_ROOT%{_infodir}
rm -f $RPM_BUILD_ROOT%{_libdir}/libiberty*
rm -f $RPM_BUILD_ROOT%{_mandir}/man7/*
rm -rf $RPM_BUILD_ROOT%{_datadir}/gcc-%{version}/python

%if 0%{bootstrap} == 0
# Move the DLL's manually to the correct location
mkdir -p $RPM_BUILD_ROOT%{mingw32_bindir}
mv    $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libgcc_s_sjlj-1.dll \
      $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libssp-0.dll \
      $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libstdc++-6.dll \
      $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libobjc-4.dll \
      $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libgfortran-3.dll \
      $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libquadmath-0.dll \
%if 0%{enable_libgomp}
      $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/libgomp-1.dll \
%endif
      $RPM_BUILD_ROOT%{mingw32_bindir}

# Various import libraries are placed in the wrong folder
mkdir -p $RPM_BUILD_ROOT%{mingw32_libdir}
mv $RPM_BUILD_ROOT%{_prefix}/%{mingw32_target}/lib/* $RPM_BUILD_ROOT%{mingw32_libdir}

# Don't want the *.la files.
find $RPM_BUILD_ROOT -name '*.la' -delete

%endif

# For some reason there are wrapper libraries created named $target-$target-gcc-$tool
# Drop those files for now as this looks like a bug in GCC
rm -f $RPM_BUILD_ROOT%{_bindir}/%{mingw32_target}-%{mingw32_target}-*

popd


%files -n mingw32-gcc
%{_bindir}/%{mingw32_target}-gcc
%{_bindir}/%{mingw32_target}-gcc-%{version}
%{_bindir}/%{mingw32_target}-gcc-ar
%{_bindir}/%{mingw32_target}-gcc-nm
%{_bindir}/%{mingw32_target}-gcc-ranlib
%{_bindir}/%{mingw32_target}-gcov
%dir %{_libdir}/gcc/%{mingw32_target}
%dir %{_libdir}/gcc/%{mingw32_target}/%{version}
%dir %{_libdir}/gcc/%{mingw32_target}/%{version}/include
%dir %{_libdir}/gcc/%{mingw32_target}/%{version}/include-fixed
%{_libdir}/gcc/%{mingw32_target}/%{version}/include-fixed/README
%{_libdir}/gcc/%{mingw32_target}/%{version}/include-fixed/*.h
%{_libdir}/gcc/%{mingw32_target}/%{version}/include/*.h
%dir %{_libdir}/gcc/%{mingw32_target}/%{version}/install-tools
%{_libdir}/gcc/%{mingw32_target}/%{version}/install-tools/*
%dir %{_libexecdir}/gcc/%{mingw32_target}/%{version}/install-tools
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/install-tools/*
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/lto-wrapper
%{_mandir}/man1/%{mingw32_target}-gcc.1*
%{_mandir}/man1/%{mingw32_target}-gcov.1*

# Non-bootstrap files
%if 0%{bootstrap} == 0
%{mingw32_bindir}/libgcc_s_sjlj-1.dll
%{mingw32_bindir}/libssp-0.dll
%{mingw32_libdir}/libgcc_s.a
%{mingw32_libdir}/libssp.a
%{mingw32_libdir}/libssp.dll.a
%{mingw32_libdir}/libssp_nonshared.a
%{_libdir}/gcc/%{mingw32_target}/%{version}/crtbegin.o
%{_libdir}/gcc/%{mingw32_target}/%{version}/crtend.o
%{_libdir}/gcc/%{mingw32_target}/%{version}/crtfastmath.o
%{_libdir}/gcc/%{mingw32_target}/%{version}/libgcc.a
%{_libdir}/gcc/%{mingw32_target}/%{version}/libgcc_eh.a
%{_libdir}/gcc/%{mingw32_target}/%{version}/libgcov.a
%dir %{_libdir}/gcc/%{mingw32_target}/%{version}/include/ssp
%{_libdir}/gcc/%{mingw32_target}/%{version}/include/ssp/*.h
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/lto1
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/liblto_plugin.so*

%if 0%{enable_libgomp}
%{mingw32_bindir}/libgomp-1.dll
%{mingw32_libdir}/libgomp.a
%{mingw32_libdir}/libgomp.dll.a
%{mingw32_libdir}/libgomp.spec
%endif
%endif

%files -n mingw32-cpp
%{_bindir}/%{mingw32_target}-cpp
%{_mandir}/man1/%{mingw32_target}-cpp.1*
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/cc1
%dir %{_libdir}/gcc/%{mingw32_target}
%dir %{_libdir}/gcc/%{mingw32_target}/%{version}


%files -n mingw32-gcc-c++
%{_bindir}/%{mingw32_target}-g++
%{_bindir}/%{mingw32_target}-c++
%{_mandir}/man1/%{mingw32_target}-g++.1*
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/cc1plus
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/collect2

# Non-bootstrap files
%if 0%{bootstrap} == 0
%{mingw32_includedir}/c++/
%{mingw32_libdir}/libstdc++.a
%{mingw32_libdir}/libstdc++.dll.a
%{mingw32_libdir}/libstdc++.dll.a-gdb.py
%{mingw32_libdir}/libsupc++.a
%{mingw32_bindir}/libstdc++-6.dll
%endif


%files -n mingw32-gcc-objc
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/cc1obj

# Non-bootstrap files
%if 0%{bootstrap} == 0
%{_libdir}/gcc/%{mingw32_target}/%{version}/include/objc/
%{mingw32_libdir}/libobjc.a
%{mingw32_libdir}/libobjc.dll.a
%{mingw32_bindir}/libobjc-4.dll
%endif


%files -n mingw32-gcc-objc++
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/cc1objplus


%files -n mingw32-gcc-gfortran
%{_bindir}/%{mingw32_target}-gfortran
%{_mandir}/man1/%{mingw32_target}-gfortran.1*
%{_libexecdir}/gcc/%{mingw32_target}/%{version}/f951
%dir %{_libdir}/gcc/%{mingw32_target}/%{version}/finclude

# Non-bootstrap files
%if 0%{bootstrap} == 0
%{mingw32_bindir}/libgfortran-3.dll
%{mingw32_bindir}/libquadmath-0.dll
%{mingw32_libdir}/libgfortran.a
%{mingw32_libdir}/libgfortran.dll.a
%{mingw32_libdir}/libgfortran.spec
%{mingw32_libdir}/libquadmath.a
%{mingw32_libdir}/libquadmath.dll.a
%{_libdir}/gcc/%{mingw32_target}/%{version}/libgfortranbegin.a
%{_libdir}/gcc/%{mingw32_target}/%{version}/libcaf_single.a
%if 0%{enable_libgomp}
%{_libdir}/gcc/%{mingw32_target}/%{version}/finclude/omp_lib.f90
%{_libdir}/gcc/%{mingw32_target}/%{version}/finclude/omp_lib.h
%{_libdir}/gcc/%{mingw32_target}/%{version}/finclude/omp_lib.mod
%{_libdir}/gcc/%{mingw32_target}/%{version}/finclude/omp_lib_kinds.mod
%endif
%endif


%changelog
* Tue Mar 06 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 4.7.0-0.6.20120224
- Renamed the source package to mingw-gcc (RHBZ #673788)
- Use mingw macros without leading underscore

* Mon Feb 27 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 4.7.0-0.5.20120224
- Re-enable libgomp support

* Mon Feb 27 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 4.7.0-0.4.20120224
- Perform a regular build

* Sat Feb 25 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 4.7.0-0.3.20120224
- Update to gcc 4.7 20120224 snapshot
- Perform a bootstrap build using mingw-w64
- Dropped the /lib/i686-pc-mingw32-cpp symlink
- Dropped the float.h patch as it isn't needed anymore with mingw-w64
- Added some patches which upstream mingw-w64 recommends us to apply

* Fri Jan 27 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 4.7.0-0.2.20120126
- Update to gcc 4.7 20120126 snapshot (fixes mingw32-qt build failure)

* Tue Jan 10 2012 Erik van Pienbroek <epienbro@fedoraproject.org> - 4.7.0-0.1.20120106
- Update to gcc 4.7 20120106 snapshot

* Wed Oct 26 2011 Marcela Mašláňová <mmaslano@redhat.com> - 4.6.1-3.2
- rebuild with new gmp without compat lib

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
