# IOC-CMS Roadmap

IOC-CMS is planned as a Fedora/RPM-first case management system for lawful darknet, OSINT, incident response, and digital-forensics investigations.

## Core modules

- Agency onboarding: first-run wizard for agency identity, investigator identity, jurisdiction, legal basis, evidence root, and UI theme.
- Case management: cases, tasks, timeline, chain-of-custody, evidence inventory, notes, tags, and report generation.
- OSINT collection: connectors for public/search, social, breach-intelligence, blockchain, domain/IP, metadata, and dark-web sources where access is lawful.
- Media acquisition: supported public downloads through tools such as `yt-dlp`, with URL, timestamp, hash, and provenance logging. IOC-CMS must not bypass authentication, paywalls, DRM, or access controls.
- Malware sandbox analysis: integration with isolated sandboxes and detonation services; never run untrusted malware on the Fedora workstation host.
- Ransomware support: triage, family identification, indicator extraction, backup/recovery workflow, and links to legitimate decryptors when available. There is no safe promise of universal ransomware decryption.
- Evidence domains: mobile, computer, drone, and CAR-CAN investigation/repair workflows with separate raw and processed evidence areas.
- Reporting: Markdown/HTML/PDF report templates with investigator profile, agency branding, evidence hashes, findings, and appendices.
- Modern GUI: desktop/web interface with dashboards, case cards, timelines, OSINT panels, evidence widgets, and fast report export.
- Admin-controlled customization: agency branding, color palette, layout, enabled modules, and default theme are configurable by administrators; standard users should have customization locked down or restricted to minor accessibility preferences only.

## Safety boundaries

- Use IOC-CMS only with explicit authorization, lawful authority, or consent.
- Preserve original evidence and work on verified copies.
- Record source, acquisition time, tool version, operator, and cryptographic hash for every collected item.
- Avoid automated interaction with darknet services unless the legal basis and operational security plan are documented.
