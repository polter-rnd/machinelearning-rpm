%global pkgvers 3
%global schash0 3e380065d4afc7347aaee8d89325a16b22158438
%global branch0 master
%global source0 https://github.com/keras-team/keras-preprocessing.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           keras-preprocessing
Version:        1.1.2
Release:        %{pkgvers}.git%{sshort0}%{?dist}
Summary:        Keras Applications
License:        MIT
BuildArch:      noarch

URL:            https://github.com/keras-team/keras-preprocessing

BuildRequires:  git python3-devel python3-setuptools

%description
Keras Preprocessing is the data preprocessing and data
augmentation module of the Keras deep learning library.

%package        python3
Summary:        Development files for python
Requires:       pkgconfig

%description    python3
This package contains the python libraries.


%prep
%setup -T -c -n %{name}
find %{_builddir} -name SPECPARTS -exec rm -rf {} +
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git log --format=fuller


%build
%py3_build


%install
%py3_install


%files python3
%license LICENSE
%doc README.md
%{python3_sitelib}/*


%changelog
* Wed Dec 04 2019 Balint Cristian <cristian.balint@gmail.com>
- github update releases
