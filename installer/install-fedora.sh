#!/usr/bin/env bash
set -euo pipefail

printf '==> IOC-CMS Fedora/RPM installer\n'
sudo dnf install -y python3 podman podman-compose git yt-dlp exiftool jq sqlite firewalld
python3 -m compileall ioc_cms >/dev/null
printf '==> Run the agency wizard next:\n'
printf 'python3 -m ioc_cms configure --agency-name "Agency" --investigator-name "Name" --investigator-email "name@example.org" --jurisdiction "RO/EU" --legal-basis "consent/warrant/policy"\n'
