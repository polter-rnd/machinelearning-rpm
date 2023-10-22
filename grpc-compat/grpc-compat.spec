## START: Set by rpmautospec
## (rpmautospec version 0.3.5)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 4;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

# We need to use C++17 to link against the system abseil-cpp, or we get linker
# errors.
%global cpp_std 17

# However, we also get linker errors building the tests if we link against the
# copy of gtest in Fedora (compiled with C++11). The exact root cause is not
# quite clear. We must therefore bundle a copy of gtest in the source RPM
# rather than using the system copy. This is to be discouraged, but there is no
# alternative in this case. It is not treated as a bundled library because it
# is used only at build time, and contributes nothing to the installed files.
# We take measures to verify this in %%check. As long as we are using our own
# copy, we use the exact same version as upstream.
%global gtest_url https://github.com/google/googletest
%global gtest_dir googletest-%{gtest_commit}
%global gtest_commit 0e402173c97aea7a00749e825b194bfede4f2e45
#global gtest_version 1.11.0
#global gtest_dir googletest-release-#{gtest_version}
%bcond_with system_gtest

# =====

# Parameters for third-party sources needed for their .proto files, which
# upstream expects to download at build time.
#
# See https://github.com/grpc/grpc/pull/29254 “[xDS Proto] Enhence gRPC
# buildgen for 3rd party proto compilation” and
# https://github.com/grpc/grpc/commit/99752b173cfa2fba81dedb482ee4fd74b2a46bb0,
# in which the download mechanism was added.
#
# Check CMakeLists.txt (search for “download_archive”) for a list of these
# third-party sources and the commit hashes used in the grpc release.
#
# Note that we do not treat these additional sources as bundled dependencies,
# since (provably) only the .proto files are used.
#
# In practice, it seems the generated binding code for these protos is not
# re-generated when building this package, so we could get by with creating the
# appropriate directories and touching an empty file within each. We include
# these archives in the source RPM anyway, since they are in some sense part of
# the original sources for the generated proto code.

# This will probably never be separately packaged in Fedora, since upstream can
# only build with Bazel (and Bazel is such a mess of bundled dependencies that
# it is unlikely to every be successfully packaged under the Fedora packaging
# guidelines. Note that the URL is a read-only mirror based on
# https://github.com/envoyproxy/envoy, with different commit hashes.
%global envoy_api_commit 9c42588c956220b48eb3099d186487c2f04d32ec
%global envoy_api_url https://github.com/envoyproxy/data-plane-api
%global envoy_api_dir data-plane-api-%{envoy_api_commit}

%global googleapis_commit 2f9af297c84c55c8b871ba4495e01ade42476c92
%global googleapis_url https://github.com/googleapis/googleapis
%global googleapis_dir googleapis-%{googleapis_commit}

%global opencensus_proto_version 0.3.0
%global opencensus_proto_url https://github.com/census-instrumentation/opencensus-proto
%global opencensus_proto_dir opencensus-proto-%{opencensus_proto_version}

%global xds_commit cb28da3451f158a947dfc45090fe92b07b243bc1
%global xds_url https://github.com/cncf/xds
%global xds_dir xds-%{xds_commit}

# =====

# Bootstrapping breaks the circular dependency on python3dist(xds-protos),
# which is packaged separately but ultimately generated from grpc sources using
# the proto compilers in this package; the consequence is that we cannot build
# the python3-grpcio-admin or python3-grpcio-csds subpackages until after
# bootstrapping.
%bcond_without bootstrap

# This must be enabled to get grpc_cli, which is apparently considered part of
# the tests by upstream. This is mentioned in
# https://github.com/grpc/grpc/issues/23432.
%bcond_with core_tests

# A great many of these tests (over 20%) fail. Any help in understanding these
# well enough to fix them or report them upstream is welcome.
%bcond_with python_aio_tests

%ifnarch s390x
# There are currently a significant number of failures like:
#
#   Exception serializing message!
#   Traceback (most recent call last):
#     File "/builddir/build/BUILDROOT/grpc-1.48.0-2.fc38~bootstrap.x86_64/usr/lib64/python3.11/site-packages/grpc/_common.py", line 86, in _transform
#       return transformer(message)
#              ^^^^^^^^^^^^^^^^^^^^
#     File "/usr/lib/python3.11/site-packages/google/protobuf/internal/python_message.py", line 1082, in SerializeToString
#       if not self.IsInitialized():
#              ^^^^^^^^^^^^^^^^^^
#   AttributeError: 'NoneType' object has no attribute 'IsInitialized'
%bcond_with python_gevent_tests
%else
# A significant number of Python tests pass in test_lite but fail in
# test_gevent, mostly by dumping core without a traceback.  Since it is tedious
# to enumerate these (and it is difficult to implement “suite-specific” skips
# for shared tests, so the tests would have to be skipped in all suites), we
# just skip the gevent suite entirely on this architecture.
%bcond_with python_gevent_tests
%endif

# Running core tests under valgrind may help debug crashes. This is mostly
# ignored if the gdb build conditional is also set.
%bcond_with valgrind
# Running core tests under gdb may help debug crashes.
%bcond_with gdb

# HTML documentation generated with Doxygen and/or Sphinx is not suitable for
# packaging due to a minified JavaScript bundle inserted by
# Doxygen/Sphinx/Sphinx themes itself. See discussion at
# https://bugzilla.redhat.com/show_bug.cgi?id=2006555.
#
# Normally we could consider enabling the Doxygen PDF documentation as a lesser
# substitute, but (after enabling it and working around some Unicode characters
# in the Markdown input) we get:
#
#   ! TeX capacity exceeded, sorry [main memory size=6000000].
#
# A similar situation applies to the Sphinx-generated HTML documentation for
# Python, except that we have not even tried to render it as a PDF because it
# is too unpleasant to try if we already cannot package the Doxygen-generated
# documentation. Instead, we have just dropped all documentation.

Name:           grpc-compat
Version:        1.48.4
Release:        1%{?dist}
Summary:        RPC library and framework

%global srcversion %(echo '%{version}' | sed -r 's/~rc/-pre/')
%global pyversion %(echo '%{version}' | tr -d '~')

# CMakeLists.txt: gRPC_CORE_SOVERSION
%global c_so_version 26
# CMakeLists.txt: gRPC_CPP_SOVERSION
# See https://github.com/abseil/abseil-cpp/issues/950#issuecomment-843169602
# regarding unusual C++ SOVERSION style (not a single number).
%global cpp_so_version 1.48

# The entire source is Apache-2.0 except the following:
#
# BSD-2-Clause:
#   - third_party/xxhash is BSD-2-Clause, at least the relevant parts (not the
#     command-line tool); it is unbundled, but then it is used as a header-only
#     library due to XXH_INCLUDE_ALL, so we must treat it as a static library
#     and include its license in that of the binary RPMs
#     * Potentially linked into any compiled subpackage (but not pure-Python
#       subpackages, etc.)
# BSD-3-Clause:
#   - third_party/upb/, except third_party/upb/third_party/lunit/ and
#     third_party/upb/third_party/utf8_range/
#     * Potentially linked into any compiled subpackage (but not pure-Python
#       subpackages, etc.)
#   - third_party/address_sorting/
#     * Potentially linked into any compiled subpackage (but not pure-Python
#       subpackages, etc.)
# MIT:
#   - third_party/upb/third_party/utf8_range
#     * Potentially linked into any compiled subpackage (but not pure-Python
#       subpackages, etc.)
#
# as well as the following which do not contribute to the base License field or
# any subpackage License field for the reasons noted:
#
# MPL-2.0:
#   - etc/roots.pem
#     * Truncated to an empty file in prep; a symlink to the shared system
#       certificates is used instead
#   - src/android/test/interop/app/src/main/assets/roots.pem
#     * Truncated to an empty file in prep
# ISC:
#   - src/boringssl/boringssl_prefix_symbols.h
#     * Removed in prep; not used when building with system OpenSSL
# BSD-3-Clause:
#   - src/objective-c/*.podspec and
#     templates/src/objective-c/*.podspec.template
#     * Unused since the Objective-C bindings are not currently built;
#       furthermore, these seem to be build-system files that would not
#       contribute their licenses to the binary RPM contents anyway
# NTP:
#   - third_party/cares/ares_build.h
#     * Removed in prep; header from system C-Ares used instead
# MIT:
#   - third_party/upb/third_party/lunit/
#     * Removed in prep, since there is no obvious way to run the upb tests
License:        Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND MIT
URL:            https://www.grpc.io
%global forgeurl https://github.com/grpc/grpc/
Source0:        %{forgeurl}/archive/v%{srcversion}/grpc-%{srcversion}.tar.gz
Source1:        %{gtest_url}/archive/%{gtest_commit}/%{gtest_dir}.tar.gz
#Source1:        #{gtest_url}/archive/release-#{gtest_version}/#{gtest_dir}.tar.gz
Source2:        %{envoy_api_url}/archive/%{envoy_api_commit}/%{envoy_api_dir}.tar.gz
Source3:        %{googleapis_url}/archive/%{googleapis_commit}/%{googleapis_dir}.tar.gz
Source4:        %{opencensus_proto_url}/archive/v%{opencensus_proto_version}/%{opencensus_proto_dir}.tar.gz
Source5:        %{xds_url}/archive/%{xds_commit}/%{xds_dir}.tar.gz

