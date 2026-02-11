***

# Ghost Shell Command Reference v6.0

Complete reference for all Ghost Shell commands and functions.

**Version:** v6.0-Ghost-Kernel  
**Last Updated:** 2026-02-11  
**Author:** xBlynd / xsvStudio

***

## Table of Contents

1. [System Commands](#system-commands)
2. [Status & Monitoring](#status--monitoring)
3. [Help & Documentation](#help--documentation)
4. [Developer Commands](#developer-commands)
5. [Data Management](#data-management)
6. [Security & Vault](#security--vault)
7. [Network Operations](#network-operations)
8. [Utility Commands](#utility-commands)
9. [Configuration](#configuration)
10. [Advanced Usage](#advanced-usage)
11. [API Reference](#api-reference)
12. [Best Practices](#best-practices)

***

## System Commands

### engine - Engine Control
Manage Ghost Shell engines at runtime.

**Usage:**
```bash
engine status                  # Show all engine states
engine list                    # List available engines
engine enable <name>           # Enable an engine
engine disable <name>          # Disable an engine
engine restart <name>          # Restart failed engine
engine info <name>             # Detailed engine information
engine logs <name>             # View engine logs
```

**Examples:**
```bash
engine status                  # View health of all engines
engine info vault              # Detailed vault engine info
engine enable ghost            # Turn on stealth operations
engine disable heartbeat       # Stop health monitoring
engine restart vault           # Restart vault engine
engine logs ghost              # View ghost engine logs
```

**Available Engines:**
- `vault` - Secure encrypted storage
- `ghost` - Stealth operations mode
- `heartbeat` - System health monitoring
- `sync` - Cloud synchronization
- `inspector` - Help system and documentation

***

### version - Version Information
Display Ghost Shell version and build information.

**Usage:**
```bash
version                        # Show version info
version --full                 # Detailed version info
version --check                # Check for updates
```

**Output:**
```
Ghost Shell v6.0-Ghost-Kernel
Build: 2026-02-11
Python: 3.11.x
Platform: Windows/Linux/Mac
Active Engines: 5
Uptime: 2h 34m
```

***

### repair - System Repair
Fix common issues and rebuild structures.

**Usage:**
```bash
repair                         # Full system repair
repair --cache                 # Clear Python cache only
repair --vault                 # Rebuild vault structure
repair --engines               # Reset all engines
repair --config                # Reset configuration
repair --all                   # Complete system rebuild
repair --verify                # Verify integrity only
```

**Actions:**
- Clears `__pycache__` folders
- Rebuilds missing vault folders
- Resets corrupted configs
- Verifies file permissions
- Restarts failed engines
- Validates module integrity

**Examples:**
```bash
repair                         # Auto-fix detected issues
repair --verify                # Check for problems
repair --vault                 # Fix vault issues
repair --all                   # Nuclear option - full rebuild
```

***

## Status & Monitoring

### status - Complete System Status
**The master diagnostic command that checks EVERYTHING in Ghost Shell.**

**Usage:**
```bash
status                         # Full system diagnostic
status --verbose               # Maximum detail output
status --quick                 # Fast essential checks
status --json                  # JSON formatted output
status --export <file>         # Save status to file
status --watch                 # Live monitoring mode
```

**Status Categories Checked:**

#### 1. System Health
```bash
status system                  # OS and Python environment
status system --cpu            # CPU usage and load
status system --memory         # Memory utilization
status system --disk           # Disk space and I/O
```

**Checks:**
- Python version and interpreter
- Operating system details
- CPU usage and threads
- Memory usage (RAM)
- Disk space (all drives)
- System uptime
- Environment variables

#### 2. Engine Status
```bash
status engines                 # All engines overview
status engine <name>           # Specific engine details
status engine vault --deep     # Deep engine diagnostics
```

**For Each Engine Checks:**
- Running state (RUNNING/STOPPED/FAILED/DISABLED)
- Uptime and restart count
- Memory footprint
- Thread count
- Error count and last error
- Performance metrics
- Dependencies status
- Health score (0-100)

#### 3. Module Integrity
```bash
status modules                 # All command modules
status module <name>           # Specific module check
status modules --validate      # Deep validation
```

**Module Checks:**
- File existence and permissions
- Import success
- Syntax validation
- Dependency check
- Version compatibility
- Command registration status
- Execution test
- Error history

#### 4. Vault Status
```bash
status vault                   # Vault system check
status vault --keys            # List all stored keys
status vault --integrity       # Verify encryption
status vault --size            # Storage usage
```

**Vault Checks:**
- Encryption status (enabled/disabled)
- Key count and storage used
- Encryption algorithm (AES-256)
- Last backup timestamp
- Integrity verification
- Access permissions
- Lock status

#### 5. Network Status
```bash
status network                 # Network connectivity
status network --speed         # Connection speed test
status network --endpoints     # Check all endpoints
```

**Network Checks:**
- Internet connectivity
- DNS resolution
- Sync endpoint status
- Firewall status
- Port availability
- Bandwidth test
- Latency measurements

#### 6. Configuration Status
```bash
status config                  # Configuration validation
status config --list           # Show all settings
status config --defaults       # Compare to defaults
```

**Config Checks:**
- Config file existence
- JSON validity
- All required keys present
- Value validation
- Permission checks
- Backup availability

#### 7. Data Status
```bash
status data                    # All data systems
status todos                   # Todo list status
status notes                   # Notes system status
status custom                  # Custom commands
```

**Data Checks:**
- Database connectivity
- Record counts
- Data integrity
- Index status
- Backup status
- Storage usage

#### 8. Performance Metrics
```bash
status performance             # Performance overview
status perf --benchm           # Run benchmarks
status perf --history          # Historical data
```

**Performance Checks:**
- Command execution times
- Engine response times
- Memory efficiency
- CPU utilization
- I/O operations
- Cache hit rates

**Complete Status Output Example:**
```bash
$ status --verbose

╔══════════════════════════════════════════════════════════╗
║           GHOST SHELL SYSTEM STATUS v6.0                 ║
╚══════════════════════════════════════════════════════════╝

[✓] SYSTEM HEALTH
  • OS: Windows 11 Pro (Build 22000)
  • Python: 3.11.8 (x64)
  • CPU: 12.3% (8 cores)
  • Memory: 2.4 GB / 16 GB (15%)
  • Disk: 450 GB / 1 TB (45%)
  • Uptime: 5h 23m
  Status: HEALTHY

[✓] ENGINES (5/5 RUNNING)
  ✓ vault      [RUNNING] Uptime: 5h 23m | Health: 100%
  ✓ ghost      [RUNNING] Uptime: 5h 23m | Health: 98%
  ✓ heartbeat  [RUNNING] Uptime: 5h 23m | Health: 100%
  ✓ sync       [RUNNING] Uptime: 5h 20m | Health: 95%
  ✓ inspector  [RUNNING] Uptime: 5h 23m | Health: 100%
  Status: ALL OPERATIONAL

[✓] MODULES (24/24 LOADED)
  ✓ cmd_status.py     | v6.0 | Last: 0.012s
  ✓ cmd_engine.py     | v6.0 | Last: 0.008s
  ✓ cmd_vault.py      | v6.0 | Last: 0.015s
  ✓ cmd_todo.py       | v6.0 | Last: 0.010s
  ... (20 more modules)
  Status: ALL VALIDATED

[✓] VAULT SYSTEM
  • Encryption: AES-256 ENABLED
  • Keys Stored: 12
  • Storage: 48 KB / 10 MB (0.5%)
  • Last Backup: 2h ago
  • Integrity: 100% VERIFIED
  Status: SECURE

[✓] NETWORK
  • Internet: CONNECTED
  • DNS: RESPONSIVE (8.8.8.8)
  • Sync Endpoint: ONLINE
  • Latency: 23ms
  • Speed: 150 Mbps down / 30 Mbps up
  Status: ONLINE

[✓] CONFIGURATION
  • Config File: VALID
  • Settings: 18/18 validated
  • Theme: dark
  • Stealth: disabled
  Status: CONFIGURED

[✓] DATA SYSTEMS
  • Todos: 8 active, 45 completed
  • Notes: 23 notes, 156 KB
  • Custom Commands: 3 registered
  • Vault Keys: 12 secure
  Status: OPERATIONAL

[✓] PERFORMANCE
  • Avg Command Time: 0.023s
  • Engine Response: 0.008s avg
  • Memory Efficiency: 98%
  • Cache Hit Rate: 87%
  Status: EXCELLENT

╔══════════════════════════════════════════════════════════╗
║  OVERALL SYSTEM STATUS: ✓ FULLY OPERATIONAL             ║
║  Health Score: 98/100 - EXCELLENT                        ║
╚══════════════════════════════════════════════════════════╝

Last Check: 2026-02-11 01:23:45 EST
Next Auto-Check: 01:33:45 EST
```

**Individual Status Checks:**
```bash
# Check specific subsystems
status engine vault            # Just vault engine
status module cmd_todo         # Just todo module
status vault --integrity       # Just vault integrity
status network --endpoints     # Just network endpoints
status config theme            # Just theme config

# Continuous monitoring
status --watch                 # Live updating status
status --watch --interval 5    # Update every 5 seconds

# Export and reporting
status --export report.txt     # Export to text file
status --json > status.json    # JSON output for scripts
status --email admin@example   # Email status report
```

**Status Exit Codes:**
- `0` - All systems operational
- `1` - Minor issues detected
- `2` - Major issues detected
- `3` - Critical failure

***

## Help & Documentation

### help - Interactive Help System
**The Inspector Engine - Complete help and documentation system.**

**Usage:**
```bash
help                           # Interactive help menu
help mmand>                 # Show command help
help --list                    # List all commands
help --category <name>         # Show category commands
help --search <term>           # Search help content
help --inspector               # Open help inspector
```

**Interactive Help Menu:**
```bash
$ help

╔══════════════════════════════════════════════════════════╗
║           GHOST SHELL HELP INSPECTOR v6.0                ║
╚══════════════════════════════════════════════════════════╝

Available Categories:
  1. System Commands      - Core system operations
  2. Status & Monitoring  - System diagnostics
  3. Data Management      - Todos, notes, vault
  4. Security & Vault     - Encryption and security
  5. Network Operations   - Network and sync
  6. Developer Tools      - Dev and debug commands
  7. Utility Commands     - Calculators, tools
  8. Configuration        - System settings

Quick Commands:
  • help mmand>        - Detailed command help
  • help --search <term>  - Search documentation
  • docs                  - Full documentation
  • version               - Version information
  • status                - System status

Navigation:
  • Type a number (1-8) to view category
  • Type 'q' or 'exit' to quit
  • Type 'back' to return to main menu

> _
```

**Detailed Command Help:**
```bash
$ help vault

╔══════════════════════════════════════════════════════════╗
║  COMMAND: vault - Secure Encrypted Storage               ║
╚══════════════════════════════════════════════════════════╝

DESCRIPTION:
  Manage encrypted storage for sensitive data like API keys,
  passwords, tokens, and configuration secrets.

USAGE:
  vault add <key> <value>        # Store encrypted data
  vault get <key>                # Retrieve data
  vault list                     # Show all keys
  vault delete <key>             # Remove entry
  vault export <file>            # Backup vault
  vault import <file>            # Restore vault

EXAMPLES:
  vault add api_key "sk-abc123..."     # Store API key
  vault get api_key                     # Retrieve key
  vault list                            # View all keys
  vault export backup.vault             # Create backup

FEATURES:
  • AES-256 encryption
  • Automatic key derivation
  • Secure memory handling
  • Password-protected backups

RELATED COMMANDS:
  • status vault     - Check vault status
  • engine vault     - Control vault engine
  • ghost            - Stealth operations

SEE ALSO:
  • docs vault       - Full vault documentation
  • help ghost       - Stealth mode help

Press 'q' to quit, 'Enter' for more examples...
```

**Help Inspector Features:**

#### 1. Command Search
```bash
help --search encryption       # Find all encryption-related
help --search "api key"        # Search with phrases
help --search vault            # Find vault references
```

#### 2. Category Browser
```bash
help --category system         # All system commands
help --category security       # All security commands
help --category dev            # All developer commands
```

#### 3. Quick Reference
```bash
help --quick                   # Quick command reference
help --cheatsheet              # Print cheatsheet
help --examples mmand>      # Just show examples
```

#### 4. Interactive Inspector Mode
```bash
help --inspector               # Full interactive mode
```

**Inspector Features:**
- Tab completion for commands
- Fuzzy search
- Command history
- Example execution
- Syntax highlighting
- Bookmark favorite commands
- Export help to file
- Print help

**Help Options:**
```bash
help --verbose                 # Maximum detail
help --brief                   # Minimal info
help --usage                   # Just usage syntax
help --examples                # Just examples
help --api                     # API documentation
help --dev                     # Developer information
```

### docs - Documentation System
Full documentation viewer and editor.

**Usage:**
```bash
docs                           # Documentation index
docs <section>                 # View specific section
docs search <term>             # Search documentation
docs edit <file>               # Open doc in editor
docs generate                  # Regenerate docs
docs export <format>           # Export documentation
```

**Available Documentation:**
```bash
docs list                      # List all docs

Available Documentation:
  • README.md          - Getting started guide
  • commands.md        - This command reference
  • architecture.md    - System architecture
  • DEVELOPER.md       - Developer guide
  • security.md        - Security documentation
  • API.md             - API reference
  • troubleshooting.md