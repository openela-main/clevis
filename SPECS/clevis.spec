%global _hardened_build 1

Name:           clevis
Version:        15
Release:        15%{?dist}
Summary:        Automated decryption framework

License:        GPLv3+
URL:            https://github.com/latchset/%{name}
Source0:        https://github.com/latchset/%{name}/releases/download/v%{version}/%{name}-%{version}.tar.xz

Patch0001: 0001-Fixes-for-dealing-with-newer-tang-without-tangd-upda.patch
Patch0002: 0002-Add-the-option-to-extract-luks-passphrase-used-for-b.patch
Patch0003: 0003-systemd-account-for-unlocking-failures-in-clevis-luk.patch
Patch0004: 0004-systemd-drop-ncat-dependency.patch
Patch0005: 0005-Stop-sending-stderr-to-the-void-when-decryption-does.patch
Patch0006: 0006-luks-enable-debugging-in-clevis-scripts-when-rd.debu.patch
Patch0007: 0007-luks-explicitly-specify-pbkdf-iterations-to-cryptset.patch
Patch0008: 0008-tang-dump-url-on-error-communication.patch
Patch0009: 0009-feat-rename-the-test-pin-to-null-pin.patch
Patch0010: 0010-avoid-clevis-invalid-msg.patch
Patch0011: 0011-Improve-boot-performance-by-removing-key-check.patch
Patch0012: 0012-ignore-empty-and-comment-lines-in-crypttab.patch
Patch0013: 0013-luks-define-max-entropy-bits-for-pwmake.patch
Patch0014: 0014-luks-edit-remove-unnecessary-redirection.patch
Patch0015: 0015-support-sha256-algorithm.patch

BuildRequires:  git
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  asciidoc
BuildRequires:  ninja-build
BuildRequires:  bash-completion

BuildRequires:  libjose-devel >= 8
BuildRequires:  libluksmeta-devel >= 8
BuildRequires:  audit-libs-devel
BuildRequires:  libudisks2-devel
BuildRequires:  openssl-devel

BuildRequires:  tpm2-tools >= 3.0.0
BuildRequires:  desktop-file-utils
BuildRequires:  pkgconfig
BuildRequires:  systemd
BuildRequires:  dracut
BuildRequires:  tang >= 6
BuildRequires:  curl
BuildRequires:  luksmeta
BuildRequires:  cracklib-dicts
BuildRequires:  jq
BuildRequires:  diffutils
BuildRequires:  expect
BuildRequires:  openssl

Requires:       cracklib-dicts
Requires:       tpm2-tools >= 3.0.0
Requires:       coreutils
Requires:       jose >= 8
Requires:       curl
Requires:       jq
Requires(pre):  shadow-utils
Requires(post): systemd

%description
Clevis is a framework for automated decryption. It allows you to encrypt
data using sophisticated unlocking policies which enable decryption to
occur automatically.

The clevis package provides basic encryption/decryption policy support.
Users can use this directly; but most commonly, it will be used as a
building block for other packages. For example, see the clevis-luks
and clevis-dracut packages for automatic root volume unlocking of LUKS
volumes during early boot.

%package luks
Summary:        LUKS integration for clevis
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cryptsetup
Requires:       luksmeta >= 8

%description luks
LUKS integration for clevis. This package allows you to bind a LUKS
volume to a clevis unlocking policy. For automated unlocking, an unlocker
will also be required. See, for example, clevis-dracut and clevis-udisks2.

%package systemd
Summary:        systemd integration for clevis
Requires:       %{name}-luks%{?_isa} = %{version}-%{release}
%if 0%{?fedora} > 27
Requires:       systemd%{?_isa} >= 235-3
%else
%if 0%{?fedora} == 27
Requires:       systemd%{?_isa} >= 234-9
%else
%if 0%{?fedora} == 26
Requires:       systemd%{?_isa} >= 233-7
%else
Requires:       systemd%{?_isa} >= 236
%endif
%endif
%endif

%description systemd
Automatically unlocks clevis-bound LUKS block devices during boot.

%package dracut
Summary:        Dracut integration for clevis
Requires:       %{name}-systemd%{?_isa} = %{version}-%{release}
Requires:       dracut-network

%description dracut
Automatically unlocks LUKS block devices in early boot.

%package udisks2
Summary:        UDisks2/Storaged integration for clevis
Requires:       %{name}-luks%{?_isa} = %{version}-%{release}

%description udisks2
Automatically unlocks LUKS block devices in desktop environments that
use UDisks2 or storaged (like GNOME).

%prep
%autosetup -S git

%build
%meson -Duser=clevis -Dgroup=clevis
%meson_build

%install
%meson_install

%check
desktop-file-validate \
  %{buildroot}/%{_sysconfdir}/xdg/autostart/%{name}-luks-udisks2.desktop
%meson_test

