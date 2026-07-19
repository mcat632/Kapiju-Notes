"""Command-line entry point for IOC-CMS.

The first release intentionally provides an auditable local CLI skeleton for
lawful investigations. High-risk actions such as malware execution, ransomware
recovery, or dark-web collection are represented as controlled workflows rather
than opaque one-click automation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

APP_DIR = Path.home() / ".config" / "ioc-cms"
CONFIG_FILE = APP_DIR / "agency.json"

WORKSPACE_TABS = [
    "Case Management",
    "Evidence",
    "Entity",
    "Darkweb",
    "Browser",
    "Video",
    "Sockpuppet",
    "OSINT",
    "Financial",
    "Mobile",
    "RAM",
    "Terminal",
    "Notes",
    "Templates",
]

CASE_DIRECTORIES = [
    "Evidence/Online/IP-Address",
    "Evidence/Online/Domain",
    "Evidence/Online/Username",
    "Evidence/Darkweb",
    "Evidence/Video",
    "Evidence/Financial/Crypto",
    "Evidence/Financial/Transactions",
    "Evidence/Mobile",
    "Evidence/Computer",
    "Evidence/Drone",
    "Evidence/CAR-CAN",
    "Artifacts",
    "Reports",
    "Notes",
    "Tools/Browser",
    "Tools/Sandbox",
    "Tools/Sockpuppet",
    "raw",
    "processed",
    "reports",
    "osint",
    "malware",
    "mobile",
    "computer",
    "drone",
    "car-can",
]


@dataclass
class AgencyProfile:
    agency_name: str
    investigator_name: str
    investigator_email: str
    jurisdiction: str
    legal_basis: str
    evidence_root: str
    theme: str = "dark-neon"
    admin_locked_ui: bool = True


def load_profile() -> AgencyProfile | None:
    if not CONFIG_FILE.exists():
        return None
    data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    data.setdefault("admin_locked_ui", True)
    return AgencyProfile(**data)


def save_profile(profile: AgencyProfile) -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(asdict(profile), indent=2, ensure_ascii=False), encoding="utf-8")


def configure(args: argparse.Namespace) -> int:
    profile = AgencyProfile(
        agency_name=args.agency_name,
        investigator_name=args.investigator_name,
        investigator_email=args.investigator_email,
        jurisdiction=args.jurisdiction,
        legal_basis=args.legal_basis,
        evidence_root=str(Path(args.evidence_root).expanduser()),
        theme=args.theme,
        admin_locked_ui=not args.allow_user_theme_changes,
    )
    save_profile(profile)
    Path(profile.evidence_root).expanduser().mkdir(parents=True, exist_ok=True)
    print(f"IOC-CMS agency configured: {profile.agency_name}")
    print(f"Config saved to: {CONFIG_FILE}")
    return 0


def report(args: argparse.Namespace) -> int:
    profile = load_profile()
    if profile is None:
        print("Run `ioc-cms configure ...` first.")
        return 2
    report_dir = Path(profile.evidence_root).expanduser() / "cases" / args.case_id / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_file = report_dir / f"{args.case_id}-{timestamp}.md"
    report_file.write_text(
        "\n".join(
            [
                f"# IOC-CMS Investigation Report: {args.case_id}",
                "",
                f"- Agency: {profile.agency_name}",
                f"- Investigator: {profile.investigator_name} <{profile.investigator_email}>",
                f"- Jurisdiction: {profile.jurisdiction}",
                f"- Legal basis: {profile.legal_basis}",
                f"- UI customization: {'admin-locked' if profile.admin_locked_ui else 'user-editable'}",
                f"- Created UTC: {timestamp}",
                "",
                "## Executive Summary",
                args.summary or "TBD",
                "",
                "## Workspace Tabs",
                ", ".join(WORKSPACE_TABS),
                "",
                "## Evidence Inventory",
                "- Add hashes, source URLs, acquisition time, capture method, submitter, MD5/SHA256, custody flag, and notes here.",
                "",
                "## OSINT Findings",
                "- Add verified findings and source citations here.",
                "",
                "## Malware/Sandbox Notes",
                "- Add sandbox references only; do not execute samples on the host.",
            ]
        ),
        encoding="utf-8",
    )
    print(report_file)
    return 0


def intake(args: argparse.Namespace) -> int:
    profile = load_profile()
    if profile is None:
        print("Run `ioc-cms configure ...` first.")
        return 2
    case_dir = Path(profile.evidence_root).expanduser() / "cases" / args.case_id
    for name in CASE_DIRECTORIES:
        (case_dir / name).mkdir(parents=True, exist_ok=True)
    manifest = case_dir / "case.json"
    if not manifest.exists():
        manifest.write_text(
            json.dumps(
                {
                    "case_id": args.case_id,
                    "created_utc": datetime.now(timezone.utc).isoformat(),
                    "workspace_tabs": WORKSPACE_TABS,
                    "evidence_model": [
                        "original_source",
                        "capture_method",
                        "capture_timestamp_utc",
                        "md5",
                        "sha256",
                        "submitter",
                        "evidence_number",
                        "chain_of_custody",
                        "notes",
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    print(case_dir)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ioc-cms", description="IOC-CMS for lawful Fedora/RPM investigations")
    sub = parser.add_subparsers(required=True)

    cfg = sub.add_parser("configure", help="configure the virtual agency and investigator profile")
    cfg.add_argument("--agency-name", required=True)
    cfg.add_argument("--investigator-name", required=True)
    cfg.add_argument("--investigator-email", required=True)
    cfg.add_argument("--jurisdiction", required=True)
    cfg.add_argument("--legal-basis", required=True, help="warrant, consent, corporate policy, or other lawful authority")
    cfg.add_argument("--evidence-root", default="~/IOC-CMS-Evidence")
    cfg.add_argument("--theme", default="dark-neon")
    cfg.add_argument(
        "--allow-user-theme-changes",
        action="store_true",
        help="allow non-admin users to change UI theme/customization; disabled by default",
    )
    cfg.set_defaults(func=configure)

    case = sub.add_parser("case-init", help="create evidence folders for a new case")
    case.add_argument("case_id")
    case.set_defaults(func=intake)

    rep = sub.add_parser("report", help="generate a Markdown investigation report")
    rep.add_argument("case_id")
    rep.add_argument("--summary")
    rep.set_defaults(func=report)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
