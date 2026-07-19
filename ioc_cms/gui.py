"""Modern local web GUI for IOC-CMS using only the Python standard library."""

from __future__ import annotations

import html
import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .cli import AgencyProfile, CASE_DIRECTORIES, CONFIG_FILE, WORKSPACE_TABS, load_profile, save_profile

CSS = """
:root{color-scheme:dark;--bg:#0b1020;--panel:#111a33;--panel2:#172447;--text:#edf4ff;--muted:#98a8c7;--brand:#70f0ff;--hot:#ff4fd8;--ok:#6dff9d;--warn:#ffd166}*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,Segoe UI,sans-serif;background:radial-gradient(circle at top left,#202b64,#0b1020 40%,#050814);color:var(--text)}header{position:sticky;top:0;z-index:2;display:flex;justify-content:space-between;align-items:center;padding:18px 28px;background:rgba(8,12,25,.85);backdrop-filter:blur(18px);border-bottom:1px solid rgba(112,240,255,.18)}h1,h2{margin:0 0 12px}.brand{font-weight:900;letter-spacing:.08em}.pill{border:1px solid rgba(112,240,255,.35);padding:8px 12px;border-radius:999px;color:var(--brand)}main{display:grid;grid-template-columns:280px 1fr;min-height:calc(100vh - 73px)}nav{padding:22px;background:rgba(10,16,34,.72);border-right:1px solid rgba(255,255,255,.08)}nav a{display:block;color:var(--text);text-decoration:none;padding:12px 14px;margin:8px 0;border-radius:14px;background:rgba(255,255,255,.04)}nav a:hover{background:linear-gradient(90deg,rgba(112,240,255,.16),rgba(255,79,216,.12))}.content{padding:28px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}.card{background:linear-gradient(180deg,rgba(23,36,71,.88),rgba(13,20,41,.9));border:1px solid rgba(255,255,255,.1);border-radius:22px;padding:20px;box-shadow:0 20px 70px rgba(0,0,0,.28)}.card.hot{border-color:rgba(255,79,216,.4)}.muted{color:var(--muted)}label{display:block;margin:12px 0 6px;color:var(--muted)}input,select,textarea{width:100%;border:1px solid rgba(255,255,255,.14);background:#071026;color:var(--text);border-radius:12px;padding:11px}button,.button{display:inline-block;border:0;border-radius:14px;background:linear-gradient(135deg,var(--brand),var(--hot));color:#081020;font-weight:800;padding:12px 16px;margin-top:14px;text-decoration:none;cursor:pointer}.tabs{display:flex;gap:8px;flex-wrap:wrap}.tab{padding:9px 12px;border:1px solid rgba(112,240,255,.25);border-radius:999px;color:var(--brand);background:rgba(112,240,255,.06)}pre{white-space:pre-wrap;background:#060a15;border-radius:14px;padding:14px;border:1px solid rgba(255,255,255,.08);overflow:auto}.status{color:var(--ok);font-weight:800}.warning{color:var(--warn)}
"""

MODULES = [
    ("Agency", "First-run agency and investigator profile with admin-locked UI policy."),
    ("Cases", "Create case containers, tasks, notes, timelines, reports and audit logs."),
    ("Evidence", "Hash, custody, provenance and raw/processed evidence separation."),
    ("OSINT", "Public and authorized source collection saved back into active cases."),
    ("Darkweb", "Documented lawful collection workflow, OPSEC notes and source logging."),
    ("Video", "Authorized media acquisition queue with provenance and hash tracking."),
    ("Malware Sandbox", "Integrations only; no sample execution on the Fedora host."),
    ("Ransomware", "Triage, family identification, recovery checklist and legitimate decryptor references."),
    ("Mobile/Computer", "Device investigation workspaces and artifact inventories."),
    ("Drone/CAR-CAN", "Specialized evidence areas for drone and vehicle bus investigations."),
    ("Reports", "Markdown now; planned HTML/PDF templates with agency branding."),
    ("Admin UI", "Admin controls theme, branding, layout and visible modules; users are locked down."),
]