# Downstream grpc_cli man pages; hand-written based on “grpc_cli help” output.
Source100:      grpc_cli.1
Source101:      grpc_cli-ls.1
Source102:      grpc_cli-call.1
Source103:      grpc_cli-type.1
Source104:      grpc_cli-parse.1
Source105:      grpc_cli-totext.1
Source106:      grpc_cli-tojson.1
Source107:      grpc_cli-tobinary.1
Source108:      grpc_cli-help.1

# ~~~~ C (core) and C++ (cpp) ~~~~

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
%if %{with core_tests}
# Used on grpc_cli:
BuildRequires:  chrpath
%endif

BuildRequires:  pkgconfig(zlib)
BuildRequires:  cmake(gflags)
BuildRequires:  protobuf-compat-devel >= 3.21.9
BuildRequires:  protobuf-compat-compiler >= 3.21.9
BuildRequires:  pkgconfig(re2)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(libcares)
BuildRequires:  abseil-cpp-compat-devel
# Sets XXH_INCLUDE_ALL, which means xxhash is used as a header-only library
BuildRequires:  pkgconfig(libxxhash)
BuildRequires:  xxhash-static

%if %{with core_tests}
BuildRequires:  cmake(benchmark)
%if %{with system_gtest}
BuildRequires:  cmake(gtest)
BuildRequires:  pkgconfig(gmock)
%endif
%if %{with valgrind}
BuildRequires:  valgrind
%endif
%if %{with gdb}
BuildRequires:  gdb
%endif
%endif

# ~~~~ Python ~~~~

BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3dist(wheel)
BuildRequires:  python3dist(pip)

# grpcio (setup.py) setup_requires (with
#     GRPC_PYTHON_ENABLE_DOCUMENTATION_BUILD, which is NOT enabled):
# BuildRequires:  python3dist(sphinx)

# grpcio (setup.py) setup_requires (with
#     GRPC_PYTHON_ENABLE_DOCUMENTATION_BUILD, which is NOT enabled):
# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
BuildRequires:  python3dist(six) >= 1.10
# grpcio (setup.py) install_requires also has:
#   six>=1.5.2

# grpcio (setup.py) setup_requires (with GRPC_PYTHON_BUILD_WITH_CYTHON, or
# absent generated sources); also needed for grpcio_tools
# (tools/distrib/python/grpcio_tools/setup.py)
#
# Not yet compatible with Cython 3, due to errors like:
#
#   Error compiling Cython file:
#   ------------------------------------------------------------
#   ...
#       return 1
#     else:
#       return 0
#
#   cdef grpc_arg_pointer_vtable default_vtable
#   default_vtable.copy = &_copy_pointer
#                         ^
#   ------------------------------------------------------------
#
#   src/python/grpcio/grpc/_cython/_cygrpc/vtable.pyx.pxi:34:22: Cannot assign
#   type 'void *(*)(void *) except *' to 'void *(*)(void *) noexcept'
#
# See:
#   Cython 3.0.0b1 and its impact on packages in Fedora
#   https://github.com/cython/cython/issues/5305
BuildRequires: ((python3dist(cython) > 0.23) with (python3dist(cython) < 3~~))

# grpcio (setup.py) install_requires:
# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
#   futures>=2.2.0; python_version<'3.2'

# grpcio (setup.py) install_requires:
# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
#   enum34>=1.0.4; python_version<'3.4'

# grpcio_csds (src/python/grpcio_csds/setup.py) install_requires:
# grpcio_channelz (src/python/grpcio_channelz/setup.py) install_requires:
# grpcio_health_checking (src/python/grpcio_health_checking/setup.py)
#     install_requires:
# grpcio_reflection (src/python/grpcio_reflection/setup.py) install_requires:
# grpcio_status (src/python/grpcio_status/setup.py) install_requires:
# grpcio_testing (src/python/grpcio_testing/setup.py) install_requires:
# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
# grpcio_tools (tools/distrib/python/grpcio_tools/setup.py) install_requires:
BuildRequires:  python3-protobuf-compat >= 3.21.9

# grpcio_status (src/python/grpcio_status/setup.py) install_requires:
BuildRequires:  python3dist(googleapis-common-protos) >= 1.5.5

%if %{without bootstrap}
# grpcio_csds (src/python/grpcio_csds/setup.py) install_requires
BuildRequires:  python3dist(xds-protos) >= 0.0.7
%endif

# Several packages have dependencies on grpcio or grpcio_tools—and grpcio-tests
# depends on all of the other Python packages—which are satisfied within this
# package.
#
# Similarly, grpcio_admin depends on grpcio_channelz and grpcio_csds.

# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
BuildRequires:  python3dist(coverage) >= 4.0

# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
BuildRequires:  python3dist(oauth2client) >= 1.4.7

# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
BuildRequires:  python3dist(google-auth) >= 1.0.0

# grpcio_tests (src/python/grpcio_tests/setup.py) install_requires:
BuildRequires:  python3dist(requests) >= 2.14.2

%if %{with python_gevent_tests}
# Required for “test_gevent” tests:
BuildRequires:  python3dist(gevent)
%endif

# For stopping the port server
BuildRequires:  curl

# ~~~~ Miscellaneous ~~~~

# https://bugzilla.redhat.com/show_bug.cgi?id=1893533
%global _lto_cflags %{nil}

# Reference documentation, which is *not* enabled
# BuildRequires:  doxygen

BuildRequires:  ca-certificates
# For converting absolute symlinks in the buildroot to relative ones
BuildRequires:  symlinks

