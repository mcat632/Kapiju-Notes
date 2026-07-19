"""Native desktop GUI for IOC-CMS using Tkinter/ttk."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from .cli import AgencyProfile, CASE_DIRECTORIES, WORKSPACE_TABS, case_directory, load_profile, save_profile

ACCENT = "#70f0ff"
BG = "#0b1020"
PANEL = "#111a33"
TEXT = "#edf4ff"
MUTED = "#98a8c7"

MODULES = [
    ("Case Management", "Cases, tasks, timeline, notes, templates and report generation."),
    ("Evidence", "Raw/processed evidence, hashes, custody, provenance and audit notes."),
    ("OSINT", "Public and authorized sources saved back into the active case."),
    ("Darkweb", "Lawful darkweb workflow, OPSEC notes, captures and source logging."),
    ("Browser", "Investigation browser workflow and captured page inventory."),
    ("Video", "Authorized video/media acquisition queue with source and hash tracking."),
    ("Malware Sandbox", "Sandbox integrations only; never detonate on the Fedora host."),
    ("Ransomware", "Family triage, indicators, backups and legitimate decryptor references."),
    ("Automotive", "CAR-CAN, OBD-II, ECU notes, captures, repairs and timeline."),
    ("Drone", "Flight logs, media, controller/mobile artifacts and device inventory."),
    ("SIM/eSIM", "SIM, eSIM, ICCID, IMSI, MSISDN, carrier and activation evidence."),
    ("Cards", "Debit/credit card evidence, issuer, transaction and skimmer context."),
    ("Crypto", "Wallets, addresses, transactions and exchange/KYC references."),
    ("Admin", "Admin locks theme, branding, module visibility and user customization."),
]


class IOCCMSDesktop(tk.Tk):
    """Native Fedora desktop shell for IOC-CMS."""

    def __init__(self) -> None:
        super().__init__()
        self.title("IOC-CMS Desktop")
        self.geometry("1180x760")
        self.minsize(980, 640)
        self.configure(bg=BG)
        self.profile = load_profile()
        self._style()
        self._layout()

    def _style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Inter", 10))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Inter", 20, "bold"))
        style.configure("Card.TLabel", background=PANEL, foreground=TEXT, font=("Inter", 11, "bold"))
        style.configure("TButton", padding=8)
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(14, 8), background=PANEL, foreground=TEXT)
        style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "#081020")])
        style.configure("TEntry", fieldbackground="#071026", foreground=TEXT)

    def _layout(self) -> None:
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=18, pady=(16, 8))
        ttk.Label(header, text="IOC-CMS Desktop", style="Title.TLabel").pack(side="left")
        status = self.profile.agency_name if self.profile else "Agency not configured"
        ttk.Label(header, text=f"{status} · native Fedora desktop", style="Muted.TLabel").pack(side="right")

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=12)
        self._dashboard_tab()
        self._agency_tab()
        self._cases_tab()
        self._module_tabs()

    def _dashboard_tab(self) -> None:
        frame = ttk.Frame(self.tabs, style="TFrame")
        self.tabs.add(frame, text="Dashboard")
        ttk.Label(frame, text="All-in-one IOC-CMS desktop workspace", style="Title.TLabel").pack(anchor="w", pady=(10, 6))
        ttk.Label(frame, text="Case management, evidence, OSINT, darknet, media, malware, ransomware, automotive, drone, SIM/eSIM, cards and crypto.", style="Muted.TLabel").pack(anchor="w")
        grid = ttk.Frame(frame, style="TFrame")
        grid.pack(fill="both", expand=True, pady=18)
        for index, (name, desc) in enumerate(MODULES):
            card = ttk.Frame(grid, style="Panel.TFrame", padding=14)
            card.grid(row=index // 3, column=index % 3, sticky="nsew", padx=8, pady=8)
            ttk.Label(card, text=name, style="Card.TLabel").pack(anchor="w")
            ttk.Label(card, text=desc, style="Muted.TLabel", wraplength=300).pack(anchor="w", pady=(6, 0))
        for col in range(3):
            grid.columnconfigure(col, weight=1)

    def _agency_tab(self) -> None:
        frame = ttk.Frame(self.tabs, style="TFrame", padding=16)
        self.tabs.add(frame, text="Agency")
        p = self.profile or AgencyProfile("", "", "", "", "", "~/IOC-CMS-Evidence")
        fields = [
            ("Agency name", "agency_name", p.agency_name),
            ("Investigator name", "investigator_name", p.investigator_name),
            ("Investigator email", "investigator_email", p.investigator_email),
            ("Jurisdiction", "jurisdiction", p.jurisdiction),
            ("Legal basis", "legal_basis", p.legal_basis),
            ("Evidence root", "evidence_root", p.evidence_root),
            ("Theme", "theme", p.theme),
        ]
        self.agency_vars: dict[str, tk.StringVar] = {}
        for row, (label, key, value) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=6)
            var = tk.StringVar(value=value)
            self.agency_vars[key] = var
            ttk.Entry(frame, textvariable=var, width=70).grid(row=row, column=1, sticky="ew", pady=6, padx=8)
        self.admin_locked = tk.BooleanVar(value=p.admin_locked_ui)
        ttk.Checkbutton(frame, text="Admin locks GUI customization for standard users", variable=self.admin_locked).grid(row=len(fields), column=1, sticky="w", pady=10)
        ttk.Button(frame, text="Save agency profile", command=self.save_agency).grid(row=len(fields) + 1, column=1, sticky="w")
        frame.columnconfigure(1, weight=1)

    def _cases_tab(self) -> None:
        frame = ttk.Frame(self.tabs, style="TFrame", padding=16)
        self.tabs.add(frame, text="Cases")
        self.case_id = tk.StringVar(value="DARKNET-001")
        ttk.Label(frame, text="Case ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.case_id, width=42).grid(row=0, column=1, sticky="w", padx=8)
        ttk.Button(frame, text="Create complete investigation case", command=self.create_case).grid(row=0, column=2, padx=8)
        self.case_list = tk.Listbox(frame, bg="#071026", fg=TEXT, highlightthickness=0, height=18)
        self.case_list.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=16)
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(1, weight=1)
        self.refresh_cases()

    def _module_tabs(self) -> None:
        for tab in WORKSPACE_TABS:
            frame = ttk.Frame(self.tabs, style="TFrame", padding=16)
            self.tabs.add(frame, text=tab)
            ttk.Label(frame, text=tab, style="Title.TLabel").pack(anchor="w")
            ttk.Label(frame, text=self._description_for(tab), style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=10)

    def _description_for(self, tab: str) -> str:
        extra = {
            "Evidence": "Includes online evidence, darkweb captures, videos, financial data, mobile/computer/drone/CAR-CAN, SIM/eSIM and debit/credit card artifacts.",
            "Darkweb": "Keep source, timestamp, capture method, OPSEC notes and hashes for every authorized collection.",
            "Financial": "Crypto, debit/credit card, transaction and exchange/KYC references are tracked as evidence domains.",
            "Mobile": "SIM, eSIM, ICCID, IMSI, MSISDN, app artifacts and handset evidence are first-class targets.",
        }
        return extra.get(tab, "Desktop module placeholder wired into the IOC-CMS workspace; implementation will store artifacts in the active case.")

    def save_agency(self) -> None:
        profile = AgencyProfile(
            agency_name=self.agency_vars["agency_name"].get(),
            investigator_name=self.agency_vars["investigator_name"].get(),
            investigator_email=self.agency_vars["investigator_email"].get(),
            jurisdiction=self.agency_vars["jurisdiction"].get(),
            legal_basis=self.agency_vars["legal_basis"].get(),
            evidence_root=str(Path(self.agency_vars["evidence_root"].get()).expanduser()),
            theme=self.agency_vars["theme"].get(),
            admin_locked_ui=self.admin_locked.get(),
        )
        save_profile(profile)
        Path(profile.evidence_root).mkdir(parents=True, exist_ok=True)
        self.profile = profile
        messagebox.showinfo("IOC-CMS", "Agency profile saved.")
        self.refresh_cases()

    def create_case(self) -> None:
        if self.profile is None:
            messagebox.showwarning("IOC-CMS", "Configure the agency profile first.")
            return
        case_id = self.case_id.get().strip()
        if not case_id:
            messagebox.showwarning("IOC-CMS", "Case ID is required.")
            return
        try:
            case_dir = case_directory(self.profile, case_id)
        except ValueError as exc:
            messagebox.showwarning("IOC-CMS", str(exc))
            return
        for name in CASE_DIRECTORIES:
            (case_dir / name).mkdir(parents=True, exist_ok=True)
        (case_dir / "case.json").write_text(
            json.dumps({"case_id": case_id, "workspace_tabs": WORKSPACE_TABS, "case_directories": CASE_DIRECTORIES}, indent=2),
            encoding="utf-8",
        )
        self.refresh_cases()
        messagebox.showinfo("IOC-CMS", f"Case created:\n{case_dir}")

    def refresh_cases(self) -> None:
        self.case_list.delete(0, tk.END)
        if self.profile is None:
            self.case_list.insert(tk.END, "Configure agency first.")
            return
        root = Path(self.profile.evidence_root).expanduser() / "cases"
        if not root.exists():
            self.case_list.insert(tk.END, "No cases yet.")
            return
        for case in sorted(p.name for p in root.iterdir() if p.is_dir()):
            self.case_list.insert(tk.END, case)


def run_desktop() -> None:
    app = IOCCMSDesktop()
    app.mainloop()
