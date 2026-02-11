
```markdown
# Ghost Shell OS

**Version:** v6.0-Ghost-Kernel  
**Status:** Alpha - Core Infrastructure Complete  
**Philosophy:** *"One Stick, Any Computer, Surgical Precision"*

---

## What is Ghost Shell?

Ghost Shell is a **portable operating environment** that lives on a USB stick or Git repository. It's designed to be your complete digital workspace that runs on any machine (Windows, Linux, Mac) without installation.

Think of it as your **personal OS-in-a-shell** - plug it in anywhere, and you're instantly "at home" with all your tools, data, and workflows.

### Key Features

✅ **Portable** - Runs from USB/folder, no installation required  
✅ **Cross-Platform** - Windows, Linux, MacOS support  
✅ **Encrypted Vault** - Your data secured with AES-256  
✅ **Self-Healing** - Auto-recovery from engine failures  
✅ **Modular** - Enable/disable features as needed  
✅ **Zero-Trace** - Optional stealth operations  

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/xBlynd/xsvCommand-Center.git
cd xsvCommand-Center

# Run preflight check
python PREFLIGHT.py

# Launch Ghost Shell
python src/main.py shell
```


### First Commands

```bash
# See available commands
help

# Check system health
status

# View engine status
engine status

# Create a todo
todo add "Learn Ghost Shell"

# Create encrypted note
note create "secrets" --encrypt
```


---

## Documentation Sections

### Installation Guides

- [Installing Ghost Shell](install/installing.md)
- [USB Setup Guide](install/usb-setup.md)
- [Linux Installation](install/linux.md)
- [Windows Installation](install/windows.md)
- [Mac Installation](install/mac.md)


### Architecture Reference

- [System Architecture](architecture/overview.md)
- [Engine System](architecture/engines.md)
- [Boot Sequence](architecture/boot-sequence.md)
- [Security Model](architecture/security.md)


### User Guides

- [Getting Started](guides/getting-started.md)
- [Daily Workflows](guides/workflows.md)
- [Command Reference](guides/commands.md)
- [Vault Management](guides/vault.md)


### Developer Guides

- [Contributing](dev/contributing.md)
- [Building Engines](dev/building-engines.md)
- [Creating Commands](dev/creating-commands.md)
- [Testing Guide](dev/testing.md)

---

## The 11 Engine System

Ghost Shell's power comes from its modular engine architecture:


| Engine | Status | Purpose |
| :-- | :-- | :-- |
| **GhostCore** | ✅ Active | OS detection, config management |
| **Security** | ✅ Active | Encryption, authentication |
| **Vault** | ✅ Active | Encrypted file storage |
| **Info** | ✅ Active | System diagnostics |
| **Host** | ✅ Active | File operations, process control |
| **Heartbeat** | ✅ Active | Health monitoring, auto-recovery |
| **Sync** | ○ Planned | USB/Cloud synchronization |
| **Interface** | ○ Planned | UI management |
| **Loader** | ○ Planned | Dynamic command loading |
| **Pulse** | ○ Planned | Scheduling, reminders |
| **Root** | ○ Planned | System-level operations |
| **Ghost** | ○ Planned | Stealth operations |
| **BlackBox** | ○ Planned | Network operations |


---

## Philosophy

Ghost Shell is built on three core principles:

1. **Unrestricted Growth**
There is no "feature creep." If you need it, add it. The modular architecture prevents bloat.
2. **Surgical Precision**
Tools should be fast, text-based, and do exactly one thing well.
3. **Portable Soul**
Your data (Vault) is separate from the Logic (Core). Logic is public; Vault is private.

---

## Community