# Apply Fedora system crypto policies. Since this is Fedora-specific, the patch
# is not suitable for upstream.
# https://docs.fedoraproject.org/en-US/packaging-guidelines/CryptoPolicies/#_cc_applications
#
# In fact, this may not be needed, since only testing code is patched.
Patch0:          grpc-1.39.0-system-crypto-policies.patch
# Fix errors like:
#   TypeError: super(type, obj): obj must be an instance or subtype of type
# It is not clear why these occur.
Patch1:          grpc-1.36.4-python-grpcio_tests-fixture-super.patch
# Skip tests requiring non-loopback network access when the
# FEDORA_NO_NETWORK_TESTS environment variable is set.
Patch2:          grpc-1.40.0-python-grpcio_tests-make-network-tests-skippable.patch
# A handful of compression tests miss the compression ratio threshold. It seems
# to be inconsistent which particular combinations fail in a particular test
# run. It is not clear that this is a real problem. Any help in understanding
# the actual cause well enough to fix this or usefully report it upstream is
# welcome.
Patch3:          grpc-1.48.0-python-grpcio_tests-skip-compression-tests.patch
# The upstream requirement to link gtest/gmock from grpc_cli is spurious.
# Remove it. We still have to build the core tests and link a test library
# (libgrpc++_test_config.so…)
#Patch4:          grpc-1.37.0-grpc_cli-do-not-link-gtest-gmock.patch
# Fix confusion about path to python_wrapper.sh in httpcli/httpscli tests. I
# suppose that the unpatched code must be correct for how upstream runs the
# tests, somehow.
Patch5:          grpc-1.45.0-python_wrapper-path.patch
# Skip failing ChannelzServicerTest tests on Python 3.11
#
# Partially works around:
#
# grpc fails to build with Python 3.11: AttributeError: module 'inspect' has no
#   attribute 'getargspec'
# https://bugzilla.redhat.com/show_bug.cgi?id=2095027
#
# TODO: Attempt to reproduce this outside the RPM build environment and submit
# a useful/actionable upstream bug report.
Patch6:          grpc-1.46.3-ChannelzServicerTest-python3.11-regressions.patch
# Running Python “test_lite”, in grpcio_tests,
# unit._dynamic_stubs_test.DynamicStubTest.test_grpc_tools_unimportable hangs.
# This may be related to:
#   [FLAKE] DynamicStubTest timeout under gevent macOS
#   https://github.com/grpc/grpc/issues/25368
# The patch simply skips the test.
Patch7:          grpc-1.48.0-python-grpcio_tests-DynamicStubTest-hang.patch
# Use CMake variables for paths in pkg-config files
#
# Use @gRPC_INSTALL_LIBDIR@ for libdir; this fixes an incorrect
# -L/usr/lib on multilib Linux systems where that is the 32-bit library
# path and the correct path is /usr/lib64.
#
# Use @gRPC_INSTALL_INCLUDEDIR@ for consistency.
#
# See also:
# https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/
#   thread/P2N35UMQVEXPILAF47RQB53MWRV2GM3J/
#
# https://github.com/grpc/grpc/pull/31671
Patch8:          %{forgeurl}/pull/31671.patch

# [http2] Dont drop connections on metadata limit exceeded (#32309)
#
# * [http] Dont drop connections on metadata limit exceeded
#
# * remove bad test
#
# * Automated change: Fix sanity tests
# https://github.com/grpc/grpc/commit/29d8beee0ac2555773b2a2dda5601c74a95d6c10
# https://github.com/grpc/grpc/pull/32309
#
# Fixes CVE-2023-32732
# https://nvd.nist.gov/vuln/detail/CVE-2023-32732
# CVE-2023-32732 grpc: denial of service [fedora-all]
# https://bugzilla.redhat.com/show_bug.cgi?id=2214470
#
# Backported to 1.48.4.
Patch9:          0001-http2-Dont-drop-connections-on-metadata-limit-exceed.patch

Requires:       %{name}-data = %{version}-%{release}

# Upstream https://github.com/protocolbuffers/upb does not support building
# with anything other than Bazel, and Bazel is not likely to make it into
# Fedora anytime soon due to its nightmarish collection of dependencies.
# Monitor this at https://bugzilla.redhat.com/show_bug.cgi?id=1470842.
# Therefore upb cannot be packaged for Fedora, and we must use the bundled
# copy.
#
# Note that upstream has never chosen a version, and it is not clear from which
# commit the bundled copy was taken or forked.
#
# Note also that libupb is installed in the system-wide linker path, which will
# be a problem if upb is ever packaged separately. We will cross that bridge if
# we get there.
Provides:       bundled(upb)
# The bundled upb itself bundles https://github.com/cyb70289/utf8; we follow
# upstream in styling this as “utf8_range”. It cannot reasonably be unbundled
# because the original code is not structured for distribution as a library (it
# does not even include header files). It is not clear which upstream commit
# was used.
Provides:       bundled(utf8_range)
Provides:       %{name} = %{version}-%{release}


# Regarding third_party/address_sorting: this looks a bit like a bundled
# library, but it is not. From a source file comment:
#   This is an adaptation of Android's implementation of RFC 6724 (in Android’s
#   getaddrinfo.c). It has some cosmetic differences from Android’s
#   getaddrinfo.c, but Android’s getaddrinfo.c was used as a guide or example
#   of a way to implement the RFC 6724 spec when this was written.

%description
gRPC is a modern open source high performance RPC framework that can run in any
environment. It can efficiently connect services in and across data centers
with pluggable support for load balancing, tracing, health checking and
authentication. It is also applicable in last mile of distributed computing to
connect devices, mobile applications and browsers to backend services.

The main usage scenarios:

  • Efficiently connecting polyglot services in microservices style
    architecture
  • Connecting mobile devices, browser clients to backend services
  • Generating efficient client libraries

Core Features that make it awesome:

  • Idiomatic client libraries in 10 languages
  • Highly efficient on wire and with a simple service definition framework
  • Bi-directional streaming with http/2 based transport
  • Pluggable auth, tracing, load balancing and health checking

This package provides the shared C core library.


%package data
Summary:        Data for gRPC bindings
License:        Apache-2.0
BuildArch:      noarch

Requires:       ca-certificates
Provides:       %{name}-data = %{version}-%{release}

%description data
Common data for gRPC bindings: currently, this contains only a symbolic link to
the system shared TLS certificates.


%package doc
Summary:        Documentation and examples for gRPC
License:        Apache-2.0
BuildArch:      noarch

Obsoletes:      python-grpcio-compat-doc < 1.26.0-13
Provides:       python-grpcio-compat-doc = %{version}-%{release}
Provides:       python-grpcio-compat-admin-doc = %{version}-%{release}
Provides:       python-grpcio-compat-csds-doc = %{version}-%{release}
Provides:       python-grpcio-compat-channelz-doc = %{version}-%{release}
Provides:       python-grpcio-compat-health-checking-doc = %{version}-%{release}
Provides:       python-grpcio-compat-reflection-doc = %{version}-%{release}
Provides:       python-grpcio-compat-status-doc = %{version}-%{release}
Provides:       python-grpcio-compat-testing-doc = %{version}-%{release}
Provides:       %{name}-doc = %{version}-%{release}

%description doc
Documentation and examples for gRPC, including Markdown documentation sources
for the following:

  • C (core)
    ○ API
    ○ Internals
  • C++
    ○ API
    ○ Internals
  • Objective C
    ○ API
    ○ Internals
  • Python
    ○ grpcio
    ○ grpcio_admin
    ○ grpcio_csds
    ○ grpcio_channelz
    ○ grpcio_health_checking
    ○ grpcio_reflection
    ○ grpcio_status
    ○ grpcio_testing

For rendered HTML documentation, please see https://grpc.io/docs/.


%package cpp
Summary:        C++ language bindings for gRPC
# License:        same as base package

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-cpp%{?_isa} = %{version}-%{release}

Provides:       bundled(upb)
Provides:       bundled(utf8_range)
Provides:       %{name}-cpp = %{version}-%{release}

%description cpp
C++ language bindings for gRPC.


%package plugins
Summary:        Protocol buffers compiler plugins for gRPC
# License:        same as base package

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-cpp%{?_isa} = %{version}-%{release}
Requires:       protobuf-compat-compiler >= 3.21.9

Provides:       bundled(upb)
Provides:       bundled(utf8_range)
Provides:       %{name}-plugins = %{version}-%{release}

%description plugins
Plugins to the protocol buffers compiler to generate gRPC sources.


%package cli
Summary:        Command-line tool for gRPC
# License:        same as base package

Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-cpp%{?_isa} = %{version}-%{release}

Provides:       bundled(upb)
Provides:       bundled(utf8_range)
Provides:       %{name}-cli = %{version}-%{release}

%description cli
The command line tool can do the following things:

  • Send unary rpc.
  • Attach metadata and display received metadata.
  • Handle common authentication to server.
  • Infer request/response types from server reflection result.
  • Find the request/response types from a given proto file.
  • Read proto request in text form.
  • Read request in wire form (for protobuf messages, this means serialized
    binary form).
  • Display proto response in text form.
  • Write response in wire form to a file.


%package devel
Summary:        Development files for gRPC library
# License:        same as base package
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name}-cpp%{?_isa} = %{version}-%{release}
Requires:       %{name}-plugins%{?_isa} = %{version}-%{release}