def html_page(title: str, body: str, profile: AgencyProfile | None = None) -> bytes:
    agency = html.escape(profile.agency_name) if profile else "Not configured"
    lock = "Admin locked" if not profile or profile.admin_locked_ui else "User editable"
    page = f"""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title><style>{CSS}</style></head><body><header><div><div class='brand'>IOC-CMS</div><div class='muted'>Fedora/RPM-first investigation platform</div></div><div class='pill'>{agency} · {lock}</div></header><main><nav><a href='/'>Dashboard</a><a href='/agency'>Agency setup</a><a href='/cases'>Cases</a><a href='/evidence'>Evidence</a><a href='/osint'>OSINT & Darkweb</a><a href='/media'>Video/Media</a><a href='/sandbox'>Malware/Ransomware</a><a href='/devices'>Mobile · Drone · CAR-CAN</a><a href='/reports'>Reports</a><a href='/admin'>Admin Theme</a><a href='/api/state'>API State</a></nav><section class='content'>{body}</section></main></body></html>"""
    return page.encode("utf-8")


def case_root(profile: AgencyProfile, case_id: str) -> Path:
    return Path(profile.evidence_root).expanduser() / "cases" / case_id


class IOCGUIHandler(BaseHTTPRequestHandler):
    server_version = "IOC-CMS-GUI/0.1"

    def _send(self, content: bytes, status: HTTPStatus = HTTPStatus.OK, content_type: str = "text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return {k: v[0] for k, v in parse_qs(raw).items()}

    def do_GET(self) -> None:  # noqa: N802
        profile = load_profile()
        path = urlparse(self.path).path
        routes = {
            "/": self.dashboard,
            "/agency": self.agency,
            "/cases": self.cases,
            "/evidence": self.evidence,
            "/osint": self.osint,
            "/media": self.media,
            "/sandbox": self.sandbox,
            "/devices": self.devices,
            "/reports": self.reports,
            "/admin": self.admin,
        }
        if path == "/api/state":
            state = {"configured": profile is not None, "workspace_tabs": WORKSPACE_TABS, "modules": [m[0] for m in MODULES]}
            self._send(json.dumps(state, indent=2).encode(), content_type="application/json; charset=utf-8")
            return
        view = routes.get(path)
        if view is None:
            self._send(b"Not found", HTTPStatus.NOT_FOUND, "text/plain")
            return
        self._send(html_page("IOC-CMS", view(profile), profile))

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        data = self._form()
        if path == "/agency":
            profile = AgencyProfile(
                agency_name=data["agency_name"],
                investigator_name=data["investigator_name"],
                investigator_email=data["investigator_email"],
                jurisdiction=data["jurisdiction"],
                legal_basis=data["legal_basis"],
                evidence_root=str(Path(data.get("evidence_root") or "~/IOC-CMS-Evidence").expanduser()),
                theme=data.get("theme") or "dark-neon",
                admin_locked_ui=data.get("admin_locked_ui") == "on",
            )
            save_profile(profile)
            Path(profile.evidence_root).mkdir(parents=True, exist_ok=True)
            self._send(html_page("Agency saved", "<h2 class='status'>Agency saved</h2><p>Configuration persisted.</p><a class='button' href='/'>Back to dashboard</a>", profile))
            return
        if path == "/cases":
            profile = load_profile()
            if profile is None:
                self._send(html_page("Configure first", "<h2>Configure agency first</h2><a class='button' href='/agency'>Agency setup</a>"))
                return
            root = case_root(profile, data["case_id"])
            for name in CASE_DIRECTORIES:
                (root / name).mkdir(parents=True, exist_ok=True)
            manifest = root / "case.json"
            manifest.write_text(json.dumps({"case_id": data["case_id"], "workspace_tabs": WORKSPACE_TABS}, indent=2), encoding="utf-8")
            self._send(html_page("Case created", f"<h2 class='status'>Case created</h2><pre>{root}</pre><a class='button' href='/cases'>Back</a>", profile))
            return
        self._send(b"Not found", HTTPStatus.NOT_FOUND, "text/plain")

    def dashboard(self, profile: AgencyProfile | None) -> str:
        cards = "".join(f"<div class='card'><h2>{name}</h2><p class='muted'>{desc}</p></div>" for name, desc in MODULES)
        tabs = "".join(f"<span class='tab'>{tab}</span>" for tab in WORKSPACE_TABS)
        return f"<h1>Modern IOC-CMS GUI</h1><p class='muted'>Un singur program pentru agency setup, cases, evidence, OSINT, darkweb, media, sandbox, ransomware, devices și reports.</p><div class='tabs'>{tabs}</div><br><div class='grid'>{cards}</div>"

    def agency(self, profile: AgencyProfile | None) -> str:
        p = profile or AgencyProfile("", "", "", "", "", "~/IOC-CMS-Evidence")
        checked = "checked" if p.admin_locked_ui else ""
        values = {
            "agency_name": html.escape(p.agency_name, quote=True),
            "investigator_name": html.escape(p.investigator_name, quote=True),
            "investigator_email": html.escape(p.investigator_email, quote=True),
            "jurisdiction": html.escape(p.jurisdiction, quote=True),
            "legal_basis": html.escape(p.legal_basis, quote=True),
            "evidence_root": html.escape(p.evidence_root, quote=True),
        }
        return f"""<h1>Agency Setup</h1><form method='post'><label>Agency name</label><input name='agency_name' value='{values["agency_name"]}' required><label>Investigator name</label><input name='investigator_name' value='{values["investigator_name"]}' required><label>Investigator email</label><input name='investigator_email' value='{values["investigator_email"]}' required><label>Jurisdiction</label><input name='jurisdiction' value='{values["jurisdiction"]}' required><label>Legal basis</label><input name='legal_basis' value='{values["legal_basis"]}' required><label>Evidence root</label><input name='evidence_root' value='{values["evidence_root"]}'><label>Theme</label><select name='theme'><option>dark-neon</option><option>dark</option><option>light</option><option>high-contrast</option></select><label><input style='width:auto' type='checkbox' name='admin_locked_ui' {checked}> Admin locks GUI customization for standard users</label><button>Save agency</button></form>"""

    def cases(self, profile: AgencyProfile | None) -> str:
        existing = ""
        if profile:
            root = Path(profile.evidence_root).expanduser() / "cases"
            cases = sorted(p.name for p in root.iterdir() if p.is_dir()) if root.exists() else []
            existing = "<h2>Existing cases</h2>" + ("".join(f"<div class='card'>{html.escape(c)}</div>" for c in cases) or "<p class='muted'>No cases yet.</p>")
        return f"<h1>Cases</h1><form method='post'><label>Case ID</label><input name='case_id' placeholder='DARKNET-001' required><button>Create CSI-CMS-like case</button></form>{existing}"

    def evidence(self, profile: AgencyProfile | None) -> str:
        return "<h1>Evidence</h1><p>Model: original source, capture method, UTC timestamp, MD5, SHA256, submitter, evidence number, custody flag and notes.</p><pre>Evidence/Online/IP-Address\nEvidence/Darkweb\nEvidence/Video\nEvidence/Financial\nEvidence/Mobile\nEvidence/Computer\nEvidence/Drone\nEvidence/CAR-CAN</pre>"

    def osint(self, profile: AgencyProfile | None) -> str:
        return "<h1>OSINT & Darkweb</h1><p>Provider panels will save findings into the active case with citations, hashes, timestamps and OPSEC notes.</p>"

    def media(self, profile: AgencyProfile | None) -> str:
        return "<h1>Video / Media</h1><p>Authorized media acquisition queue. No bypass for authentication, paywalls, DRM or access controls.</p>"

    def sandbox(self, profile: AgencyProfile | None) -> str:
        return "<h1>Malware Sandbox & Ransomware</h1><p>Sandbox integrations only. The Fedora host must not execute malware samples directly.</p>"

    def devices(self, profile: AgencyProfile | None) -> str:
        return "<h1>Mobile · Computer · Drone · CAR-CAN</h1><p>Separate workspaces for device artifacts, repair notes, captures and technical reports.</p>"

    def reports(self, profile: AgencyProfile | None) -> str:
        return "<h1>Reports</h1><p>Markdown reports exist now; HTML/PDF branded reports are the next GUI target.</p>"

    def admin(self, profile: AgencyProfile | None) -> str:
        return "<h1>Admin Theme & Modules</h1><p>Admin controls branding, theme, module visibility and layout. Standard users are locked down by default.</p>"

    def log_message(self, format: str, *args: object) -> None:
        return


def run_gui(host: str = "127.0.0.1", port: int = 8765, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer((host, port), IOCGUIHandler)
    url = f"http://{host}:{port}"
    if open_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    print(f"IOC-CMS GUI running at {url}")
    server.serve_forever()
