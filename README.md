# IOC-CMS pentru Fedora Workstation

Kapiju-Notes pornește acum un proiect practic numit **IOC-CMS**: un Case Management System Fedora/RPM-first pentru investigații autorizate de tip OSINT, darknet intelligence, malware triage, evidence management și raportare automată.

> Folosește acest proiect doar cu mandat, consimțământ, politică internă validă sau altă bază legală documentată. IOC-CMS nu trebuie folosit pentru acces neautorizat, ocolirea autentificării, DRM/paywall bypass sau descărcarea ilegală de conținut.

## Ce include această primă versiune

- CLI Python auditable: `python3 -m ioc_cms`.
- Proces de configurare pentru agenția virtuală, investigator, jurisdicție, bază legală, director de evidențe și temă administrată central.
- Inițializare de caz cu foldere separate pentru raw evidence, processed evidence, OSINT, malware, mobile, computer, drone și CAR-CAN.
- Generator automat de raport Markdown cu datele agenției, investigatorului, sumar, inventar de probe și secțiuni pentru OSINT/malware.
- Installer Fedora/RPM cu dependențe de bază pentru Podman, `yt-dlp`, ExifTool, JSON/SQLite și tooling local.
- Roadmap pentru GUI modern, teme controlate de admin, workspace pe taburi ca CSI-CMS, sandbox malware, ransomware triage, media acquisition și integrare TheHive/Cortex/MISP.

## Instalare rapidă pe Fedora Workstation

```bash
git clone <repo-url> IOC-CMS
cd IOC-CMS
./installer/install-fedora.sh
```

## Configurarea agenției virtuale

Clientul/investigatorul rulează configurarea inițială și declară explicit baza legală a investigației:

```bash
python3 -m ioc_cms configure \
  --agency-name "Kapiju Virtual Agency" \
  --investigator-name "Investigator Name" \
  --investigator-email "investigator@example.org" \
  --jurisdiction "RO/EU" \
  --legal-basis "consent/warrant/corporate-policy" \
  --evidence-root "~/IOC-CMS-Evidence" \
  --theme "dark-neon"
```

## Crearea unui caz și raport automat

```bash
python3 -m ioc_cms case-init DARKNET-001
python3 -m ioc_cms report DARKNET-001 --summary "Initial darknet OSINT and IOC review."
```

Structura creată pentru caz:

```text
~/IOC-CMS-Evidence/cases/DARKNET-001/
├── Evidence/
│   ├── Online/IP-Address/
│   ├── Darkweb/
│   ├── Video/
│   ├── Financial/
│   ├── Mobile/
│   ├── Computer/
│   ├── Drone/
│   └── CAR-CAN/
├── Artifacts/
├── Reports/
├── Notes/
└── Tools/
```

## Capabilități țintă

- **Darknet investigations:** organizare de cazuri, surse, capturi, note, timeline și rapoarte.
- **OSINT:** colectare controlată din surse publice și autorizate, cu log de proveniență.
- **Video/media acquisition:** descărcare doar din surse unde ai drept legal de colectare; nu bypass pentru DRM, login, paywall sau controale de acces.
- **Malware sandbox:** integrare cu sandbox-uri izolate, fără execuție de malware pe hostul Fedora.
- **Ransomware:** triage, identificare familie, indicatori, recuperare din backup și referințe către decryptori legitimi când există.
- **Evidence management:** hashing, chain-of-custody, separare raw/processed și export raport.
- **Mobile/computer/drone/CAR-CAN:** spații de lucru separate pentru artefacte și reparații/investigații tehnice.
- **GUI modern:** interfață viitoare de tip desktop/web app, responsive, cu dashboard-uri, carduri de caz, timeline, panouri OSINT și export rapid de rapoarte.
- **Teme/UI controlate de admin:** administratorul poate personaliza brandingul agenției, culorile, layout-ul și modulele vizibile; utilizatorul obișnuit are modificările blocate sau foarte limitate pentru a păstra consistența operațională și evidența auditabilă.

## Documentație

- Roadmap complet: [`docs/ROADMAP.md`](docs/ROADMAP.md)
- Model de referință CSI-CMS 2026 pentru IOC-CMS: [`docs/CSI_CMS_REFERENCE.md`](docs/CSI_CMS_REFERENCE.md)
- RPM skeleton: [`packaging/rpm/ioc-cms.spec`](packaging/rpm/ioc-cms.spec)