# grpc/impl/codegen/port_platform.h includes linux/version.h
Requires:       kernel-headers%{?_isa}
# grpcpp/impl/codegen/config_protobuf.h includes google/protobuf/…
Requires:       protobuf-compat-devel >= 3.21.9
# grpcpp/test/mock_stream.h includes gmock/gmock.h
Requires:       pkgconfig(gmock)
# grpcpp/impl/codegen/sync.h includes absl/synchronization/mutex.h
# grpc.pc has -labsl_[…]
Requires:       abseil-cpp-compat-devel%{?_isa}
# grpc.pc has -lre2
Requires:       pkgconfig(re2)
# grpc.pc has -lcares
Requires:       cmake(c-ares)
# grpc.pc has -lz
Requires:       pkgconfig(zlib)

%description devel
Development headers and files for gRPC libraries (both C and C++).


%package -n python3-grpcio
Summary:        Python language bindings for gRPC
# License:        same as base package

# Note that the Python package has no runtime dependency on the base C library;
# everything it needs is linked statically. It is not practical to change this,
# and since they both come from the same source RPM, we do not need to attempt
# to do so.
Requires:       %{name}-data = %{version}-%{release}

Provides:       bundled(upb)
Provides:       bundled(utf8_range)
Provides:       %{name}-devel = %{version}-%{release}

%description -n python3-grpcio
Python language bindings for gRPC (HTTP/2-based RPC framework).


%global grpcio_egg %{python3_sitearch}/grpcio-%{pyversion}-py%{python3_version}.egg-info
%{?python_extras_subpkg:%python_extras_subpkg -n python3-grpcio -i %{grpcio_egg} protobuf}


%package -n python3-grpcio-tools
Summary:       Package for gRPC Python tools
# License:        same as base package

Provides:       bundled(upb)
Provides:       bundled(utf8_range)
Provides:       python3-grpcio-compat-tools = %{version}-%{release}

%description -n python3-grpcio-tools
Package for gRPC Python tools.


%if %{without bootstrap}
%package -n python3-grpcio-admin
Summary:        A collection of admin services
License:        Apache-2.0
BuildArch:      noarch
Provides:       python3-grpcio-compat-adin = %{version}-%{release}

%description -n python3-grpcio-admin
gRPC Python Admin Interface Package
===================================

Debugging gRPC library can be a complex task. There are many configurations and
internal states, which will affect the behavior of the library. This Python
package will be the collection of admin services that are exposing debug
information. Currently, it includes:

* Channel tracing metrics (grpcio-channelz)
* Client Status Discovery Service (grpcio-csds)

Here is a snippet to create an admin server on "localhost:50051":

    server = grpc.server(ThreadPoolExecutor())
    port = server.add_insecure_port('localhost:50051')
    grpc_admin.add_admin_servicers(self._server)
    server.start()

Welcome to explore the admin services with CLI tool "grpcdebug":
https://github.com/grpc-ecosystem/grpcdebug.

For any issues or suggestions, please send to
https://github.com/grpc/grpc/issues.
%endif


%if %{without bootstrap}
%package -n python3-grpcio-csds
Summary:        xDS configuration dump library
License:        Apache-2.0
BuildArch:      noarch
Provides:       python3-grpcio-compat-csds = %{version}-%{release}

%description -n python3-grpcio-csds
gRPC Python Client Status Discovery Service package
===================================================

CSDS is part of the Envoy xDS protocol:
https://www.envoyproxy.io/docs/envoy/latest/api-v3/service/status/v3/csds.proto.
It allows the gRPC application to programmatically expose the received traffic
configuration (xDS resources). Welcome to explore with CLI tool "grpcdebug":
https://github.com/grpc-ecosystem/grpcdebug.

For any issues or suggestions, please send to
https://github.com/grpc/grpc/issues.
%endif


%package -n python3-grpcio-channelz
Summary:        Channel Level Live Debug Information Service for gRPC
License:        Apache-2.0
BuildArch:      noarch
Provides:       python3-grpcio-compat-channelz = %{version}-%{release}

%description -n python3-grpcio-channelz
gRPC Python Channelz package
============================

Channelz is a live debug tool in gRPC Python.


%package -n python3-grpcio-health-checking
Summary:        Standard Health Checking Service for gRPC
License:        Apache-2.0
BuildArch:      noarch
Provides:       python3-grpcio-compat-health-checking = %{version}-%{release}

%description -n python3-grpcio-health-checking
gRPC Python Health Checking
===========================

Reference package for GRPC Python health checking.


%package -n python3-grpcio-reflection
Summary:        Standard Protobuf Reflection Service for gRPC
License:        Apache-2.0
BuildArch:      noarch
Provides:       python3-grpcio-compat-reflection = %{version}-%{release}

%description -n python3-grpcio-reflection
gRPC Python Reflection package
==============================

Reference package for reflection in GRPC Python.


%package -n python3-grpcio-status
Summary:        Status proto mapping for gRPC
License:        Apache-2.0
BuildArch:      noarch
Provides:       python3-grpcio-compat-status = %{version}-%{release}

%description -n python3-grpcio-status
gRPC Python Status Proto
===========================

Reference package for GRPC Python status proto mapping.


%package -n python3-grpcio-testing
Summary:        Testing utilities for gRPC Python
License:        Apache-2.0
BuildArch:      noarch
Provides:       python3-grpcio-compat-testing = %{version}-%{release}

%description -n python3-grpcio-testing
gRPC Python Testing Package
===========================

Testing utilities for gRPC Python.


%prep
%autosetup -p1 -n grpc-%{srcversion}

cp -p third_party/upb/third_party/utf8_range/LICENSE LICENSE-utf8_range

echo '===== Patching grpcio_tools for system protobuf =====' 2>&1
# Build python3-grpcio_tools against system protobuf packages instead of
# expecting a git submodule. Must also add requisite linker flags using
# GRPC_PYTHON_LDFLAGS. This was formerly done by
# grpc-VERSION-python-grpcio_tools-use-system-protobuf.patch, but it had to be
# tediously but trivially rebased every patch release as the CC_FILES list
# changed, so we automated the patch.
sed -r -i \
    -e "s/^(# AUTO-GENERATED .*)/\\1\\n\
# Then, modified by hand to build with an external system protobuf\
# installation./" \
    -e 's/^(CC_FILES=\[).*(\])/\1\2/' \
    -e "s@^((CC|PROTO)_INCLUDE=')[^']+'@\1%{_includedir}'@" \
    -e '/^PROTOBUF_SUBMODULE_VERSION=/d' \
    'tools/distrib/python/grpcio_tools/protoc_lib_deps.py'

echo '===== Preparing gtest/gmock =====' 2>&1
%if %{without system_gtest}
# Copy in the needed gtest/gmock implementations.
%setup -q -T -D -b 1 -n grpc-%{srcversion}
rm -rvf 'third_party/googletest'
mv '../%{gtest_dir}' 'third_party/googletest'
%else
# Patch CMakeLists for external gtest/gmock.
#
#  1. Create dummy sources, adding a typedef so the translation unit is not
#     empty, rather than removing references to these sources from
#     CMakeLists.txt. This is so that we do not end up with executables with no
#     sources, only libraries, which is a CMake error.
#  2. Either remove references to the corresponding include directories, or
#     create the directories and leave them empty.
#  3. “Stuff” the external library into the target_link_libraries() for each
#     test by noting that GMock/GTest/GFlags are always used together.
for gwhat in test mock
do
  mkdir -p "third_party/googletest/google${gwhat}/src" \
      "third_party/googletest/google${gwhat}/include"
  echo "typedef int dummy_${gwhat}_type;" \
      > "third_party/googletest/google${gwhat}/src/g${gwhat}-all.cc"
done
sed -r -i 's/^([[:blank:]]*)(\$\{_gRPC_GFLAGS_LIBRARIES\})/'\
'\1\2\n\1gtest\n\1gmock/' CMakeLists.txt
%endif

# Extract the source tarballs needed for their .proto files, which upstream
# expects to download at build time.
%setup -q -T -D -b 2 -n grpc-%{srcversion}
%setup -q -T -D -b 3 -n grpc-%{srcversion}
%setup -q -T -D -b 4 -n grpc-%{srcversion}
%setup -q -T -D -b 5 -n grpc-%{srcversion}
{
  awk '$1 ~ /^(#|$)/ { next }; 1' <<'EOF'
../%{envoy_api_dir}/ third_party/envoy-api/
../%{googleapis_dir}/ third_party/googleapis/
../%{opencensus_proto_dir}/ third_party/opencensus-proto/
../%{xds_dir}/ third_party/xds/
EOF
} | while read -r fromdir todir
do
  # Remove everything from the external source tree except the .proto files, to
  # prove that none of it is bundled.
  find "${fromdir}" -type f ! -name '*.proto' -print -delete
  # Remove the empty directory corresponding to the git submodule
  rm -rvf "${todir}"
  # Move the extracted source, to the location where the git submodule would be
  # in a git checkout that included it.
  mv "${fromdir}" "${todir}"
