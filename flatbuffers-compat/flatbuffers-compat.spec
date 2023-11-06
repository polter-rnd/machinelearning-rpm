%bcond_with tests

Name:           flatbuffers-compat
Version:        23.3.3
Release:        1%{?dist}
Summary:        Memory efficient serialization library
URL:            http://google.github.io/flatbuffers

# The entire source code is ASL 2.0 except grpc/ which is BSD (3 clause)
License:        ASL 2.0 and BSD

Source0:        https://github.com/google/flatbuffers/archive/v%{version}/flatbuffers-%{version}.tar.gz
Source1:        flatc.1

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 2.8.9
BuildRequires:  git-core
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires: make

# The library contains pieces of gRPC project, with some additions.
# It is not easy to identify the version, which was used to take the code,
# but it should be something after version 1.3.2. See this discussion for
# details: https://github.com/google/flatbuffers/pull/4305
Provides:       bundled(grpc)

%global common_description %{expand:
FlatBuffers is a cross platform serialization library architected for maximum
memory efficiency. It allows you to directly access serialized data without
parsing/unpacking it first, while still having great forwards/backwards
compatibility.}

%description %{common_description}


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel %{common_description}

This package contains libraries and header files for developing applications
that use FlatBuffers.


%package        compiler
Summary:        FlatBuffers compiler (flatc)
# The flatc compiler does not link against the shared library, so this could
# possibly be removed; we leave it for now to ensure there is no version skew
# across subpackages.
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    compiler %{common_description}

This package contains flatc, the FlatBuffers compiler.


%package        doc
Summary:        Documentation and examples for FlatBuffers

BuildArch:      noarch


%description    doc %{common_description}

This package contains documentation and examples for FlatBuffers.


%package        python3
Summary:        FlatBuffers serialization format for Python

BuildArch:      noarch

Recommends:     python3dist(numpy)

Provides:       %{name}-python3 = %{version}-%{release}

%description    python3 %{common_description}

This package contains the Python runtime library for use with the Flatbuffers
serialization format.


%prep
%autosetup -n flatbuffers-%{version} -S git_am
# cleanup distribution
rm -rf js net php docs go java js biicode {samples/,}android kotlin/
chmod -x readme.md

%cmake -DCMAKE_BUILD_TYPE=Release \
       -DFLATBUFFERS_BUILD_SHAREDLIB=ON \
       -DFLATBUFFERS_BUILD_FLATLIB=OFF \
       -DFLATBUFFERS_BUILD_FLATC=ON \
       -DFLATBUFFERS_BUILD_TESTS=%{?with_tests:ON}%{!?with_tests:OFF} \
       .

%build
%cmake_build

pushd python
%{__python3} setup.py build
popd

%install
%cmake_install
pushd python
%{__python3} setup.py install --root %{buildroot}
popd
mkdir -p %{buildroot}%{_mandir}/man1
cp -p %SOURCE1 %{buildroot}%{_mandir}/man1/flatc.1


%check
%if %{with tests}
make test
%endif

%ldconfig_scriptlets

%files
%license LICENSE

%{_libdir}/libflatbuffers.so.{%version}

%files devel
%{_includedir}/flatbuffers/

%{_libdir}/libflatbuffers.so

%{_libdir}/cmake/flatbuffers/
%{_libdir}/pkgconfig/flatbuffers.pc


%files compiler
%{_bindir}/flatc
%{_mandir}/man1/flatc.1*


%files doc
%license LICENSE
%doc CHANGELOG.md
%doc SECURITY.md
%doc readme.md

%files python3
%{python3_sitelib}/*

%changelog
* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 2.0.0-2
- Rebuilt for Python 3.10

* Mon May 17 2021 Benjamin Lowry <ben@ben.gmbh - 2.0.0-1
- flatbuffers 2.0.0

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Aug 10 2020 Cristian Balint <cristian.balint@gmail.com> - 1.12.0-5
- Enable python module

* Sat Aug 01 2020 Benjamin lowry <ben@ben.gmbh> - 1.12.0-4
- Update to new cmake macros, fix build error

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.12.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue May 12 2020 Benjamin Lowry <ben@ben.gmbh> - 1.12.0-1
- Upgrade to 1.12.0, fix compilation on F32

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.11.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed May 15 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.11.0-1
- Update to 1.11.0

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 21 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.10.0-3
- Add explicit curdir on CMake invocation

* Thu Jan 10 2019 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.10.0-2
- Fix generator (and generated tests) for gcc9 (ignore -Wclass-memaccess)

* Thu Oct 04 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.10.0-1
- Update to 1.10.0

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.9.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Apr 06 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.9.0-1
- Update to 1.9.0

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.8.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.8.0-3
- Fix build errors.

* Wed Nov 22 2017 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.8.0-2
- Update manpages for 1.8.0

* Wed Nov 22 2017 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.8.0-1
- Update to 1.8.0

* Thu Nov 2 2017 Sergey Avseyev <sergey.avseyev@gmail.com> - 1.7.1-1
- Initial version

* Mon Mar 30 2015 Daniel Vrátil <dvratil@redhat.com> - 1.0.3-1
- Initial version (abandoned at #1207208)
