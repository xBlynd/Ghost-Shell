# Ghost Shell OS - System Architecture

## Overview

Ghost Shell is a portable, command-driven operating system shell designed for advanced system management, monitoring, and control. The architecture follows a modular, engine-based design with a robust kernel at its core.

## Core Architecture

**Version:** v6.0-Ghost-Kernel
**Status:** AUTHORITATIVE

---

## 1. The 11 Core Engines (The Truth)

These are the **ONLY** recognized engines. Any reference to "ShieldEngine", "BlackSmithEngine", or "RoofEngine" is an error and must be purged.

### 💀 1. GhostCoreEngine (The Kernel)
* **Role:** The Brain & Environment Detector.
* **Touchpoint:** The "God Object" initialized in `main.py`.
* **Responsibilities:** OS Detection, Config Loading, Dependency Checks.

### 🛡️ 2. SecurityEngine (The Gatekeeper)
* **Role:** Defense & Authentication.
* **Responsibilities:** Login, Keyfile Checks, Fernet Key Management (RAM only).
* **Note:** This is **NOT** "ShieldEngine".

### 👻 3. GhostEngine (The Phantom)
* **Role:** Offensive Stealth & Anti-Forensics.
* **Responsibilities:** PID Spoofing, Timestomping, Trace Wiping (`clean`).

### 📡 4. BlackBoxEngine (The Shadow Network)
* **Role:** Network Dominance & Forensics.
* **Responsibilities:** Jitter Logging, Incognito Search, Promiscuous Mode.

### ⚡ 5. RootEngine (The Mechanic)
* **Role:** Host Control / God Mode.
* **Responsibilities:** Registry Hacks, Process Killing, Hardware ID Spoofing.
* **Note:** This replaces the old "HostEngine".

### ⏳ 6. PulseEngine (The Timekeeper)
* **Role:** Scheduling & Consciousness.
* **Responsibilities:** Cron jobs, Relative Time parsing (`10m`), Toast Notifications.

### 📚 7. VaultEngine (The Librarian)
* **Role:** Data Management.
* **Responsibilities:** CRUD for Notes/Journals, Search Indexing, Encryption Hooks.

### 🔄 8. SyncEngine (The Bridge)
* **Role:** Data Transport.
* **Responsibilities:** Mirroring (Host <-> USB), Silent Transfer (`ghost cp`).

### 📺 9. InterfaceEngine (The Face)
* **Role:** UI, Help, and Alias Manager.
* **Responsibilities:** Help Menu Generation, Themes, Spinners.

### 🧩 10. LoaderEngine (The Nervous System)
* **Role:** Expansion & Routing.
* **Responsibilities:** Hot-Swap Command Loading, Manifest Parsing.

### 💓 11. HeartbeatEngine (The Immune System)
* **Role:** Vital Signs & Diagnostics.
* **Responsibilities:** Self-Healing, Integrity Checks, Crash Handling.

---

## 2. The Interaction Matrix (Touchpoints)

### 🕵️ Stealth Operations
* **Commands:** `ghost cp`, `clean`, `incognito`
* **Engines:** GhostEngine (Hide PID), RootEngine (Wipe Logs), VaultEngine (Store Loot)

### 📡 Network Operations
* **Commands:** `scan`, `ping`, `netmon`
* **Engines:** BlackBoxEngine (Sockets), RootEngine (Raw Packet), InterfaceEngine (Graphs)

### 🔐 Security Operations
* **Commands:** `login`, `lock`, `encrypt`
* **Engines:** SecurityEngine (Auth), GhostCore (Session), InterfaceEngine (Masked Input)

### 📝 Data Operations
* **Commands:** `note`, `journal`, `search`
* **Engines:** VaultEngine (CRUD), SyncEngine (Mirroring), SecurityEngine (Decrypt)

---

## 3. The Core Rules
1.  **No Direct Print:** Engines never print to screen. They return data. Commands print.
2.  **No Direct File Access:** Only `VaultEngine` opens files in `data/vault`.
3.  **No Hardcoded Paths:** All paths must be relative to `ROOT`.
4.  **Manifest Protocol:** Every command MUST have a `MANIFEST` dict for the Help System.