done

echo '===== Removing bundled xxhash =====' 2>&1
# Remove bundled xxhash
rm -rvf third_party/xxhash
# Since grpc sets XXH_INCLUDE_ALL wherever it uses xxhash, it is using xxhash
# as a header-only library. This means we can replace it with the system copy
# by doing nothing further; xxhash.h is in the system include path and will be
# found instead, and there are no linker flags to add. See also
# https://github.com/grpc/grpc/issues/25945.

echo '===== Fixing permissions =====' 2>&1
# https://github.com/grpc/grpc/pull/27069
find . -type f -perm /0111 \
    -exec gawk '!/^#!/ { print FILENAME }; { nextfile }' '{}' '+' |
  xargs -r chmod -v a-x

echo '===== Removing selected unused sources =====' 2>&1
# Remove unused sources that have licenses not in the License field, to ensure
# they are not accidentally used in the build. See the comment above the base
# package License field for more details.
rm -rfv \
    src/boringssl/boringssl_prefix_symbols.h \
    third_party/cares/ares_build.h \
    third_party/upb/third_party/lunit
# Since we are replacing roots.pem with a symlink to the shared system
# certificates, we do not include its license (MPLv2.0) in any License field.
# We remove its contents so that, if we make a packaging mistake, we will have
# a bug but not an incorrect License field.
echo '' > etc/roots.pem

# Remove Android sources and examples. We do not need these on Linux, and they
# have some issues that will be flagged when reviewing the package, such as:
#   - Another copy of the MPLv2.0-licensed certificate bundle from
#     etc/roots.pem, in src/android/test/interop/app/src/main/assets/roots.pem
#   - Pre-built jar files at
#     src/android/test/interop/gradle/wrapper/gradle-wrapper.jar and
#     examples/android/helloworld/gradle/wrapper/gradle-wrapper.jar
rm -rvf examples/android src/android

# Drop the NodeJS example’s package-lock.json file, which will hopefully keep
# us from having bugs filed due to CVE’s in its (unpackaged) recursive
# dependencies.
rm -vf examples/node/package-lock.json

# Remove unwanted .gitignore files, generally in examples. One could argue that
# a sample .gitignore file is part of the example, but, well, we’re not going
# to do that.
find . -type f -name .gitignore -print -delete

echo '===== Fixing shebangs =====' 2>&1
# Find executables with /usr/bin/env shebangs in the examples, and fix them.
find . -type f -perm /0111 -exec gawk \
    '/^#!\/usr\/bin\/env[[:blank:]]/ { print FILENAME }; { nextfile }' \
    '{}' '+' |
  xargs -r sed -r -i '1{s|^(#!/usr/bin/)env[[:blank:]]+([^[:blank:]]+)|\1\2|}'

echo '===== Fixing hard-coded C++ standard =====' 2>&1
# We need to adjust the C++ standard to avoid abseil-related linker errors. For
# the main C++ build, we can use CMAKE_CXX_STANDARD. For extensions, examples,
# etc., we must patch.
sed -r -i 's/(std=c\+\+)14/\1%{cpp_std}/g' \
    setup.py grpc.gyp Rakefile \
    examples/cpp/*/Makefile \
    examples/cpp/*/CMakeLists.txt \
    tools/run_tests/artifacts/artifact_targets.py \
    tools/distrib/python/grpcio_tools/setup.py

# Relax minimum version for python3-google-auth to support RHEL8
sed -i 's|google-auth>=1.17.2|google-auth>=1.0.0|' src/python/grpcio_tests/setup.py
sed -i 's|google-auth>=1.17.2|google-auth>=1.0.0|' tools/run_tests/helper_scripts/build_python.sh
sed -i 's|google-auth==1.24.0|google-auth>=1.0.0|' requirements.bazel.txt

%build
# ~~~~ C (core) and C++ (cpp) ~~~~

# Length of the prefix (e.g. /usr), plus a trailing slash (or newline), plus
# one, to get the index of the first relative path character after the prefix.
# This is needed because gRPC_INSTALL_*DIR options expect paths relative to the
# prefix, and supplying absolute paths causes certain subtle problems.
%global rmprefix %(echo $(($(wc -c <<<'%{_prefix}')+1)))

echo '===== Building C (core) and C++ components =====' 2>&1
# We could use either make or ninja as the backend; ninja is faster and has no
# disadvantages (except a small additional BR, given we already need Python)
#
# We need to adjust the C++ standard to avoid abseil-related linker errors.
%cmake \
    -DgRPC_INSTALL:BOOL=ON \
    -DCMAKE_CXX_STANDARD:STRING=%{cpp_std} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DgRPC_INSTALL_BINDIR:PATH=%(cut -b %{rmprefix}- <<<'%{_bindir}') \
    -DgRPC_INSTALL_LIBDIR:PATH=%(cut -b %{rmprefix}- <<<'%{_libdir}') \
    -DgRPC_INSTALL_INCLUDEDIR:PATH=%(cut -b %{rmprefix}- <<<'%{_includedir}') \
    -DgRPC_INSTALL_CMAKEDIR:PATH=%(cut -b %{rmprefix}- <<<'%{_libdir}/cmake/grpc') \
    -DgRPC_INSTALL_SHAREDIR:PATH=%(cut -b %{rmprefix}- <<<'%{_datadir}/grpc') \
    -DgRPC_BUILD_TESTS:BOOL=%{?with_core_tests:ON}%{?!with_core_tests:OFF} \
    -DgRPC_BUILD_CODEGEN:BOOL=ON \
    -DgRPC_BUILD_CSHARP_EXT:BOOL=ON \
    -DgRPC_BACKWARDS_COMPATIBILITY_MODE:BOOL=OFF \
    -DgRPC_ZLIB_PROVIDER:STRING='package' \
    -DgRPC_CARES_PROVIDER:STRING='package' \
    -DgRPC_RE2_PROVIDER:STRING='package' \
    -DgRPC_SSL_PROVIDER:STRING='package' \
    -DgRPC_PROTOBUF_PROVIDER:STRING='package' \
    -DgRPC_PROTOBUF_PACKAGE_TYPE:STRING='MODULE' \
    -DgRPC_BENCHMARK_PROVIDER:STRING='package' \
    -DgRPC_ABSL_PROVIDER:STRING='package' \
    -DgRPC_USE_PROTO_LITE:BOOL=OFF \
    -DgRPC_BUILD_GRPC_CPP_PLUGIN:BOOL=ON \
    -DgRPC_BUILD_GRPC_CSHARP_PLUGIN:BOOL=ON \
    -DgRPC_BUILD_GRPC_NODE_PLUGIN:BOOL=ON \
    -DgRPC_BUILD_GRPC_OBJECTIVE_C_PLUGIN:BOOL=ON \
    -DgRPC_BUILD_GRPC_PHP_PLUGIN:BOOL=ON \
    -DgRPC_BUILD_GRPC_PYTHON_PLUGIN:BOOL=ON \
    -DgRPC_BUILD_GRPC_RUBY_PLUGIN:BOOL=ON \
    -GNinja
%cmake_build
# ~~~~ Python ~~~~

echo '===== Building Python grpcio package =====' 2>&1
# Since there are some interdependencies in the Python packages (e.g., many
# have setup_requires: grpcio-tools), we do temporary installs of built
# packages into a local directory as needed, and add it to the PYTHONPATH.
PYROOT="${PWD}/%{_vpath_builddir}/pyroot"
if [ -n "${PYTHONPATH-}" ]; then PYTHONPATH="${PYTHONPATH}:"; fi
PYTHONPATH="${PYTHONPATH-}${PYROOT}%{python3_sitelib}"
PYTHONPATH="${PYTHONPATH}:${PYROOT}%{python3_sitearch}"
export PYTHONPATH

