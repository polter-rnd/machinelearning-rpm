%global pkgvers 1
%global schash0 5b9fc9ad978757654843f4a8d899715dbea30e88
%global branch0 main
%global source0 https://github.com/jax-ml/ml_dtypes.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           python-ml_dtypes
Version:        0.2.0
Release:        %{pkgvers}.git%{sshort0}%{?dist}
Summary:        NumPy dtype extensions used in machine learning.
License:        Apache 2.0

URL:            https://github.com/jax-ml/ml_dtypes

BuildRequires:  git python3-devel python3-setuptools
BuildRequires:  gcc-c++ python3-numpy python3-pybind11
BuildRequires:  eigen3-devel pybind11-devel

%if 0%{?rhel} == 8
%global debug_package %{nil}
%endif

%global _description %{expand:
A stand-alone implementation of several NumPy dtype extensions used in machine learning.}

%description %_description

%package -n python3-ml_dtypes
Summary:	%{summary}

%description -n python3-ml_dtypes %_description

%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git submodule update --init --depth 1 third_party/eigen
git log --format=fuller
# py3
sed -i 's|setup(|setup(name="ml_dtypes", version="%{version}",|' setup.py


%build
%py3_build


%install
%py3_install
# clean
rm -rf %{buildroot}%{python3_sitearch}/third_party


%files -n python3-ml_dtypes
%license LICENSE
%doc README.md
%{python3_sitearch}/ml_dtypes/
%{python3_sitearch}/ml_dtypes-%{version}-py%{python3_version}.egg-info/


%changelog
* Tue Jun 06 2023 Cristian Balint <cristian.balint@gmail.com>
- github release updates

