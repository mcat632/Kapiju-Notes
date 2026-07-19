Name:           ioc-cms
Version:        0.1.0
Release:        1%{?dist}
Summary:        Fedora-first investigation case management system skeleton
License:        MIT
BuildArch:      noarch
Requires:       python3
Requires:       python3-tkinter
Requires:       podman
Requires:       podman-compose
Requires:       yt-dlp
Requires:       exiftool

%description
IOC-CMS is a Fedora/RPM-first case management system skeleton for lawful OSINT,
darknet, malware-triage, and digital-forensics investigations.

%install
mkdir -p %{buildroot}%{_datadir}/ioc-cms
cp -a ioc_cms docs installer %{buildroot}%{_datadir}/ioc-cms/
mkdir -p %{buildroot}%{_datadir}/applications
cp packaging/linux/ioc-cms.desktop %{buildroot}%{_datadir}/applications/ioc-cms.desktop
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/ioc-cms <<'WRAPPER'
#!/usr/bin/env bash
export PYTHONPATH="/usr/share/ioc-cms${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m ioc_cms "$@"
WRAPPER
chmod 0755 %{buildroot}%{_bindir}/ioc-cms

%files
%{_bindir}/ioc-cms
%{_datadir}/ioc-cms
%{_datadir}/applications/ioc-cms.desktop
