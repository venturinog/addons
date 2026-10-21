%define modname addons

Summary: Issabel Addons
Name: issabel-addons
Version: 6.0.0
Release: 11
License: GPL
Group:   Applications/System
Source0: issabel-%{modname}-%{version}.tar.gz
#Patch0:  repo-40.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
Requires(pre): issabel-framework >= 5.0.0-1
Requires(pre): chkconfig, php-soap
Requires: yum
# commands: /usr/bin/uname
Requires: coreutils

# commands: rpm
Requires: rpm

Obsoletes: elastix-addons

%description
Issabel Addons

%prep
%setup -n %{name}-%{version}
#%patch0 -p0

%install
rm -rf $RPM_BUILD_ROOT

# Files provided by all Issabel modules
mkdir -p    $RPM_BUILD_ROOT/var/www/html/
mv modules/ $RPM_BUILD_ROOT/var/www/html/

# Additional (module-specific) files that can be handled by RPM
mkdir -p $RPM_BUILD_ROOT/opt/issabel/
mv setup/issabel-moduleconf $RPM_BUILD_ROOT/opt/issabel/issabel-updater
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
mv $RPM_BUILD_ROOT/opt/issabel/issabel-updater/issabel-updaterd $RPM_BUILD_ROOT/etc/init.d/
chmod +x $RPM_BUILD_ROOT/etc/init.d/issabel-updaterd
mkdir -p $RPM_BUILD_ROOT/etc/yum.repos.d/

## Add the GNU Privacy Guard for the Postgresql91 repo
mkdir -p $RPM_BUILD_ROOT/etc/pki/
mv setup/etc/pki/rpm-gpg/ $RPM_BUILD_ROOT/etc/pki/
rmdir setup/etc/pki

# The following folder should contain all the data that is required by the installer,
# that cannot be handled by RPM.
mkdir -p    $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
mv setup/etc/yum.repos.d/ $RPM_BUILD_ROOT/etc/

rmdir setup/etc
mv setup/   $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
mv menu.xml $RPM_BUILD_ROOT/usr/share/issabel/module_installer/%{name}-%{version}-%{release}/

%pre
mkdir -p /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/
touch /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
if [ $1 -eq 2 ]; then
    rpm -q --queryformat='%%{VERSION}-%%{RELEASE}' %{name} > /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/preversion_%{modname}.info
fi

%post
pathModule="/usr/share/issabel/module_installer/%{name}-%{version}-%{release}"

# Run installer script to fix up ACLs and add module to Issabel menus.
issabel-menumerge /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/menu.xml
pathSQLiteDB="/var/www/db"
mkdir -p $pathSQLiteDB
preversion=`cat $pathModule/preversion_%{modname}.info`
rm -f $pathModule/preversion_%{modname}.info

if [ $1 -eq 1 ]; then #install
  # The installer database
    issabel-dbprocess "install" "$pathModule/setup/db"
elif [ $1 -eq 2 ]; then #update
    # Removing addons_installed modules
    issabel-menuremove "addons_installed"
    issabel-menuremove "addons_avalaibles"
    # Removing addons_installed files
    rm -rf /var/www/html/modules/addons_installed
    issabel-dbprocess "update"  "$pathModule/setup/db" "$preversion"
    # restart daemon
    /usr/bin/systemctl daemon-reload
    /usr/sbin/service issabel-updaterd restart
fi

# The installer script expects to be in /tmp/new_module
mkdir -p /tmp/new_module/%{modname}
cp -r /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/* /tmp/new_module/%{modname}/
chown -R asterisk.asterisk /tmp/new_module/%{modname}

php /tmp/new_module/%{modname}/setup/installer.php
rm -rf /tmp/new_module

# Install issabel-updaterd as a service
chkconfig --add issabel-updaterd
chkconfig --level 2345 issabel-updaterd on

%clean
rm -rf $RPM_BUILD_ROOT

%preun
pathModule="/usr/share/issabel/module_installer/%{name}-%{version}-%{release}"
if [ $1 -eq 0 ] ; then # Validation for desinstall this rpm
  echo "Delete Addons menus"
  issabel-menuremove "%{modname}"

  echo "Dump and delete %{name} databases"
  issabel-dbprocess "delete" "$pathModule/setup/db"
fi

%files
%defattr(-, root, root)
%{_localstatedir}/www/html/*
/usr/share/issabel/module_installer/*
/etc/init.d/issabel-updaterd
/opt/issabel/issabel-updater
/etc/pki/rpm-gpg/*
/etc/yum.repos.d/*

%changelog
* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-11
- Ask the machine type and not the hardware platform to the addon catalogue.
  'uname -i' returns 'unknown' on EL10 x86-64, so the catalogue was filtered
  by a value that no addon could match. The trailing newline that the shell
  adds is removed as well, so the value that travels to the Web Service is
  the architecture and nothing else.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-10
- Translate the addon market into the 25 languages of the framework. The
  module only had English, Spanish, Persian and Ukrainian, so the page was
  shown in English in the other 21 languages. The 21 files were added with
  the same 44 keys, and the 13 messages that the Persian file carried in
  English were translated.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-9
- Bring the addon market onto the theme grid. The page was built with the
  markup of Issabel 5: a header row of its own, the list of addons as a set
  of absolutely positioned divs, the pagination as a row of images and the
  progress dialog as a modal of its own. The filter is now a card of the
  theme, every addon is a card, the actions are buttons with the icons of the
  theme, the pagination is a row of buttons that are disabled when they do
  not lead anywhere, and the progress is shown in the modal of the theme.
- Rewrite the stylesheet of the module with the tokens of the theme. It had
  102 hexadecimal colours and 18 rgba() of its own, and the ones of the
  buttons, the dialog and the progress bar did not survive the dark mode.
- Remove the images that the new design does not use: the arrows of the
  pagination, the backgrounds of the buttons and the dialog, the icons of the
  actions and the image of the search.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-8
- Show the messages of the addon market with the alert family of the theme.
  The page used the jQuery UI classes, which the Modern theme does not define,
  so the notice came out without any style. Each severity of the theme has
  its own icon and title now, and the two browser alerts of the module were
  replaced by the same notice.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-7
- Escape the addon data that comes from the marketplace. The name, version,
  description and notes of every addon are published by the Web Service and
  were interpolated into the page without escaping, so a compromised or
  malicious catalogue could inject markup into the administrator's browser.
- Escape the package names that the Web Service returns before handing them
  to the shell. They were concatenated into an rpm query, so a catalogue
  entry could run an arbitrary command on the server.
- Translate the labels of the addon buttons and give the images of the addon
  list an accessible name. The alternative text of the pagination arrows was
  left empty because the page does not use the grid of the framework.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-6
- Add the language keys the addon market code looks for and were missing from
  the base file: "Invalid addon name" and "The system can not connect to the
  Web Service resource...". The four language files of the module now have
  the same keys, so the messages no longer fall back to the English text.

* Fri Oct 16 2026 Issabel Foundation <info@issabel.org> - 6.0.0-5
- Escape the rpm queryformat used to record the pre-version on upgrade.
  The VERSION and RELEASE macros were expanded at build time, so %pre always
  wrote the new version and issabel-dbprocess skipped every version_sql
  migration. They are now escaped so rpm expands them at run time.

* Fri Oct 09 2026 Issabel Foundation <info@issabel.org> - 6.0.0-3
- Require the unversioned PHP packages (php-*, 8.3 on EL10) instead of the
  versioned php8.4-*, which conflict with the PHP 8.3 in the netinstall base.