# ~~ grpcio ~~
export GRPC_PYTHON_BUILD_WITH_CYTHON='True'
export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL='True'
export GRPC_PYTHON_BUILD_SYSTEM_ZLIB='True'
export GRPC_PYTHON_BUILD_SYSTEM_CARES='True'
export GRPC_PYTHON_BUILD_SYSTEM_RE2='True'
export GRPC_PYTHON_BUILD_SYSTEM_ABSL='True'
export GRPC_PYTHON_DISABLE_LIBC_COMPATIBILITY='True'
export GRPC_PYTHON_ENABLE_DOCUMENTATION_BUILD='False'
# Use the upstream defaults for GRPC_PYTHON_CFLAGS adn GRPC_PYTHON_LDFLAGS,
# except:
#
# - Add any flags necessary for using the system protobuf library.
# - Drop -lpthread and -lrt, since these are not needed on glibc 2.34 and
#   later.
# - Do not link libgcc statically (-static-libgcc).
#
# See also:
# https://developers.redhat.com/articles/2021/12/17/why-glibc-234-removed-libpthread
export GRPC_PYTHON_CFLAGS="$(
  pkg-config --cflags protobuf
) -std=c++%{cpp_std} -fvisibility=hidden -fno-wrapv -fno-exceptions"
export GRPC_PYTHON_LDFLAGS="$(pkg-config --libs protobuf)"
%py3_build
%{__python3} %{py_setup} %{?py_setup_args} install \
    -O1 --skip-build --root "${PYROOT}"

# ~~ grpcio-tools ~~
echo '===== Building Python grpcio_tools package =====' 2>&1
pushd "tools/distrib/python/grpcio_tools/" >/dev/null
# When copying more things in here, make sure the subpackage License field
# stays correct. We need copies, not symlinks, so that the “graft” in
# MANIFEST.in works.
mkdir -p grpc_root/src
for srcdir in compiler
do
  cp -rp "../../../../src/${srcdir}" "grpc_root/src/"
done
cp -rp '../../../../include' 'grpc_root/'
# We must set GRPC_PYTHON_CFLAGS and GRPC_PYTHON_LDFLAGS again; grpcio_tools
# does not have the same default upstream flags as grpcio does, and it needs to
# link the protobuf compiler library.
export GRPC_PYTHON_CFLAGS="-fno-wrapv -frtti $(pkg-config --cflags protobuf)"
export GRPC_PYTHON_LDFLAGS="$(pkg-config --libs protobuf) -lprotoc"
%py3_build
# Remove unwanted shebang from grpc_tools.protoc source file, which will be
# installed without an executable bit:
find . -type f -name protoc.py -execdir sed -r -i '1{/^#!/d}' '{}' '+'
%{__python3} %{py_setup} %{?py_setup_args} install \
    -O1 --skip-build --root "${PYROOT}"
popd >/dev/null

echo '===== Building pure-Python packages =====' 1>&2
for suffix in channelz %{?!with_bootstrap:csds admin} health_checking \
    reflection status testing tests
do
  echo "----> grpcio_${suffix} <----" 1>&2
  pushd "src/python/grpcio_${suffix}/" >/dev/null
  if ! echo "${suffix}" | grep -E "^(admin|csds)$" >/dev/null
  then
    %{__python3} %{py_setup} %{?py_setup_args} preprocess
  fi
  if ! echo "${suffix}" | grep -E "^(admin|csds|testing)$" >/dev/null
  then
    %{__python3} %{py_setup} %{?py_setup_args} build_package_protos
  fi
  %py3_build
  %{__python3} %{py_setup} %{?py_setup_args} install \
      -O1 --skip-build --root "${PYROOT}"
  popd >/dev/null
done


%install
# ~~~~ C (core) and C++ (cpp) ~~~~
%cmake_install

%if %{with core_tests}
# For some reason, grpc_cli is not installed. Do it manually.
install -t '%{buildroot}%{_bindir}' -p -D '%{_vpath_builddir}/grpc_cli'
# grpc_cli build does not respect CMAKE_INSTALL_RPATH
# https://github.com/grpc/grpc/issues/25176
chrpath --delete '%{buildroot}%{_bindir}/grpc_cli'

# This library is also required for grpc_cli; it is built as part of the test
# code.
install -t '%{buildroot}%{_libdir}' -p \
    '%{_vpath_builddir}/libgrpc++_test_config.so.%{cpp_so_version}'
chrpath --delete \
    '%{buildroot}%{_libdir}/libgrpc++_test_config.so.%{cpp_so_version}'

install -d '%{buildroot}/%{_mandir}/man1'
install -t '%{buildroot}/%{_mandir}/man1' -p -m 0644 \
    %{SOURCE100} %{SOURCE101} %{SOURCE102} %{SOURCE103} %{SOURCE104} \
    %{SOURCE106} %{SOURCE107} %{SOURCE108}
%endif

# Remove any static libraries that may have been installed against our wishes
find %{buildroot} -type f -name '*.a' -print -delete
# Fix wrong permissions on installed headers
find %{buildroot}%{_includedir}/grpc* -type f -name '*.h' -perm /0111 \
    -execdir chmod -v a-x '{}' '+'

# ~~~~ Python ~~~~

# Since several packages have an install_requires: grpcio-tools, we must ensure
# the buildroot Python site-packages directories are in the PYTHONPATH.
pushd '%{buildroot}'
PYROOT="${PWD}"
popd
if [ -n "${PYTHONPATH-}" ]; then PYTHONPATH="${PYTHONPATH}:"; fi
PYTHONPATH="${PYTHONPATH-}${PYROOT}%{python3_sitelib}"
PYTHONPATH="${PYTHONPATH}:${PYROOT}%{python3_sitearch}"
export PYTHONPATH

# ~~ grpcio ~~
%py3_install

# ~~ grpcio-tools ~~
pushd "tools/distrib/python/grpcio_tools/" >/dev/null
%py3_install
popd >/dev/null

# ~~ pure-python modules grpcio-* ~~
for suffix in channelz %{?!with_bootstrap:csds admin} health_checking \
    reflection status testing
do
  pushd "src/python/grpcio_${suffix}/" >/dev/null
  %py3_install
  popd >/dev/null
done
# The grpcio_tests package should not be installed; it would provide top-level
# packages with generic names like “tests” or “tests_aio”.

# ~~~~ Miscellaneous ~~~~

# Replace copies of the certificate bundle with symlinks to the shared system
# certificates. This has the following benefits:
#   - Reduces duplication and save space
#   - Respects system-wide administrative trust configuration
#   - Keeps “MPLv2.0” from having to be added to a number of License fields
%global sysbundle %{_sysconfdir}/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
# We do not own this file; we temporarily install it in the buildroot so we do
# not have dangling symlinks.
install -D -t "%{buildroot}$(dirname '%{sysbundle}')" -m 0644 '%{sysbundle}'

find '%{buildroot}' -type f -name 'roots.pem' |
  while read -r fn
  do
    ln -s -f "%{buildroot}%{sysbundle}" "${fn}"
    symlinks -c -o "$(dirname "${fn}")"
  done

rm -rvf "%{buildroot}$(dirname '%{sysbundle}')"

# ~~ documentation and examples ~~

install -D -t '%{buildroot}%{_pkgdocdir}' -m 0644 -p AUTHORS *.md
cp -rvp doc examples '%{buildroot}%{_pkgdocdir}'


%files
%license LICENSE NOTICE.txt LICENSE-utf8_range
%{_libdir}/libaddress_sorting.so.%{c_so_version}*
%{_libdir}/libgpr.so.%{c_so_version}*
%{_libdir}/libgrpc.so.%{c_so_version}*
%{_libdir}/libgrpc_unsecure.so.%{c_so_version}*
%{_libdir}/libupb.so.%{c_so_version}*


%files data
%license LICENSE NOTICE.txt
%dir %{_datadir}/grpc
%{_datadir}/grpc/roots.pem


%files doc
%license LICENSE NOTICE.txt
%{_pkgdocdir}


