"""
Ghost Kernel - Engine Orchestrator
Manages engine lifecycle, dependencies, and failure recovery.
"""
import sys
import importlib
from pathlib import Path
from queue import Queue
from threading import Lock, Event
from enum import Enum

ROOT = Path(__file__).parent.parent.parent

class EngineState(Enum):
    UNLOADED = "unloaded"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"
    SHUTDOWN = "shutdown"

class CriticalEngineFailure(Exception):
    """Raised when a critical engine fails - shell cannot continue"""
    pass

class EngineMessenger:
    """Thread-safe message passing between engines"""
    def __init__(self):
        self.queues = {}
        self.lock = Lock()
    
    def register(self, engine_name):
        with self.lock:
            self.queues[engine_name] = Queue()
    
    def send(self, target_engine, message):
        with self.lock:
            if target_engine in self.queues:
                self.queues[target_engine].put(message)
    
    def receive(self, engine_name, timeout=0.1):
        try:
            return self.queues[engine_name].get(timeout=timeout)
        except:
            return None

class EngineWrapper:
    """Wraps an engine with state tracking and health monitoring"""
    def __init__(self, name, module_path, critical=True):
        self.name = name
        self.module_path = module_path
        self.critical = critical
        self.state = EngineState.UNLOADED
        self.instance = None
        self.restart_attempts = 0
        self.max_restarts = 3
        self.errors = []
    
    def load(self):
        """Import and initialize the engine"""
        try:
            self.state = EngineState.INITIALIZING
            module = importlib.import_module(self.module_path)
            
            # Assume engine class name matches module (GhostCoreEngine, etc.)
            class_name = ''.join(word.title() for word in self.name.split('_'))
            engine_class = getattr(module, class_name)
            
            self.instance = engine_class()
            if hasattr(self.instance, 'initialize'):
                self.instance.initialize()
            
            self.state = EngineState.RUNNING
            return True
        
        except Exception as e:
            self.errors.append(str(e))
            self.state = EngineState.FAILED
            if self.critical:
                raise CriticalEngineFailure(f"{self.name} failed: {e}")
            return False
    
    def restart(self):
        """Attempt to restart a failed engine"""
        if self.restart_attempts >= self.max_restarts:
            self.state = EngineState.FAILED
            return False
        
        self.restart_attempts += 1
        print(f"⚠ Restarting {self.name} (attempt {self.restart_attempts}/{self.max_restarts})")
        return self.load()
    
    def shutdown(self):
        """Gracefully shutdown the engine"""
        if self.instance and hasattr(self.instance, 'shutdown'):
            try:
                self.instance.shutdown()
            except Exception as e:
                print(f"⚠ Error shutting down {self.name}: {e}")
        self.state = EngineState.SHUTDOWN

class GhostKernel:
    """
    The Ghost Shell Kernel
    Manages engine boot sequence, health monitoring, and graceful shutdown.
    """
    
    # Boot sequence - ORDER MATTERS
    BOOT_SEQUENCE = [
        ('ghost_core', 'src.core.ghost_core_engine', True),
        ('security', 'src.core.security_engine', True),
        ('vault', 'src.core.vault_api', True),
        ('info', 'src.core.info_engine', False),
        ('host', 'src.core.host_engine', True),
        ('sync', 'src.core.sync_engine', False),
        ('interface', 'src.core.interface_engine', True),
        ('loader', 'src.core.loader_engine', True),
        ('pulse', 'src.core.pulse_engine', False),
        ('heartbeat', 'src.core.heartbeat_engine', False),
        ('root', 'src.core.root_engine', False),
        ('ghost', 'src.core.ghost_engine', False),
        ('blackbox', 'src.core.blackbox_engine', False),
    ]
    
    def __init__(self):
        self.engines = {}
        self.messenger = EngineMessenger()
        self.shutdown_event = Event()
        self.degraded_mode = False
    
    def boot(self):
        """Initialize all engines in boot sequence"""
        print("👻 Ghost Shell Kernel Booting...\n")
        
        for name, module_path, critical in self.BOOT_SEQUENCE:
            wrapper = EngineWrapper(name, module_path, critical)
            self.messenger.register(name)
            
            try:
                if wrapper.load():
                    self.engines[name] = wrapper
                    print(f"✓ {name.upper()}: {wrapper.state.value}")
                else:
                    if critical:
                        raise CriticalEngineFailure(f"{name} is critical and failed")
                    self.degraded_mode = True
                    print(f"⚠ {name.upper()}: DISABLED (non-critical failure)")
            
            except CriticalEngineFailure as e:
                print(f"\n❌ BOOT FAILURE: {e}")
                self.emergency_shutdown()
                raise
        
        if self.degraded_mode:
            print("\n⚠ Ghost Shell running in DEGRADED mode (some features disabled)")
        else:
            print("\n✓ Ghost Shell fully operational")
        
        return True
    
    def get_engine(self, name):
        """Get engine instance by name"""
        wrapper = self.engines.get(name)
        return wrapper.instance if wrapper and wrapper.state == EngineState.RUNNING else None
    
    def monitor_health(self):
        """Check health of all engines (called by HeartbeatEngine)"""
        results = {}
        for name, wrapper in self.engines.items():
            results[name] = {
                'state': wrapper.state.value,
                'restarts': wrapper.restart_attempts,
                'errors': len(wrapper.errors)
            }
        return results
    
    def emergency_shutdown(self):
        """Immediate shutdown on critical failure"""
        print("\n⚠ EMERGENCY SHUTDOWN")
        self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown - REVERSE boot order"""
        print("\n👻 Ghost Shell Kernel Shutting Down...")
        self.shutdown_event.set()
        
        # Shutdown in reverse order
        for name, _, _ in reversed(self.BOOT_SEQUENCE):
            if name in self.engines:
                wrapper = self.engines[name]
                print(f"  Stopping {name}...")
                wrapper.shutdown()
        
        print("✓ Ghost Shell stopped cleanly")

# Global kernel instance
kernel = None

def initialize():
    """Initialize the Ghost Kernel"""
    global kernel
    kernel = GhostKernel()
    return kernel.boot()

def get_kernel():
    """Get the running kernel instance"""
    return kernel
