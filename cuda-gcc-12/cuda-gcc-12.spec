%global _gnu %{nil}
%global _host %{_target_platform}
%global gcc_target_platform %{_target_platform}
%global gmp_version 4.3.2
%global libmpc_version 0.8.1
%global mpfr_version 2.4.2
%global binary_prefix cuda-

%global __provides_exclude_from (%{_libdir}|%{_libexecdir})/gcc/%{gcc_target_platform}/%{version}/
%global __requires_exclude_from (%{_libdir}|%{_libexecdir})/gcc/%{gcc_target_platform}/%{version}/

Name:           cuda-gcc-12
Version:        12.3.0
Release:        1%{?dist}
Summary:        GNU Compiler Collection CUDA compatibility package
License:        GPLv3+ and GPLv3+ with exceptions and GPLv2+ with exceptions and LGPLv2+ and BSD
URL:            http://gcc.gnu.org
Source0:        https://ftp.gnu.org/gnu/gcc/gcc-%{version}/gcc-%{version}.tar.gz

Patch0:         gcc12-hack.patch
Patch2:         gcc12-sparc-config-detection.patch
Patch3:         gcc12-libgomp-omp_h-multilib.patch
Patch4:         gcc12-libtool-no-rpath.patch
Patch5:         gcc12-isl-dl.patch
Patch6:         gcc12-isl-dl2.patch
Patch7:         gcc12-libstdc++-docs.patch
Patch8:         gcc12-no-add-needed.patch
Patch9:         gcc12-Wno-format-security.patch
Patch10:        gcc12-rh1574936.patch
Patch11:        gcc12-d-shared-libphobos.patch

Patch100:       gcc12-fortran-fdec-duplicates.patch
Patch101:       gcc12-fortran-flogical-as-integer.patch
Patch102:       gcc12-fortran-fdec-override-kind.patch
Patch103:       gcc12-fortran-fdec-non-logical-if.patch

BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
# from contrib/download_prerequisites
BuildRequires:  gmp-devel >= %{gmp_version}
BuildRequires:  isl-devel >= 0.15
BuildRequires:  libmpc-devel >= %{libmpc_version}
BuildRequires:  mpfr-devel >= %{mpfr_version}
BuildRequires:  zlib-devel

Requires:       binutils
Provides:       cuda-gcc = %{version}-%{release}

# Disable annobin
%undefine _annotated_build
%global _lto_cflags %{nil}

%description
The %{name} package contains a CUDA supported version of the GNU Compiler
Collection.

%package        c++
Summary:        C++ support for GCC CUDA compatibility package
Requires:       %{name} = %{version}-%{release}
%if 0%{?fedora} >= 35
Requires:       isl
%endif
Provides:       cuda-gcc-c++ = %{version}-%{release}

%description    c++
The %{name} package contains a CUDA supported version of the GNU Compiler
Collection.

This package adds C++ support to the GNU Compiler Collection.

%package        gfortran
Summary:        Fortran support for GCC CUDA compatibility package
Requires:       %{name} = %{version}-%{release}
Provides:       cuda-gcc-gfortran = %{version}-%{release}

%description    gfortran
The %{name} package contains a CUDA supported version of the GNU Compiler
Collection.

This package adds C++ support to the GNU Compiler Collection.

%prep
%autosetup -p0 -n gcc-%{version}

%build
export CFLAGS=`echo %{build_cflags} | sed -e 's/-Werror=format-security//g' -e 's/-fcf-protection//g'`
export CXXFLAGS=`echo %{build_cxxflags} | sed -e 's/-Werror=format-security//g' -e 's/-fcf-protection//g'`
export FFLAGS=`echo %{build_fflags} | sed -e 's/-Werror=format-security//g' -e 's/-fcf-protection//g'`
export FCFLAGS=`echo %{build_fflags} | sed -e 's/-Werror=format-security//g' -e 's/-fcf-protection//g'`

