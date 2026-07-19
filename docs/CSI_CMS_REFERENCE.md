# CSI-CMS 2026 Reference Model for IOC-CMS

Reference article: <https://osintteam.blog/csi-linux-2026-and-the-new-case-management-system-a-practitioner-walkthrough-3e53f1284a2f>

The target for IOC-CMS is a Fedora/RPM-first implementation inspired by the operational ideas described in the CSI Linux 2026 CMS walkthrough, not a clone of CSI Linux.

## Features IOC-CMS should mirror conceptually

- Case-first workflow where the case owns evidence, artifacts, notes, timelines, reports, and audit logs.
- First-run legal/agency wizard that captures agency identity, investigator identity, jurisdiction, and report metadata.
- Generic case container instead of locking the investigator into one case type at creation time.
- Workspace tabs for Case Management, Evidence, Entity, Darkweb, Browser, Video, Sockpuppet, OSINT, Financial, Mobile, RAM, Terminal, Notes, and Templates.
- A persistent evidence table with original source, capture method, UTC timestamp, MD5, SHA256, submitter, evidence number, chain-of-custody flag, and notes.
- Per-artifact reports plus case-level reports generated from templates.
- OSINT modules that save provider output back into the active case instead of loose folders.
- Browser/darkweb/video workflows that preserve captured material with source, timestamp, hashes, and audit entries.
- Admin-controlled GUI customization so agency branding and module visibility remain consistent across users.

## Fedora-specific IOC-CMS direction

- Use Fedora Workstation and RPM packaging as first-class targets.
- Use Podman for local services and isolated analysis components.
- Keep malware analysis behind sandbox integrations rather than executing samples on the host.
- Keep media acquisition limited to lawful, authorized collection without bypassing authentication, paywalls, DRM, or access controls.