%pre
getent group %{name} >/dev/null || groupadd -r %{name} &>/dev/null
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_localstatedir}/cache/%{name} -s /sbin/nologin \
    -c "Clevis Decryption Framework unprivileged user" %{name} &>/dev/null
# Add clevis user to tss group.
if getent group tss >/dev/null && ! groups %{name} | grep -q "\btss\b"; then
    usermod -a -G tss %{name} &>/dev/null
fi
exit 0

%post systemd
systemctl preset %{name}-luks-askpass.path >/dev/null 2>&1 || :

%files
%license COPYING
%{_datadir}/bash-completion/
%{_bindir}/%{name}-decrypt-tang
%{_bindir}/%{name}-decrypt-tpm2
%{_bindir}/%{name}-decrypt-sss
%{_bindir}/%{name}-decrypt-null
%{_bindir}/%{name}-decrypt
%{_bindir}/%{name}-encrypt-tang
%{_bindir}/%{name}-encrypt-tpm2
%{_bindir}/%{name}-encrypt-sss
%{_bindir}/%{name}-encrypt-null
%{_bindir}/%{name}
%{_mandir}/man1/%{name}-encrypt-tang.1*
%{_mandir}/man1/%{name}-encrypt-tpm2.1*
%{_mandir}/man1/%{name}-encrypt-sss.1*
%{_mandir}/man1/%{name}-decrypt.1*
%{_mandir}/man1/%{name}.1*

%files luks
%{_mandir}/man7/%{name}-luks-unlockers.7*
%{_mandir}/man1/%{name}-luks-unlock.1*
%{_mandir}/man1/%{name}-luks-unbind.1*
%{_mandir}/man1/%{name}-luks-bind.1*
%{_mandir}/man1/%{name}-luks-list.1*
%{_mandir}/man1/%{name}-luks-pass.1*
%{_mandir}/man1/%{name}-luks-regen.1*
%{_mandir}/man1/%{name}-luks-report.1*
%{_mandir}/man1/%{name}-luks-edit.1*
%{_bindir}/%{name}-luks-unlock
%{_bindir}/%{name}-luks-unbind
%{_bindir}/%{name}-luks-bind
%{_bindir}/%{name}-luks-common-functions
%{_bindir}/%{name}-luks-list
%{_bindir}/%{name}-luks-pass
%{_bindir}/%{name}-luks-regen
%{_bindir}/%{name}-luks-report
%{_bindir}/%{name}-luks-edit

%files systemd
%{_libexecdir}/%{name}-luks-askpass
%{_unitdir}/%{name}-luks-askpass.path
%{_unitdir}/%{name}-luks-askpass.service

%files dracut
%{_prefix}/lib/dracut/modules.d/60%{name}
%{_prefix}/lib/dracut/modules.d/60%{name}-pin-null
%{_prefix}/lib/dracut/modules.d/60%{name}-pin-sss
%{_prefix}/lib/dracut/modules.d/60%{name}-pin-tang
%{_prefix}/lib/dracut/modules.d/60%{name}-pin-tpm2

%files udisks2
%{_sysconfdir}/xdg/autostart/%{name}-luks-udisks2.desktop
%attr(4755, root, root) %{_libexecdir}/%{name}-luks-udisks2

%changelog
* Tue May 23 2023 Sergio Arroutbi <sarroutb@redhat.com> - 15-15
- Include SHA-256 thumbprints clevis support
  Resolves: rhbz#2209058

* Mon Jan 16 2023 Sergio Arroutbi <sarroutb@redhat.com> - 15-14
- luks-edit: remove unnecessary 2>/dev/null
  Resolves: rhbz#2159739

* Wed Jan 11 2023 Sergio Arroutbi <sarroutb@redhat.com> - 15-13
- luks: define max entropy bits for pwmake
  Resolves: rhbz#2159736

* Wed Jan 11 2023 Sergio Arroutbi <sarroutb@redhat.com> - 15-12
- Ignore empty & comment lines in crypttab
  Resolves: rhbz#2159440

* Tue Aug 02 2022 Sergio Arroutbi <sarroutb@redhat.com> - 15-11
- Start clevis-luks-askpass.path service according to global policy
  Resolves: rhbz#2107081

* Thu Jul 21 2022 Sergio Arroutbi <sarroutb@redhat.com> - 15-10
- Improve boot performance by removing key check
  Resolves: rhbz#2099748

* Wed Jun 22 2022 Sergio Arroutbi <sarroutb@redhat.com> - 15-9
- Avoid invalid message for clevis command
  Resolves: rhbz#2099325

* Wed Jan 26 2022 Sergio Correia <scorreia@redhat.com> - 15-8
- Support a null pin
  Resolves: rhbz#2028096

* Fri Jan 21 2022 Sergio Arroutbi <sarroutb@redhat.com> - 15-7
- Dump server information on server error communication
  Resolves: rhbz#2020193

* Tue Jan 04 2022 Sergio Correia <scorreia@redhat.com> - 15-6
- Explicitly specify pbkdf iterations to cryptsetup
  Resolves: rhbz#1979256

