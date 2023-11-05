Name:		python-astor
Version:	0.8.1
Release:	3%{?dist}
Summary:	Read / rewrite / write Python ASTs
		
License:	BSD
URL:		https://github.com/berkerpeksag/astor
Source0:	%{url}/archive/%{version}/%{name}-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python3-devel
BuildRequires:	python3-pytest

%global _description %{expand:
astor is designed to allow easy manipulation of Python source via the AST.}

%description %_description

%package -n python3-astor
Summary:	%{summary}

%description -n python3-astor %_description

%prep
%autosetup -n astor-%{version}
sed -i '/\/usr\/bin\/env.*python/ d' astor/rtrip.py


%build
%py3_build


%install
%py3_install


%files -n python3-astor
%doc README.*
%{python3_sitelib}/*


%changelog
* Sat Jan 22 2022 Vanessa_kris <vanessaigwe1@gmail.com> 0.8.1-3
- minor tweaks

* Sat Jan 22 2022 Vanessa_kris <vanessaigwe1@gmail.com> 0.8.1-2
- initial build

* Sat Jan 22 2022 Vanessa_kris <vanessaigwe1@gmail.com> 0.8.1-1
- initial build