- **GitHub:** [xBlynd/xsvCommand-Center](https://github.com/xBlynd/xsvCommand-Center)
- **Issues:** [Report bugs](https://github.com/xBlynd/xsvCommand-Center/issues)
- **Wiki:** [Community wiki](https://github.com/xBlynd/xsvCommand-Center/wiki)

---

## License

Ghost Shell is open source software. See [LICENSE](../LICENSE) for details.


```

***

## **`/docs/architecture/engines.md`** - Engine System Deep Dive

```markdown
# The Engine System

Ghost Shell's architecture is based on **11 specialized engines** that work together to create a "conscious" operating environment.

## Engine Architecture

### What is an Engine?

An engine is an independent subsystem that:
- Has a specific domain of responsibility
- Can be enabled/disabled independently
- Communicates via thread-safe message queues
- Self-reports health status
- Can auto-recover from failures

### Engine vs Command

**Engines** provide functionality. **Commands** provide the user interface.

```

User types: todo add "Task"
↓
Command: cmd_todo.py (parses arguments, prints output)
↓
Engine: VaultEngine (saves encrypted data to disk)

```

This separation means multiple commands can use the same engine, and engines can be upgraded without breaking commands.

---

## The 11 Engines

### 1. GhostCoreEngine - The Kernel

**Purpose:** OS detection and environment setup  
**Dependencies:** None  
**Critical:** Yes

```python
from src.core.ghost_core_engine import GhostCoreEngine

core = GhostCoreEngine()
core.initialize()

print(core.os_type)      # "Windows" or "Linux"
print(core.is_linux)     # Boolean
config = core.get_config('theme')  # Get setting
```

**Responsibilities:**

- Detect operating system (Windows/Linux/Mac)
- Load `data/config/settings.json`
- Provide OS-specific paths and behaviors
- Set environment variables for other engines

---

### 2. SecurityEngine - The Gatekeeper

**Purpose:** Authentication and encryption
**Dependencies:** GhostCore
**Critical:** Yes

```python
from src.core.security_engine import SecurityEngine

security = SecurityEngine()
security.initialize()

# Authenticate
if security.authenticate("mypassword"):
    # Encrypt data
    encrypted = security.encrypt(b"secret data")
    
    # Decrypt data
    decrypted = security.decrypt(encrypted)
```

**Responsibilities:**

- Derive encryption keys using PBKDF2 (100k iterations)
- Manage session authentication
- Encrypt/decrypt vault data with Fernet (AES-128 CBC)
- Auto-lock after idle timeout
- Wipe keys from RAM on shutdown

**Security Model:**

- Password → PBKDF2 + Salt → 256-bit key
- Key stored in RAM only (never disk)
- Salt stored in `data/config/.salt` (not secret)
- Session timeout: 5 minutes (configurable)

---

### 3. VaultEngine - The Librarian

**Purpose:** Encrypted file storage
**Dependencies:** Security
**Critical:** Yes

```python
from src.core.vault_api import VaultAPI

vault = VaultAPI()
vault.initialize()

# Create encrypted note
vault.create_note("ideas", "My secret thoughts")

# Read note
content = vault.read_note("ideas")

# List all notes
notes = vault.list_notes()
```

**Responsibilities:**

- CRUD operations for encrypted files
- Manage vault folder structure
- Search across encrypted documents
- Repair corrupted vault structure

**Vault Structure:**

```
data/vault/
  ├── notes/        # Encrypted markdown files
  ├── journals/     # Daily journals
  ├── configs/      # Encrypted configs
  ├── loot/         # Captured data
  └── library/      # Reference documents
```


---

### 4. InfoEngine - The Detective

**Purpose:** System diagnostics and monitoring
**Dependencies:** GhostCore
**Critical:** No

```python
from src.core.info_engine import InfoEngine

info = InfoEngine()
info.initialize()

# Get system info
hardware = info.get_hardware_info()
network = info.get_network_info()
processes = info.get_running_processes()
```

**Responsibilities:**

- Collect hardware information (CPU, RAM, disk)
- Monitor network interfaces
- Track running processes
- Generate system reports

---

### 5. HostEngine - The Worker

**Purpose:** File operations and process control
**Dependencies:** GhostCore, Info
**Critical:** Yes

```python
from src.core.host_engine import HostEngine

host = HostEngine()
host.initialize()

# File operations
host.copy_file(src, dst)
host.delete_file(path)

# Process control
host.launch_process("notepad.exe")
host.kill_process(pid)
```

**Responsibilities:**

- Cross-platform file operations
- Process launching and termination
- Path resolution (handles Windows vs Linux)
- File searching and filtering

---

### 6. HeartbeatEngine - The Immune System

**Purpose:** Health monitoring and auto-recovery
**Dependencies:** ALL (monitors everything)
**Critical:** No

```python
from src.core.heartbeat_engine import HeartbeatEngine

heartbeat = HeartbeatEngine()
heartbeat.initialize()  # Starts background thread

# Check health
health = heartbeat.get_all_health()

# Send message
heartbeat.send_message({
    'type': 'restart_request',
    'engine': 'vault'
})
```

**Responsibilities:**

- Monitor all engines every 5 seconds
- Auto-restart failed engines (max 3 attempts)
- Detect and report degraded states
- Process inter-engine messages

**State Machine:**

```
UNLOADED → INITIALIZING → RUNNING → FAILED → RESTARTING
                            ↓
                        SHUTDOWN
```


---

### 7-13. Future Engines

#### 7. SyncEngine - The Bridge

Cross-device data synchronization (USB ↔ Cloud)

#### 8. InterfaceEngine - The Face

UI management, help system, theming

#### 9. LoaderEngine - The Nervous System

Dynamic command loading, plugin system

#### 10. PulseEngine - The Timekeeper

Scheduling, reminders, cron-style jobs

#### 11. RootEngine - The Mechanic

System-level operations, registry tweaks

#### 12. GhostEngine - The Phantom

Stealth operations, anti-forensics

#### 13. BlackBoxEngine - The Shadow Network

Network operations, packet analysis

---

## Engine Communication

Engines communicate via **thread-safe message queues**:

```python
from src.core.kernel import get_kernel

kernel = get_kernel()
messenger = kernel.messenger

# Send message
messenger.send('vault', {
    'type': 'backup_request',
    'priority': 'high'
})

# Receive message
msg = messenger.receive('security', timeout=1.0)
```


---

## Engine Lifecycle

### Boot Sequence

Engines load in strict dependency order:

```
1. GhostCore  (no deps)
2. Security   (needs GhostCore for OS detection)
3. Vault      (needs Security for encryption key)
4. Info       (needs GhostCore)
5. Host       (needs GhostCore + Info)
6. Heartbeat  (monitors all previous engines)
... etc
```


### Failure Handling

**Critical Engine Fails:**

```
SecurityEngine crashes → Kernel emergency shutdown
```

**Optional Engine Fails:**

```
BlackBoxEngine crashes → Mark as DISABLED, continue in degraded mode
```


### Graceful Shutdown

Engines shutdown in **reverse boot order**:

```
13. BlackBoxEngine  (close network connections)
12. GhostEngine     (disable stealth mode)
...
2. SecurityEngine   (wipe encryption key)
1. GhostCore        (final cleanup)
```


---

## Controlling Engines

### Via Command Line

```bash
# View all engine states
python src/main.py engine status

# Enable an engine
python src/main.py engine enable ghost

# Disable an engine
python src/main.py engine disable heartbeat

# Restart an engine
python src/main.py engine restart vault
```


### Via Python API

```python
from src.core.kernel import get_kernel

kernel = get_kernel()

# Get engine instance
vault = kernel.get_engine('vault')

# Enable engine
kernel.enable_engine('ghost')

# Disable engine
kernel.disable_engine('blackbox')

# Check health
health = kernel.monitor_health()
```


---

## Building Your Own Engine

See [Building Engines](../dev/building-engines.md) for a step-by-step guide.

```