# Parameter '--enable-version-specific-runtime-libs' can't be used as it
# prevents the proper include directories to be added by default to cc1/cc1plus
%configure \
    --build=%{gcc_target_platform} \
    --disable-bootstrap \
    --enable-libquadmath \
    --enable-libquadmath-support \
    --disable-libsanitizer \
    --disable-libssp \
    --disable-multilib \
    --enable-__cxa_atexit \
    --enable-languages=c,c++,fortran \
    --enable-linker-build-id \
    --enable-threads=posix \
    --enable-version-specific-runtime-libs \
    --program-prefix=cuda- \
    --with-system-zlib

%make_build

%install
rm -rf %{buildroot}
%make_install

mv %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include-fixed/*.h \
    %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/

mv %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{_lib}/* \
    %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{version}/

rm -fr \
    %{buildroot}%{_bindir}/%{gcc_target_platform}-* \
    %{buildroot}%{_datadir}/locale \
    %{buildroot}%{_infodir}/{dir,*.info}* \
    %{buildroot}%{_mandir}/man7/{fsf-funding,gfdl,gpl}* \
    %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include-fixed \
    %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{version}/install-tools \
    %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{version}/plugin \
    %{buildroot}%{_libdir}/gcc/%{gcc_target_platform}/%{_lib}/ \
    %{buildroot}%{_libdir}/libcc1.so* \
    %{buildroot}%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/install-tools \
    %{buildroot}%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/plugin

find %{buildroot} -name "*.la" -delete

%files
%{_bindir}/%{?binary_prefix}gcc
%{_bindir}/%{?binary_prefix}gcc-ar
%{_bindir}/%{?binary_prefix}gcc-nm
%{_bindir}/%{?binary_prefix}gcc-ranlib
%{_bindir}/%{?binary_prefix}gcov
%{_bindir}/%{?binary_prefix}gcov-dump
%{_bindir}/%{?binary_prefix}gcov-tool
%{_bindir}/%{?binary_prefix}lto-dump
%dir %{_libdir}/gcc
%dir %{_libdir}/gcc/%{gcc_target_platform}
%dir %{_libdir}/gcc/%{gcc_target_platform}/%{version}
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/crt*.o
%{_mandir}/man1/%{?binary_prefix}gcc.1*
%{_mandir}/man1/%{?binary_prefix}gcov.1*
%{_mandir}/man1/%{?binary_prefix}gcov-dump.1*
%{_mandir}/man1/%{?binary_prefix}gcov-tool.1*
%{_mandir}/man1/%{?binary_prefix}lto-dump.1*
%dir %{_libexecdir}/gcc
%dir %{_libexecdir}/gcc/%{gcc_target_platform}
%dir %{_libexecdir}/gcc/%{gcc_target_platform}/%{version}
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/cc1
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/collect2
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/lto1
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/lto-wrapper
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/liblto_plugin.so*
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/g++-mapper-server
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libatomic.*
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libcaf_single.a
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/libcilkrts.*
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libgcc.a
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libgcc_eh.a
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libgcc_s.*
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libgcov.a
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libgomp.*
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libitm.*
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/libmpx.*
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/libmpxwrappers.*
%ifnarch aarch64
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libquadmath.a
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libquadmath.so
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libquadmath.so.0
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libquadmath.so.0.0.0
%endif
# Headers
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stddef.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdarg.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdfix.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/varargs.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/float.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/limits.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdbool.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/iso646.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/syslimits.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/unwind.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdint.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdint-gcc.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdalign.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdnoreturn.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/stdatomic.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/acc_prof.h
%ifnarch aarch64
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/quadmath.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/quadmath_weak.h
%endif
%ifarch %{ix86} x86_64
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/emmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/pmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/tmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/ammintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/smmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/nmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/bmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/wmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/immintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avxintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/x86intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/fma4intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xopintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/lwpintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/popcntintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/bmiintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/tbmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/ia32intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx2intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/bmi2intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/f16cintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/fmaintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/lzcntintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/rtmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xtestintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/adxintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/prfchwintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/rdseedintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/fxsrintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xsaveintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xsaveoptintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/enqcmdintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512cdintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512erintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512fintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512pfintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512bf16intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512bf16vlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vp2intersectintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vp2intersectvlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512fp16intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512fp16vlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/shaintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mm_malloc.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mm3dnow.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/cpuid.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/cross-stdarg.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512bwintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512dqintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512ifmaintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512ifmavlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vbmiintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vbmivlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vlbwintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vldqintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/clflushoptintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/clwbintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mwaitxintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xsavecintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xsavesintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/clzerointrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/pkuintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx5124fmapsintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx5124vnniwintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vpopcntdqintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/gcov.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/sgxintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512bitalgintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vbmi2intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vbmi2vlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vnniintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vnnivlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avx512vpopcntdqvlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/cet.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/cetintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/gfniintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/movdirintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/pconfigintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/vaesintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/vpclmulqdqintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/wbnoinvdintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/amxbf16intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/amxint8intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/amxtileintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/avxvnniintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/hresetintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/keylockerintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mwaitintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/serializeintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/tsxldtrkintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/uintrintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/x86gprintrin.h
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/include/libv4l1-videodev.h
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/include/libv4lconvert.h
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/include/slang.h
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/include/rb_mjit_min_header-3.2.2-x86_64.h
%endif
%ifarch ppc ppc64 ppc64le ppc64p7
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/ppc-asm.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/altivec.h
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/include/spe.h
# % {_libdir}/gcc/ % {gcc_target_platform}/ % {version}/include/paired.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/ppu_intrinsics.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/si2vmx.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/spu2vmx.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/vec_types.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/htmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/htmxlintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/amo.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/bmi2intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/bmiintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/emmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/gcov.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mm_malloc.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/pmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/smmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/tmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/x86intrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/xmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/immintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/nmmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/rs6000-vecdefines.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/x86gprintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/ecrti.o
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/ecrtn.o
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/ncrti.o
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/ncrtn.o
%endif
%ifarch %{arm}
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/unwind-arm-common.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/mmintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/arm_neon.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/arm_acle.h
%endif
%ifarch aarch64
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/gcov.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/arm_neon.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/arm_acle.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/arm_fp16.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/arm_bf16.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/arm_sve.h
%endif
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/ISO_Fortran_binding.h
%ifarch x86_64
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/cldemoteintrin.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/waitpkgintrin.h
%endif
%if (0%{?fedora} >= 35) || (0%{?rhel} >= 9)
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/pthread.h
%endif

%files c++
%{_bindir}/%{?binary_prefix}c++
%{_bindir}/%{?binary_prefix}cpp
%{_bindir}/%{?binary_prefix}g++
%{_mandir}/man1/%{?binary_prefix}cpp.1*
%{_mandir}/man1/%{?binary_prefix}g++.1*
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/cc1plus
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/c++/
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libstdc++.*
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libstdc++fs.a
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libsupc++.a
%{_datadir}/gcc-%{version}/python/libstdcxx
# Headers
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/omp.h
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/include/openacc.h

%files gfortran
%{_bindir}/%{?binary_prefix}gfortran
%{_mandir}/man1/%{?binary_prefix}gfortran.1*
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/finclude
%{_libexecdir}/gcc/%{gcc_target_platform}/%{version}/f951
%{_libdir}/gcc/%{gcc_target_platform}/%{version}/libgfortran.*

%changelog
* Sun Oct 22 2023 Pavel Artsishevskii <polter.rnd@gmail.com> - 12.3.0-1
- Update to 12.3.0

* Sat Feb 05 2022 Balint Cristian <cristian.balint@gmail.com> - 11.2.1-1
- Update to 10.3.1

* Thu Nov 11 2021 Balint Cristian <cristian.balint@gmail.com> - 10.3.1-1
- Update to 10.3.1

* Fri Jul 23 2021 Balint Cristian <cristian.balint@gmail.com> - 9.4.1-1
- Update to 9.4.1