%files cpp
%{_libdir}/libgrpc++.so.%{cpp_so_version}*
%{_libdir}/libgrpc++_alts.so.%{cpp_so_version}*
%{_libdir}/libgrpc++_error_details.so.%{cpp_so_version}*
%{_libdir}/libgrpc++_reflection.so.%{cpp_so_version}*
%{_libdir}/libgrpc++_unsecure.so.%{cpp_so_version}*
%{_libdir}/libgrpc_plugin_support.so.%{cpp_so_version}*

%{_libdir}/libgrpcpp_channelz.so.%{cpp_so_version}*


%if %{with core_tests}
%files cli
%{_bindir}/grpc_cli
%{_libdir}/libgrpc++_test_config.so.%{cpp_so_version}
%{_mandir}/man1/grpc_cli.1*
%{_mandir}/man1/grpc_cli-*.1*
%endif


%files plugins
# These are for program use and do not offer a CLI for the end user, so they
# should really be in %%{_libexecdir}; however, too many downstream users
# expect them in $PATH to change this for the time being.
%{_bindir}/grpc_*_plugin


%files devel
%{_libdir}/libaddress_sorting.so
%{_libdir}/libgpr.so
%{_libdir}/libgrpc.so
%{_libdir}/libgrpc_unsecure.so
%{_libdir}/libupb.so
%{_includedir}/grpc
%{_libdir}/pkgconfig/gpr.pc
%{_libdir}/pkgconfig/grpc.pc
%{_libdir}/pkgconfig/grpc_unsecure.pc
%{_libdir}/cmake/grpc

%{_libdir}/libgrpc++.so
%{_libdir}/libgrpc++_alts.so
%{_libdir}/libgrpc++_error_details.so
%{_libdir}/libgrpc++_reflection.so
%{_libdir}/libgrpc++_unsecure.so
%{_libdir}/libgrpc_plugin_support.so
%{_includedir}/grpc++
%{_libdir}/pkgconfig/grpc++.pc
%{_libdir}/pkgconfig/grpc++_unsecure.pc

%{_libdir}/libgrpcpp_channelz.so
%{_includedir}/grpcpp


%files -n python3-grpcio
%license LICENSE NOTICE.txt LICENSE-utf8_range
%{python3_sitearch}/grpc
%{python3_sitearch}/grpcio-%{pyversion}-py%{python3_version}.egg-info


%files -n python3-grpcio-tools
%license LICENSE NOTICE.txt LICENSE-utf8_range
%{python3_sitearch}/grpc_tools
%{python3_sitearch}/grpcio_tools-%{pyversion}-py%{python3_version}.egg-info


%if %{without bootstrap}
%files -n python3-grpcio-admin
%{python3_sitelib}/grpc_admin
%{python3_sitelib}/grpcio_admin-%{pyversion}-py%{python3_version}.egg-info
%endif


%files -n python3-grpcio-channelz
%{python3_sitelib}/grpc_channelz
%{python3_sitelib}/grpcio_channelz-%{pyversion}-py%{python3_version}.egg-info


%if %{without bootstrap}
%files -n python3-grpcio-csds
%{python3_sitelib}/grpc_csds
%{python3_sitelib}/grpcio_csds-%{pyversion}-py%{python3_version}.egg-info
%endif


%files -n python3-grpcio-health-checking
%{python3_sitelib}/grpc_health
%{python3_sitelib}/grpcio_health_checking-%{pyversion}-py%{python3_version}.egg-info


%files -n python3-grpcio-reflection
%{python3_sitelib}/grpc_reflection
%{python3_sitelib}/grpcio_reflection-%{pyversion}-py%{python3_version}.egg-info


%files -n python3-grpcio-status
%{python3_sitelib}/grpc_status
%{python3_sitelib}/grpcio_status-%{pyversion}-py%{python3_version}.egg-info


%files -n python3-grpcio-testing
%{python3_sitelib}/grpc_testing
%{python3_sitelib}/grpcio_testing-%{pyversion}-py%{python3_version}.egg-info


%changelog
* Sun Mar 05 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.4-4
- Post-bootstrap rebuild for abseil-cpp-20230125

* Sat Mar 04 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.4-3
- Bootstrap for abseil-cpp-20230125

* Sat Mar 04 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.4-2
- Skip a couple of new failing tests on aarch64 for abseil-cpp-20230125.0

* Thu Mar 02 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.4-1
- Update to 1.48.4

