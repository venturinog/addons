%define modname addons

Summary: Issabel Addons
Name: issabel-addons
Version: 6.0.0
Release: 18
License: GPL
Group:   Applications/System
Source0: issabel-%{modname}-%{version}.tar.gz
#Patch0:  repo-40.patch
BuildRoot: %{_tmppath}/%{name}-%{version}-root
BuildArch: noarch
Requires(pre): issabel-framework >= 5.0.0-1
Requires: php-cli, php-soap
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
# El demonio se instala como servicio de systemd. El script de init que
# usaba el paquete no arrancaba en EL10: depende de
# /etc/rc.d/init.d/functions y del binario 'daemon', y ninguno de los dos
# existe en Rocky 10, de modo que salia con codigo 0 sin hacer nada.
mkdir -p $RPM_BUILD_ROOT/etc/systemd/system/
mv setup/etc/systemd/system/issabel-updaterd.service $RPM_BUILD_ROOT/etc/systemd/system/
chmod 0644 $RPM_BUILD_ROOT/etc/systemd/system/issabel-updaterd.service
mkdir -p $RPM_BUILD_ROOT/etc/yum.repos.d/

## Add the GNU Privacy Guard for the Postgresql91 repo
mkdir -p $RPM_BUILD_ROOT/etc/pki/
mv setup/etc/pki/rpm-gpg/ $RPM_BUILD_ROOT/etc/pki/
rmdir setup/etc/pki
rmdir setup/etc/systemd/system
rmdir setup/etc/systemd

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
fi

# The installer script expects to be in /tmp/new_module
mkdir -p /tmp/new_module/%{modname}
cp -r /usr/share/issabel/module_installer/%{name}-%{version}-%{release}/* /tmp/new_module/%{modname}/
chown -R asterisk.asterisk /tmp/new_module/%{modname}

php /tmp/new_module/%{modname}/setup/installer.php
rm -rf /tmp/new_module

# Install issabel-updaterd as a systemd service. El demonio es el que abre el
# socket tcp://localhost:20004 por donde la GUI instala y desinstala los
# addons: si no corre, el boton de instalar no hace nada.
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable issabel-updaterd
/usr/bin/systemctl restart issabel-updaterd

%clean
rm -rf $RPM_BUILD_ROOT

%preun
pathModule="/usr/share/issabel/module_installer/%{name}-%{version}-%{release}"
if [ $1 -eq 0 ] ; then # Validation for desinstall this rpm
  echo "Delete Addons menus"
  issabel-menuremove "%{modname}"

  echo "Dump and delete %{name} databases"
  issabel-dbprocess "delete" "$pathModule/setup/db"

  echo "Stop the update daemon"
  /usr/bin/systemctl disable --now issabel-updaterd
fi

%files
%defattr(-, root, root)
%{_localstatedir}/www/html/*
/usr/share/issabel/module_installer/*
/etc/systemd/system/issabel-updaterd.service
/opt/issabel/issabel-updater
/etc/pki/rpm-gpg/*
/etc/yum.repos.d/*

%changelog
* Thu Oct 22 2026 Issabel Foundation <info@issabel.org> - 6.0.0-18
- Open the cloud login popup at its designed size. The popup of the
  unregistered branch asked for 540x335, a legacy height 70 pixels below
  the one the registration form is built for (the menu register link and
  the signup button already use 540x405), so the bottom of the form fell
  out of the box. The framework popup container now scrolls as a safety
  net as well.

* Thu Oct 22 2026 Issabel Foundation <info@issabel.org> - 6.0.0-17
- Warn instead of going silent when the cloud login popup cannot open.
  For an unregistered server the install button ends in showPopupCloudLogin(),
  whose markup (neo-modal-issabel-popup-* nodes) belongs to the page shell of
  the framework. Page templates that do not carry that markup made the click
  a silent no-op: the AJAX round trip ran, but nothing appeared. The module
  now shows a theme alert asking to register the server when the popup nodes
  are missing, in every supported language.

* Thu Oct 22 2026 Issabel Foundation <info@issabel.org> - 6.0.0-16
- Point the unit file at /run for the daemon PID. /var/run is a symlink to
  /run in EL10 and systemd warned about the legacy path on every start.
- Fall back to an empty value for the page script variables. The template
  and the PHP that assigns it travel together in the package, but partial
  manual deployments have been seen with the template newer than the PHP:
  the script then parsed an empty assignment, the whole block was dropped
  and every action of the page, including the install button, became a
  no-op. With the fallback the script parses and the page keeps working.
- Ask uname and /etc/os-release for the yum cachedir markers. The daemon
  ran a Python 2 snippet with the yum module to figure out basearch and
  releasever for the cachedir line, and neither the interpreter nor the
  module exist in EL10, so every start logged a command not found and the
  markers stayed unset.
- Expect the PHP 8 error handler signature in the daemon. PHP 8 no longer
  passes the error context as the fifth argument, so any warning raised
  while the daemon ran, as the one of a closed socket on shutdown, died
  with an argument count error instead of reaching the log.
- Keep the daemon stop from crashing. The error handler referenced the
  deprecated E_STRICT constant and did not know the deprecation levels of
  PHP 8, and its messages were still handed to a log already closed,
  which died with a write to a NULL resource and left the unit as
  failed. The map knows both levels, the strict check uses the number,
  and the logger drops late messages instead of writing to a closed
  file.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-15
- Accept the names of the addons that have more than one group. The rule
  allowed a single dash after the first group, so the catalogue entries
  whose name carries a second one, such as issabel-network-agent, were
  rejected and their install button did nothing. Dots, slashes and semicolons
  are still not allowed, so the name can be neither a path nor a command.
- Tell the user why the name was rejected. The notice said the title of the
  alert instead of the reason.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-14
- Do not fail when the update daemon is not running. The writes to the daemon
  did not check that the socket was open, so with the daemon down they died
  with a TypeError of PHP 8 and the request answered with an error page
  instead of JSON. The page then opened the progress dialog with an
  undefined title and left it frozen at zero. The module now answers with
  the reason and the page shows it in the notice of the theme.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-13
- Install the update daemon as a systemd service. The package installed a
  SysV script that does not start on EL10: it needs
  /etc/rc.d/init.d/functions and the 'daemon' binary, and neither of them
  exists in Rocky 10, so the script exited with code 0 without doing
  anything. The daemon was therefore never running, the socket that the
  GUI uses to install the addons was never opened, and the install button
  did nothing. The unit file takes its place and the daemon now starts
  with the system.

* Wed Oct 21 2026 Issabel Foundation <info@issabel.org> - 6.0.0-12
- Tell the user when the addon catalogue has nothing for this version. The
  marketplace publishes one catalogue per version of Issabel, and the notice
  that the page showed was "No addons match your search criteria", which
  blames the search for a catalogue that the server has not published yet.
  The page now says which version was asked for, and keeps the old message
  for the case in which the catalogue has content but the filter does not
  match anything.

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
