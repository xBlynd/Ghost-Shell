# 🔗 Engine Dependencies & Boot Sequence

## Boot Order (Critical Path)

The Ghost Shell follows a strict initialization sequence. Engines MUST load in this order:

```
1. GhostCoreEngine    [No Dependencies]
   ↓
2. SecurityEngine     [Requires: GhostCoreEngine for OS detection]
   ↓
3. VaultEngine        [Requires: SecurityEngine for encryption key]
   ↓
4. InfoEngine         [Requires: GhostCoreEngine]
   ↓
5. HostEngine         [Requires: GhostCoreEngine, InfoEngine]
   ↓
6. SyncEngine         [Requires: VaultEngine, HostEngine]
   ↓
7. InterfaceEngine    [Requires: GhostCoreEngine]
   ↓
8. LoaderEngine       [Requires: InterfaceEngine, HostEngine]
   ↓
9. PulseEngine        [Requires: SecurityEngine, VaultEngine]
   ↓
10. HeartbeatEngine   [Requires: ALL previous engines for monitoring]
   ↓
11. RootEngine        [Requires: SecurityEngine, HostEngine]
   ↓
12. GhostEngine       [Requires: RootEngine, SecurityEngine]
   ↓
13. BlackBoxEngine    [Requires: GhostCoreEngine, SecurityEngine]
```

## Dependency Matrix

| Engine | Depends On | Provides To | Can Run Without |
|--------|------------|-------------|------------------|
| GhostCoreEngine | None | All | N/A |
| SecurityEngine | GhostCore | VaultEngine, GhostEngine, RootEngine, BlackBoxEngine, PulseEngine | NO |
| VaultEngine | SecurityEngine | SyncEngine, PulseEngine, Commands | NO |
| InfoEngine | GhostCore | HostEngine, Diagnostics | YES (degraded) |
| HostEngine | GhostCore, InfoEngine | SyncEngine, LoaderEngine, RootEngine | NO |
| SyncEngine | VaultEngine, HostEngine | Commands | YES |
| InterfaceEngine | GhostCore | LoaderEngine, Shell UI | NO |
| LoaderEngine | InterfaceEngine, HostEngine | Shell Router | NO |
| PulseEngine | SecurityEngine, VaultEngine | HeartbeatEngine, Reminder Commands | YES |
| HeartbeatEngine | ALL | Self-Healing | YES (monitoring disabled) |
| RootEngine | SecurityEngine, HostEngine | GhostEngine, System Commands | YES |
| GhostEngine | RootEngine, SecurityEngine | Stealth Commands | YES |
| BlackBoxEngine | GhostCore, SecurityEngine | Network Commands | YES |

## Failure Cascade Map

### CRITICAL FAILURES (Shell Cannot Start)
```
GhostCoreEngine FAIL → TOTAL FAILURE
SecurityEngine FAIL → Vault locked, shell cannot authenticate
InterfaceEngine FAIL → No UI, shell cannot display
LoaderEngine FAIL → Commands cannot route
```

### DEGRADED MODE FAILURES (Shell Runs, Features Disabled)
```
VaultEngine FAIL → No encrypted storage, todos/journals unavailable
PulseEngine FAIL → No scheduled tasks or reminders
SyncEngine FAIL → No USB/Cloud sync
InfoEngine FAIL → No system diagnostics
HostEngine FAIL → No file operations or process control
```

### OPTIONAL FAILURES (Shell Runs Normally)
```
HeartbeatEngine FAIL → No self-healing or health monitoring
RootEngine FAIL → No system-level operations
GhostEngine FAIL → No stealth/forensics features
BlackBoxEngine FAIL → No network operations
```

## Engine Communication Protocol

### Message Queue Pattern (Thread-Safe)
```python
from queue import Queue
from threading import Lock

class EngineMessenger:
    def __init__(self):
        self.queues = {}  # engine_name -> Queue
        self.lock = Lock()
    
    def send(self, target_engine, message):
        with self.lock:
            if target_engine in self.queues:
                self.queues[target_engine].put(message)
    
    def register(self, engine_name):
        with self.lock:
            self.queues[engine_name] = Queue()
    
    def receive(self, engine_name, timeout=0.1):
        try:
            return self.queues[engine_name].get(timeout=timeout)
        except:
            return None
```

### Engine State Machine
```
STATES:
- UNLOADED: Engine not yet imported
- INITIALIZING: __init__() running
- READY: Initialized, waiting for dependencies
- RUNNING: Fully operational
- DEGRADED: Running with missing optional dependencies
- FAILED: Crashed or failed initialization
- SHUTDOWN: Gracefully stopped
```

## Initialization Example
```python
# /src/core/kernel.py
class GhostKernel:
    BOOT_SEQUENCE = [
        'ghost_core',
        'security',
        'vault',
        'info',
        'host',
        'sync',
        'interface',
        'loader',
        'pulse',
        'heartbeat',
        'root',
        'ghost',
        'blackbox'
    ]
    
    def boot(self):
        for engine_name in self.BOOT_SEQUENCE:
            try:
                engine = self.load_engine(engine_name)
                engine.initialize()
                self.engines[engine_name] = engine
            except CriticalEngineFailure:
                self.emergency_shutdown()
                raise
            except OptionalEngineFailure:
                self.log_warning(f"{engine_name} failed, running in degraded mode")
                continue
```

## Shutdown Protocol

Engines MUST shutdown in REVERSE boot order:

```
1. BlackBoxEngine.shutdown()   # Close network connections
2. GhostEngine.shutdown()      # Disable stealth mode
3. RootEngine.shutdown()       # Release system hooks
4. HeartbeatEngine.shutdown()  # Stop monitoring
5. PulseEngine.shutdown()      # Cancel scheduled tasks
6. LoaderEngine.shutdown()     # Unload commands
7. InterfaceEngine.shutdown()  # Close UI
8. SyncEngine.shutdown()       # Finish pending syncs
9. HostEngine.shutdown()       # Release file handles
10. InfoEngine.shutdown()      # Close diagnostic streams
11. VaultEngine.shutdown()     # Close encrypted files
12. SecurityEngine.shutdown()  # Wipe encryption key from RAM
13. GhostCoreEngine.shutdown() # Final cleanup
```

## Health Check Protocol

HeartbeatEngine pings each engine every 5 seconds:

```python
health_check = {
    'engine': 'VaultEngine',
    'status': 'RUNNING',
    'uptime': 3600,  # seconds
    'operations': 42,
    'errors': 0,
    'memory_mb': 15.3,
    'last_operation': '2026-02-10T21:45:33Z'
}
```

If an engine doesn't respond within 10 seconds: `DEGRADED` state.  
If an engine throws exception: `FAILED` state, attempt restart.  
If restart fails 3 times: Mark as `DISABLED`, continue without it.

## Recovery Strategies

### Auto-Recovery (HeartbeatEngine)
```python
if engine.state == 'FAILED':
    if engine.restart_attempts < 3:
        engine.restart()
    else:
        engine.disable()
        notify_user(f"{engine.name} is disabled")
```

### User-Initiated Recovery
```bash
# Shell commands
repair                    # Reset all engines, rebuild state
reload                    # Hot-reload specific engine
status --verbose          # Show engine states and dependencies
status engine vault       # Show specific engine diagnostics
```

---

**Last Updated:** 2026-02-10  
**Version:** 1.0  
**Status:** Production Ready
