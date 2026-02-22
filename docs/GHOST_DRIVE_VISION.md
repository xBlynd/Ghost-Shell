# Ghost Drive Vision
# Ghost Shell Phoenix — Portable Deployment Architecture
# Last Updated: 2026-02-22 (partially captured — Ian filling in gaps)

---

## What Ghost Drive Is

Ghost Shell Phoenix isn't just a shell — it's a **portable life operating system** designed
to run anywhere, leave nothing behind, and stay invisible when needed.

**Ghost Drive** is the deployment model that makes this real. Three modes. One codebase.

### Three Deployment Modes

| Mode | How | Typical Use Case |
|------|-----|-----------------|
| **USB Ghost** | Run directly from USB drive, clean exit on close | Hosts you don't own (work PC, borrowed machine, hotel kiosk) |
| **Installed Node** | Wraith installer deploys permanently | Your own machines (home PC, laptop, server) |
| **EXE (Wraith Compiled)** | PyInstaller standalone binary | Hosts with no Python installed, maximum portability |

### The Core Principle

**Choice.** Stay hidden and leave no trace on a host you don't own. Install permanently and
integrate fully on your own machines. Both modes are first-class. Neither is an afterthought.

**Legion ties it together.** Multi-machine mesh networking means your installed nodes form a
private grid. Your USB Ghost can authenticate into the mesh and sync data without leaving
anything on the host. When you pull the drive, the session is gone.

---

## Threat Model & Privacy Goals

Ghost Shell is built for **personal privacy and operational security** — not offense.

### Primary Threat
- Casual snooping: roommates, family, whoever picks up your device
- Personal data hygiene: you own your data, it doesn't leak to cloud services

### Secondary Threat
- IT/employer oversight on machines you use but don't own
- Logging, telemetry, monitoring on shared or corporate hosts
- Leaving traces of your tools, habits, and workflows on foreign machines

### Future / Authorized Context
- Red team / pentesting: Ghost Shell as a toolkit for **authorized** engagements
- OPSEC training: hands-on understanding of how to stay clean on a host
- This context requires explicit authorization — not the default assumption