## 4. Folder Map
* `/bin/` -> Portable Python Runtime
* `/src/core/` -> The 11 Engines
* `/src/commands/` -> The Interface Layer
* `/data/vault/` -> Encrypted User Data
* `/docs/` -> The Constitution (Public)
## System Layers

```
┌─────────────────────────────────────┐
│  Commands Layer (cmd_*.py)          │  User Interface
│  - Shell, Create, Edit, Help, etc.  │
├─────────────────────────────────────┤
│  Main Router (main.py)              │  Command Routing
│  - PREFLIGHT checks                 │
│  - Command dispatch                 │
├─────────────────────────────────────┤
│  Kernel & Engine Layer (src/core)   │  System Core
│  - 11 Specialized Engines           │
│  - Engine management                │
├─────────────────────────────────────┤
│  System Services                    │  Background Tasks
│  - ReminderPulse thread             │
│  - HeartbeatMonitor                 │
│  - WebServer                        │
├─────────────────────────────────────┤
│  Data Layer (data/)                 │  Persistence
│  - Configuration files              │
│  - Vault storage                    │
│  - Logs                             │
└─────────────────────────────────────┘
```

## Boot Sequence

1. **PREFLIGHT Phase** (PREFLIGHT.py)
   - Python 3.8+ version check
   - Core module availability verification
   - Optional module detection
   - Folder structure validation
   - File permissions check
   - System readiness report

2. **Kernel Initialization** (kernel.py)
   - Engine discovery and registration
   - System state setup
   - Configuration loading

3. **Engine Bootstrap** (src/core/*)
   - Each engine initializes in dependency order
   - Security engine locks down access
   - Heartbeat engine starts monitoring
   - Reminder engine starts background thread

4. **Command Routing** (main.py)
   - Command parser reads user input
   - Command module dynamically loaded
   - Engine context provided to command
   - Result returned to user

## Command Architecture

Each command file (cmd_*.py) implements a standard interface:

```python
def run(args=None):
    """Execute the command with optional arguments"""
    # Implementation here
    pass
```

Commands can:
- Access any engine via kernel.get_engine()
- Spawn background tasks via RemindePulse
- Store/retrieve data via VaultEngine
- Execute system commands via HostEngine
- Check system status via InfoEngine

## Background Services

### ReminderPulse Thread
- Runs as daemon thread in cmd_shell.py
- Monitors reminder queue continuously
- Executes scheduled callbacks
- Handles event notifications
- Non-blocking with configurable check interval

### HeartbeatMonitor
- Runs alongside ReminderPulse
- Polls system health every N seconds
- Reports via InfoEngine
- Triggers alarms on anomalies

## Data Storage

```
data/
├── config/
│   ├── reminder_config.json     # ReminderEngine settings
│   ├── system_config.json       # Global configuration
│   └── vault_config.json        # Vault settings
├── vault/
│   └── secrets.encrypted        # Encrypted credentials
├── logs/
│   ├── system.log
│   ├── commands.log
│   └── errors.log
└── version.json                 # Version tracking
```

## Security Model

- **Multi-layer authentication**: User credentials validated on shell entry
- **Encrypted vault**: All secrets stored with AES encryption
- **Permission matrix**: Role-based command access control
- **Session tokens**: Time-limited access credentials
- **Audit logging**: All command execution logged

## Extensibility

### Adding New Commands
1. Create cmd_newcommand.py in src/commands/
2. Implement run(args=None) function
3. Command auto-discovered by main.py
4. Access engines via kernel.get_engine()

### Adding New Engines
1. Create engine_*.py in src/core/
2. Inherit from base Engine class
3. Register with kernel in kernel.py
4. Commands can access via get_engine()

## Performance Characteristics

- **Startup time**: ~500ms-1s (PREFLIGHT + kernel init)
- **Command execution**: 50-200ms typical
- **Memory footprint**: ~50-80MB baseline
- **ReminderPulse overhead**: <1% CPU when idle

## Dependencies

Core dependencies documented in requirements.txt:
- hashlib: Cryptography
- json: Configuration
- threading: Background tasks
- socket: Networking
- sys, os, platform: System utilities
- pathlib: Path handling
- subprocess: Process execution

## Future Architecture Considerations

- Distributed mode: Multi-host coordination
- Event streaming: Real-time event pipeline
- Plugin marketplace: Third-party engine registry
- GraphQL API: Alternative query interface
- Container support: Docker/Kubernetes integration