* Wed Dec 01 2021 Sergio Correia <scorreia@redhat.com> - 15-5
- Enable debugging in clevis scripts when rd.debug is set
  Resolves: rhbz#1980742

* Thu Nov 25 2021 Sergio Correia <scorreia@redhat.com> - 15-4
- Stop sending stderr to the void when decryption doesn't happen
  Resolves: rhbz#1976880

* Thu Nov 18 2021 Sergio Correia <scorreia@redhat.com> - 15-3
- Drop ncat dependency
  Resolves: rhbz#1949289

* Wed Nov 17 2021 Sergio Correia <scorreia@redhat.com> - 15-2
- Account for unlocking failures in clevis-luks-askpass
  Resolves: rhbz#2018292

* Mon Oct 26 2020 Sergio Correia <scorreia@redhat.com> - 15-1
- Update to latest upstream release, v15
  Resolves: rhbz#1887836
  Resolves: rhbz#1853651
  Resolves: rhbz#1874460

* Wed May 20 2020 Sergio Correia <scorreia@redhat.com> - 13-3
- Add clevis luks edit command
  Resolves: rhbz#1436735

* Mon May 18 2020 Sergio Correia <scorreia@redhat.com> - 13-2
- Introduce -y (assume yes) argument to clevis luks bind
  Resolves: rhbz#1819767

* Sun May 10 2020 Sergio Correia <scorreia@redhat.com> - 13-1
- Update to new upstream release, v13
  Resolves: rhbz#1827225
  Resolves: rhbz#1827665
  Resolves: rhbz#1801556
  Resolves: rhbz#1784448
  Resolves: rhbz#1826917
  Resolves: rhbz#1812014

* Sun Feb 02 2020 Sergio Correia <scorreia@redhat.com> - 11-9
- Improve clevis luks regen not to unbind+bind in every case
  Resolves: rhbz#1795675

* Mon Jan 13 2020 Sergio Correia <scorreia@redhat.com> - 11-8
- Use one clevis-luks-askpass per device
  Resolves: rhbz#1784524

* Sat Nov 30 2019 Sergio Correia <scorreia@redhat.com> - 11-7
- Add rd.neednet=1 to cmdline only if there are devices bound to tang
  Resolves: rhbz#1762028

* Sat Nov 30 2019 Sergio Correia <scorreia@redhat.com> - 11-6
- Add option to extract luks passphrase used for binding
  Resolves: rhbz#1436780

* Thu Nov 28 2019 Sergio Correia <scorreia@redhat.com> - 11-5
- Add support for listing existing PBD policies in place
  Resolves: rhbz#1766526

* Fri Oct 18 2019 Sergio Correia <scorreia@redhat.com> - 11-4
- Improve error message when bind is given an invalid PIN
  Resolves: rhbz#1543380

* Wed Oct 16 2019 Sergio Correia <scorreia@redhat.com> - 11-3
- Add clevis luks report and regen
  Resolves: rhbz#1564566
  Resolves: rhbz#1564559

* Fri Jan 04 2019 Daniel Kopecek <dkopecek@redhat.com> - 11-2
- Check that key derivation key is available
- Delete remaining references to the removed http pin
- Install cryptsetup and tpm2_pcrlist in the initramfs
- Add device TCTI library to the initramfs
  Resolves: rhbz#1648004
  Resolves: rhbz#1650246

* Tue Aug 14 2018 Nathaniel McCallum <npmccallum@redhat.com> - 11-1
- Update to v11

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Mar 21 2018 Nathaniel McCallum <npmccallum@redhat.com> - 10-1
- Update to v10

* Tue Feb 13 2018 Nathaniel McCallum <npmccallum@redhat.com> - 9-1
- Update to v9

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Nov 13 2017 Nathaniel McCallum <npmccallum@redhat.com> - 8-1
- Update to v8

* Wed Nov 08 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 7-2
- Rebuild for cryptsetup-2.0.0

* Fri Oct 27 2017 Nathaniel McCallum <npmccallum@redhat.com> - 7-1
- Update to v7

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 6-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jun 27 2017 Nathaniel McCallum <npmccallum@redhat.com> - 6-1
- New upstream release
- Specify unprivileged user/group during configuration
- Move clevis user/group creation to base clevis package

* Mon Jun 26 2017 Nathaniel McCallum <npmccallum@redhat.com> - 5-1
- New upstream release
- Run clevis decryption from udisks2 under an unprivileged user

* Wed Jun 14 2017 Nathaniel McCallum <npmccallum@redhat.com> - 4-1
- New upstream release

* Wed Jun 14 2017 Nathaniel McCallum <npmccallum@redhat.com> - 3-1
- New upstream release

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Nov 18 2016 Nathaniel McCallum <npmccallum@redhat.com> - 2-1
- New upstream release

* Mon Nov 14 2016 Nathaniel McCallum <npmccallum@redhat.com> - 1-1
- First release