### Tools Philosophy
- **Curated toolkit** that grows over time — quality over quantity
- **Wrapper commands** for host tools (run host's nmap, netstat, etc. without leaving your own)
- **Anonymity and OPSEC tools** first — privacy-focused, not just offensive capability
- Tools live in `library/` until promoted to custom commands

---

## The Three Deployment Modes (Detail)

### Mode 1: USB Ghost

Run Ghost Shell from a USB drive on a host you don't own.

**What this requires:**
- Anchor Pattern (`ROOT_DIR`) keeps all paths relative — nothing touches the host filesystem
- Clean exit: no temp files, no logs written to host, no registry entries, no artifacts
- Ghost Engine handles the cleanup sequence on shutdown
- Data (vault, config) stays on the USB drive
- Keys stay on the USB drive — never touch the host

**What "getting out clean" means:**
- Any temp files written during session are cleaned up
- Python cache (`__pycache__`) doesn't persist on host
- No crash dumps or error logs written to host paths
- Process exits cleanly — no orphan threads
- *(Ian: fill in additional specifics below in the TODO section)*

### Mode 2: Installed Node

Wraith installer deploys Ghost Shell permanently to a machine you own.

**What this enables:**
- Full Legion mesh participation as a permanent node
- PulseEngine background scheduling and notifications
- Vault data lives locally and syncs via SyncThing
- God Key is machine-specific — security boundary per install
- HeartbeatEngine can run as a startup task for always-on monitoring

**Key constraint:** Each installed node has a unique `node_id` from GhostCore and its own
god.key. Compromise one machine ≠ compromise the mesh.

### Mode 3: EXE (Wraith Compiled)

PyInstaller compiles Ghost Shell to a standalone binary.

**Use case:** Hosts with no Python installed. Maximum drop-and-run portability.

**Current status:** Planned. PyInstaller packaging is on the Wraith Installer roadmap.
Needs testing — some engine dependencies (psutil, cryptography) affect bundle size.

---

## Multi-Machine Architecture (Legion)

### What's Already Built (Phase 1 HTTP)

- HTTP mesh — nodes communicate via REST over LAN or Tailscale VPN (100.x.y.z)
- Node registry — each node knows about peers (`data/legion/`)
- Node roles: **MASTER** / **LEGIONNAIRE** / **HIVE_MIND**
- Store-and-forward queue for offline nodes (`data/queue/`)

### Sync Architecture

| Layer | Mechanism | Syncs? |
|-------|-----------|--------|
| Vault + Config | SyncThing | YES — your data follows you |
| Keys | Per-machine only | NEVER — security boundary |
| Session state | Ephemeral | NEVER — runtime only |
| Legion registry | Per-machine | NEVER — each node knows its own peers |

### Key Engine Files

| Engine | File | Role |
|--------|------|------|
| Engine 12: Legion | `src/core/legion_engine.py` | Mesh networking, node registry, peer comms |
| Engine 08: Sync | `src/core/sync_engine.py` | USB detection, export/import, store-and-forward |
| Engine 01: GhostCore | `src/core/ghost_core.py` | node_id, ROOT_DIR, environment detection |
| Engine 07: Vault | `src/core/vault_engine.py` | Data persistence — only gateway for all data |

### USB Ghost + Legion

A USB Ghost session can authenticate into the Legion mesh using its god.key. Data syncs to/from
the mesh during the session. When the drive is removed, the mesh continues — the USB node is
just offline. No data stranded on the host.

*(Ian: expand this with specific Legion use cases for Ghost Drive if needed)*

---

## Build Roadmap

These are the Ghost Drive-specific build phases. NOT the full Ghost Shell roadmap.

### Phase A — Ghost Engine (Clean Exit)

**Status:** Stub exists (`src/core/ghost_engine.py`) — not implemented.

**What needs building:**
- Session artifact tracking (what did we write during this session?)
- Cleanup sequence: temp files, `__pycache__`, any host-path writes
- Graceful thread shutdown before exit
- "Panic wipe" mode — fast cleanup if session needs to end immediately
- Hook into kernel shutdown sequence

**Priority:** HIGH. This is the foundational promise of Ghost Drive.

### Phase B — Vault Encryption at Rest

**Status:** Vault is plaintext JSON. No encryption.

**What needs building:**
- AES-256 encryption for vault data files
- Key derivation from god.key (already exists per-machine)
- Transparent read/write through VaultEngine (commands don't change)
- Migration path: encrypt existing plaintext vault on first keyed boot

**Priority:** HIGH. USB Ghost with plaintext vault is a privacy risk.

### Phase C — Wraith Installer

**Status:** Planned. Not started.

**What needs building:**
- USB deploy: copy Ghost Shell to target USB, generate new god.key, configure for USB Ghost mode
- Permanent install: deploy to `AppData` or user-chosen path, set startup entry, register Legion node
- EXE compile: PyInstaller build script, bundle handling for optional deps
- Uninstall: clean removal, optionally wipe vault

**Priority:** MEDIUM. Needed for frictionless deployment. USB Ghost works manually for now.

### Phase D — Tools Toolkit

**Status:** `library/` directory exists. Empty.

**What needs building:**
- Curated library scripts for OPSEC/privacy use cases
- Wrapper commands for host tools (net, nmap, etc.)
- Anonymity tools: MAC randomization helpers, traffic analysis, DNS leak check
- Document each tool: what it does, when to use it, what it leaves behind

**Priority:** MEDIUM. Grows organically as needs are identified.

---

## TODO — Ian to Fill In

> **The following pieces of the vision are NOT yet fully captured.**
> Fill this in before the next Ghost Drive build session.
> These gaps exist because we ran out of time to articulate them — not because they don't matter.

- [ ] What specifically was missing from Claude's understanding of Ghost Drive (things you said "I haven't had time to write down yet")
- [ ] Any additional deployment modes or use cases not listed above
- [ ] Specific tools you want in the toolkit (beyond the generic OPSEC/anonymity categories)
- [ ] What "getting out clean" looks like in full detail — the complete checklist beyond the four items discussed (temp files, pycache, crash dumps, orphan threads)
- [ ] Any Legion use cases specific to Ghost Drive — e.g., USB Ghost syncing to mesh, distributed vault, cross-node orchestration
- [ ] The "panic mode" scenario: what triggers it, what it does, what the acceptable loss is
- [ ] Whether the EXE mode has a different threat model than USB Ghost (no Python dependency vs. artifact risk of an EXE on the host)
- [ ] Your target machines for the first Wraith install (home PC, laptop, USB — what's the rollout order?)
- [ ] Any red team / pentesting use cases you want Ghost Drive to eventually support (scope + authorization context)
- [ ] Anything about the anonymity/OPSEC tools direction that's more specific than "privacy first"

---

*This document is intentionally incomplete. The TODO section above is the north star for the
next Ghost Drive planning session. Don't build Ghost Engine or Vault Encryption without filling
in the gaps — the implementation details depend on the answers.*
