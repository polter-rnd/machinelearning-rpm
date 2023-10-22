Name:           opt_einsum
Summary:        Optimizing einsum functions
BuildArch:      noarch
Version:        3.3.0
Release:        5%{?dist}
License:        MIT

URL:            https://github.com/dgasmith/opt_einsum

Source0:        https://github.com/dgasmith/opt_einsum/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  python3-devel python3-setuptools

%description
Optimizing einsum functions in NumPy, Tensorflow, Dask, and more with contraction order optimization.

%package -n     python3-%{name}
Summary:        Development files for python

%description -n python3-%{name}
This package contains the python libraries.


%prep
%setup -q -n %{name}-%{version}


%build
sed -i '/versioneer/d' setup.py
echo "[metadata]" >> setup.cfg
echo "  version = %{version}" >> setup.cfg
%py3_build

%install
%py3_install


%files -n python3-%{name}
%doc README.md
%{python3_sitelib}/*


%changelog
* Wed Dec 04 2019 Balint Cristian <cristian.balint@gmail.com>
- initial build