* Thu Feb 09 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.3-1
- Update to 1.48.3 (close RHBZ#2126980)

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 1.48.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Tue Jan 10 2023 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.2-2
- Update License to include header-only dependencies

* Sat Dec 17 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.2-1
- Update to 1.48.2

* Mon Nov 21 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.1-4
- More-correct .pc file path fix
- When passing paths to the build system, they are now correctly relative
  to the prefix rather than absolute.

* Wed Nov 16 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.1-3
- Fix wrong paths in .pc files

* Sat Sep 17 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.1-2
- Update test skips for 1.48.1

* Thu Sep 08 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.1-1
- Update to grpc 1.48.1 (close RHBZ#2123215)

* Fri Aug 19 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.0-2
- Update to grpc 1.48.0 (close RHBZ#2100262)

* Fri Aug 19 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.48.0-1
- Update to grpc 1.48.0 (bootstrap build)

* Sun Aug 14 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.47.1-1
- Update to 1.47.1

* Sat Aug 13 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.3-10
- Update License fields to SPDX

* Thu Aug 04 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.3-9
- Add dependency on grpc-plugins from grpc-devel

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.46.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Jun 20 2022 Python Maint <python-maint@redhat.com> - 1.46.3-7
- Rebuilt for Python 3.11

* Wed Jun 15 2022 Python Maint <python-maint@redhat.com> - 1.46.3-6
- Bootstrap for Python 3.11

* Fri Jun 10 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.3-5
- Work around ChannelzServicerTest Python 3.11 regressions for now
- Skips five failing tests. Closes RHBZ#2095027.

* Fri Jun 10 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.3-4
- Fix deprecated “inspect.getargspec”

* Fri May 27 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.3-3
- Use new upstream PR#25635 as .pc path fix

* Sat May 21 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.3-2
- Add exact-version dependency on grpc-cpp from grpc-cli

* Sat May 21 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.3-1
- Update to 1.46.3 (close RHBZ#2088859)

* Tue May 17 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.2-1
- Update to 1.46.2 (close RHBZ#2087019)

* Tue May 17 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.1-2
- Trivial typo fixes in spec file comments

* Sun May 15 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.46.1-1
- Update to 1.46.1 (close RHBZ#2024386)
- No longer depends on wyhash, as the core of the algorithm has been
  rewritten and included in the primary sources

* Mon May 02 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-21
- F37+: Stop tracking test failures on 32-bit arches

* Thu Mar 31 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-20
- Improve grpc-1.40.0-python-grpcio-use-system-abseil.patch

* Wed Mar 30 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-19
- Add exactly-versioned grpc-cpp subpackage dependencies

* Wed Mar 30 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-18
- Add virtual Provides for bundled upb to binary packages

* Mon Mar 28 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-17
- Skip client_ssl_test, which is prone to occasional timeouts

* Mon Mar 28 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-16
- Drop the NodeJS example’s package-lock.json file

* Wed Mar 09 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-15
- Rebuild for abseil-cpp 20211102.0 (non-bootstrap)

* Tue Mar 08 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-14
- Rebuild for abseil-cpp 20211102.0 (bootstrap)

* Tue Mar 08 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-13
- Rebuild for abseil-cpp 20211102.0

* Sat Feb 05 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-12
- Drop Conflicts with libgpr (fix RHBZ#2017576)

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 1.41.1-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Sun Jan 16 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-10
- Add link to PR for GCC 12 fix

* Sun Jan 16 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-9
- Fix build on GCC 12

* Thu Jan 13 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-8
- Non-bootstrap rebuild

* Wed Jan 12 2022 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-7
- Bootstrap after libre2.so.9 bump (fix RHBZ#2038546)

* Sat Jan 08 2022 Miro Hrončok <miro@hroncok.cz> - 1.41.1-6
- Rebuilt for libre2.so.9

* Tue Dec 14 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-5
- Dep. on cmake-filesystem is now auto-generated

* Fri Nov 05 2021 Adrian Reber <adrian@lisas.de> - 1.41.1-4
- Rebuilt for protobuf 3.19.0

* Tue Oct 26 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-3
- Add explicit Conflicts with libgpr for now (RHBZ#2017576)

* Tue Oct 26 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-2
- Fix mixed spaces and tabs in spec file

* Tue Oct 26 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.1-1
- Update to 1.41.1 (close RHBZ#20172232)

* Tue Oct 26 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.0-4
- Reduce macro indirection in the spec file

* Mon Oct 25 2021 Adrian Reber <adrian@lisas.de> - 1.41.0-3
- Rebuilt for protobuf 3.18.1

* Tue Oct 12 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.0-2
- Update failing/skipped tests

* Wed Oct 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.41.0-1
- Update to 1.41.0

* Thu Sep 30 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.40.0-3
- Add missing python3-grpcio+protobuf extras metapackage

* Tue Sep 28 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.40.0-2
- Drop HTML documentation

* Fri Sep 17 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.40.0-1
- Update to 1.40.0 (close RHBZ#2002019)

* Wed Sep 15 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-10
- Trivial fix to grpc_cli-call man page

* Tue Sep 14 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-9
- Adapt to google-benchmark 1.6.0

* Tue Sep 14 2021 Sahana Prasad <sahana@redhat.com> - 1.39.1-8
- Rebuilt with OpenSSL 3.0.0

* Mon Aug 23 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-7
- Update some spec file comments

* Fri Aug 20 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-6
- Remove arguably-excessive use of the %%%%{name} macro

* Fri Aug 20 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-5
- No files need CRNL line ending fixes anymore

* Fri Aug 20 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-4
- Spiff up shebang-fixing snippet

* Fri Aug 20 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-3
- Remove executable permissions from more non-script sources, and send a PR
  upstream

* Fri Aug 20 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-2
- Some minor spec file cleanup

* Thu Aug 19 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.1-1
- Update to grpc 1.39.1 (close RHBZ#1993554)

* Thu Aug 19 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.0-3
- More updates to documented/skipped test failures

* Fri Aug 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.0-2
- Some updates to documented/skipped test failures

* Tue Aug 03 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.39.0-1
- Update to 1.39.0

* Wed Jul 21 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.37.1-10
- Simplify core test exclusion (no more useless use of cat)

* Fri Jul  9 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.37.1-8
- Use googletest 1.11.0

* Mon Jun 14 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.37.1-7
- Add BR on xxhash-static since we use it as a header-only library

* Thu Jun 10 2021 Rich Mattes <richmattes@gmail.com> - 1.37.1-6
- Rebuild for abseil-cpp-20210324.2

* Thu Jun 10 2021 Stephen Gallagher <sgallagh@redhat.com> - 1.37.1-5
- Fix builds against Python 3.10 on ELN/RHEL as well

* Thu Jun 10 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.37.1-4
- Since it turns out xxhash is used as a header-only library, we can stop
  patching the source to unbundle it; removing the bundled copy suffices

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 1.37.1-3
- Rebuilt for Python 3.10

* Fri May 21 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.37.1-2
- Use full gRPC_{CPP,CSHARP}_SOVERSION in file globs

* Tue May 11 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.37.1-1
- General:
  * New version 1.37.1
  * Drop patches that were upstreamed since the last packaged release, were
    backported from upstream in the first place, or have otherwise been
    obsoleted by upstream changes.
  * Rebase/update remaining patches as needed
  * Drop Fedora 32 compatibility
  * Add man pages for grpc_cli
- C (core) and C++ (cpp):
  * Switch to CMake build system
  * Build with C++17 for compatibility with the abseil-cpp package in Fedora
  * Add various Requires to -devel subpackage

* Tue Apr 06 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.26.0-15
- General:
  * Do not use %%exclude for unpackaged files (RPM 4.17 compatibility)
- Python:
  * Stop using %%pyproject_buildrequires, since it is difficult to fit the
    pyproject-rpm-macros build and install macros into this package, and Miro
    Hrončok has advised that “mixing %%pyproject_buildrequires with
    %%py3_build/%%py3_install is generally not a supported way of building
    Python packages.”

* Thu Mar 25 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.26.0-14
- General:
  * Improved googletest source URL (better tarball name)

* Tue Mar 23 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.26.0-13
- General:
  * Replace * with • in descriptions
  * Use cmake() dependencies first, and pkgconfig() dependencies second, where
    available
  * Drop explicit pkgconfig BR
  * Fix the directory in which CMake installs pkgconfig files
  * Improved CMake options
  * Build the Doxygen reference manuals
- C (core) and C++ (cpp):
  * Let the -devel package require cmake-filesystem
  * Allow building tests with our own copy of gtest/gmock, which will become
    mandatory when we depend on abseil-cpp and switch to C++17
  * Fix a link error in the core tests when using CMake
  * Manually install grpc_cli (CMake)
  * Add CMake files to the files list for the -devel package
  * Start running some of the core tests in %%check
- Python:
  * Add several patches required for the tests
  * BR gevent for gevent_tests
  * Fix build; in particular, add missing preprocess and build_package_protos
    steps, without which the packages were missing generated proto modules and
    were not
    usable!
  * Add %%py_provides for Fedora 32
  * Drop python3dist(setuptools) BR, redundant with %%pyproject_buildrequires
  * Start running most of the Python tests in %%check
  * Merge the python-grpcio-doc subpackage into grpc-doc

* Tue Feb 16 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.26.0-12
- C (core) and C++ (cpp):
  * Add CMake build support but do not enable it yet; there is still a problem
    where grpc_cli is only built with the tests, and a linking problem when
    building the tests

* Tue Feb 02 2021 Benjamin A. Beasley <code@musicinmybrain.net> - 1.26.0-11
- General:
  * Update summaries and descriptions
  * Update License fields to include licenses from bundled components
  * Fix failure to respect Fedora build flags
  * Use the system shared certificate bundle instead of shipping our own
- CLI:
  * No longer set rpath $ORIGIN
- C (core) and C++ (cpp):
  * Add c_so_version/cpp_so_version macros
  * Split out C++ bindings and shared data into subpackages
  * Drop obsolete ldconfig_scriptlets macro
  * Stop stripping debugging symbols
- Python:
  * Use generated BR’s
  * Build and package Python binding documentation
  * Disable accommodations for older libc’s
  * Patch out -std=gnu99 flag, which is inappropriate for C++
  * Build additional Python packages grpcio_tools, gprcio_channelz,
    grpcio_health_checking, grpcio_reflection, grpcio_status, and
    grpcio_testing

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.26.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Jan 14 08:46:34 CET 2021 Adrian Reber <adrian@lisas.de> - 1.26.0-9
- Rebuilt for protobuf 3.14

* Fri Nov 13 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 1.26.0-8
- build: disable LTO due to rh#1893533

* Thu Sep 24 2020 Adrian Reber <adrian@lisas.de> - 1.26.0-7
- Rebuilt for protobuf 3.13

* Mon Aug 03 2020 Gwyn Ciesla <gwync@protonmail.com> - 1.26.0-6
- Patches for https://github.com/grpc/grpc/pull/21669

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.26.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun Jun 14 2020 Adrian Reber <adrian@lisas.de> - 1.26.0-4
- Rebuilt for protobuf 3.12

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 1.26.0-3
- Rebuilt for Python 3.9

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.26.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jan 15 2020 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.26.0-1
- Update to 1.26.0

* Thu Dec 19 2019 Orion Poplawski <orion@nwra.com> - 1.20.1-5
- Rebuild for protobuf 3.11

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 1.20.1-4
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 1.20.1-3
- Rebuilt for Python 3.8

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.20.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Fri May 17 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.20.1-1
- Update to 1.20.1

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.18.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Jan 16 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.18.0-1
- Update to 1.18.0

* Mon Dec 17 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.17.1-3
- Properly store patch in SRPM

* Mon Dec 17 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.17.1-2
- Build without ruby plugin for Fedora < 30 (Thanks to Mathieu Bridon)

* Fri Dec 14 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.17.1-1
- Update to 1.17.1 and package python bindings

* Fri Dec 07 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.17.0-1
- Initial revision

