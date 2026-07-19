#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
USER_BIN="${HOME}/.local/bin"

printf '==> IOC-CMS Fedora/RPM installer\n'
printf '==> Repository root: %s\n' "${REPO_ROOT}"

if command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y python3 python3-tkinter podman podman-compose git yt-dlp exiftool jq sqlite firewalld
else
  printf '!! dnf not found; skipping Fedora package installation.\n' >&2
fi

cd "${REPO_ROOT}"
python3 -m compileall ioc_cms >/dev/null
mkdir -p "${USER_BIN}"
cat > "${USER_BIN}/ioc-cms" <<WRAPPER
#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH="${REPO_ROOT}\${PYTHONPATH:+:\${PYTHONPATH}}"
exec python3 -m ioc_cms "\$@"
WRAPPER
chmod +x "${USER_BIN}/ioc-cms"

printf '==> Installed user launcher: %s/ioc-cms\n' "${USER_BIN}"
printf '==> If needed, add this to PATH: export PATH="$HOME/.local/bin:$PATH"\n'
printf '==> Try: ioc-cms --help\n'
printf '==> Desktop app: ioc-cms gui\n'
printf '==> Configure agency:\n'
printf 'ioc-cms configure --agency-name "Agency" --investigator-name "Name" --investigator-email "name@example.org" --jurisdiction "RO/EU" --legal-basis "consent/warrant/policy"\n'
