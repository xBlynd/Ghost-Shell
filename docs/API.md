# Ghost Shell API Reference v6.0

Complete Python API reference for Ghost Shell developers.

**Version:** v6.0-Ghost-Kernel  
**Last Updated:** 2026-02-11  
**Author:** xBlynd / xsvStudio

---

## Table of Contents

1. [Engine API](#engine-api)
2. [Vault API](#vault-api)
3. [Command API](#command-api)
4. [Module System](#module-system)
5. [Core Classes](#core-classes)
6. [Utilities](#utilities)
7. [Examples](#examples)

---

## Engine API

Manage and control Ghost Shell engines programmatically.

### EngineManager Class

```python
from src.core.HostEngine import EngineManager

em = EngineManager()
```

#### Methods

**get_status(engine_name: str) -> dict**
- Get current status of an engine
- Returns: Dictionary with status information

```python
status = em.get_status('vault')
print(f"Status: {status['state']}")
print(f"Health: {status['health']}%")
```

**enable(engine_name: str) -> bool**
- Enable an engine
- Returns: True if successful

```python
if em.enable('ghost'):
    print("Ghost engine enabled")
```

**disable(engine_name: str) -> bool**
- Disable an engine
- Returns: True if successful

```python
if em.disable('heartbeat'):
    print("Heartbeat engine disabled")
```

**restart(engine_name: str) -> bool**
- Restart a failed engine
- Returns: True if successful

```python
if em.restart('sync'):
    print("Sync engine restarted")
```

**list_engines() -> list**
- Get list of all engines
- Returns: List of engine names

```python
engines = em.list_engines()
for engine in engines:
    print(engine)
```

**get_all_status() -> dict**
- Get status of all engines
- Returns: Dictionary with all engine statuses

```python
all_status = em.get_all_status()
for engine, status in all_status.items():
    print(f"{engine}: {status['state']}")
```

---

## Vault API

Secure encrypted storage operations.

### Vault Class

```python
from src.core.vault import Vault

vault = Vault()
```

#### Methods

**set(key: str, value: str) -> bool**
- Store encrypted data
- Returns: True if successful

```python
vault.set('api_key', 'sk-abc123...')
vault.set('db_password', 'secret123')
```

**get(key: str) -> str**
- Retrieve encrypted data
- Returns: Decrypted value or None

```python
api_key = vault.get('api_key')
if api_key:
    print(f"Retrieved key: {api_key[:10]}...")
```

**list_keys() -> list**
- Get all stored keys
- Returns: List of key names

```python
keys = vault.list_keys()
for key in keys:
    print(key)
```

**delete(key: str) -> bool**
- Remove entry from vault
- Returns: True if successful

```python
if vault.delete('old_key'):
    print("Key deleted")
```

**export(filepath: str, password: str) -> bool**
- Backup vault to file
- Returns: True if successful

```python
vault.export('backup.vault', password='backup_password')
```

**import_vault(filepath: str, password: str) -> bool**
- Restore vault from backup
- Returns: True if successful

```python
vault.import_vault('backup.vault', password='backup_password')
```

**get_size() -> int**
- Get vault size in bytes
- Returns: Size in bytes

```python
size = vault.get_size()
print(f"Vault size: {size} bytes")
```

**verify_integrity() -> bool**
- Verify vault encryption integrity
- Returns: True if valid

```python
if vault.verify_integrity():
    print("Vault is secure")
else:
    print("Vault corrupted!")
```

---

## Command API

Execute commands programmatically.

### Shell Class

```python
from src.core.shell import GhostShell

shell = GhostShell()
```

#### Methods

**execute(command: str) -> CommandResult**
- Execute a Ghost Shell command
- Returns: CommandResult object

```python
result = shell.execute('status')
print(f"Output: {result.output}")
print(f"Exit code: {result.return_code}")
```

**execute_batch(commands: list) -> list**
- Execute multiple commands
- Returns: List of CommandResult objects

```python
cmds = ['engine status', 'todo list', 'vault list']
results = shell.execute_batch(cmds)
for result in results:
    print(result.output)
```

**load_command(name: str) -> Command**
- Load a command module
- Returns: Command object

```python
cmd = shell.load_command('status')
result = cmd.execute(['--verbose'])
```

**get_available_commands() -> list**
- List all available commands
- Returns: List of command names

```python
commands = shell.get_available_commands()
for cmd in commands:
    print(cmd)
```

---

## Module System

Create custom commands and modules.

### CommandBase Class

```python
from src.core.command_base import CommandBase

class MyCommand(CommandBase):
    def __init__(self):
        super().__init__()
        self.name = "mycommand"
        self.description = "My custom command"
        self.usage = "mycommand [options]"
    
    def execute(self, args):
        # Your command logic
        print("Command executed!")
        return 0
```

### Module Loading

```python
from src.core.loader_engine import ModuleLoader

loader = ModuleLoader()
module = loader.load('cmd_mycustom')
result = module.main(['arg1', 'arg2'])
```

---

## Core Classes

### CommandResult

Represents the result of a command execution.

```python
result.output        # str - Command output
result.return_code   # int - Exit code (0=success)
result.error         # str - Error message (if any)
result.execution_time # float - Time taken in seconds
```

### Status

Represents system status.

```python
from src.core.info_engine import SystemStatus

status = SystemStatus()
status.get_health_score()      # int 0-100
status.get_engine_status()     # dict
status.get_system_info()       # dict
```

---

## Utilities

### Configuration Manager

```python
from src.core.config import ConfigManager

config = ConfigManager()
value = config.get('theme')
config.set('theme', 'dark')
config.save()
```

### Logger

```python
from src.core.logger import get_logger

logger = get_logger('mymodule')
logger.info("Information message")
logger.error("Error message")
logger.debug("Debug message")
```

---

## Examples

### Example 1: Check System Health

```python
from src.core.HostEngine import EngineManager
from src.core.info_engine import SystemStatus

em = EngineManager()
status_obj = SystemStatus()

health = status_obj.get_health_score()
print(f"System Health: {health}/100")

engines = em.get_all_status()
for engine, status in engines.items():
    if status['state'] != 'RUNNING':
        print(f"WARNING: {engine} is {status['state']}")
```

### Example 2: Secure Data Storage

```python
from src.core.vault import Vault

vault = Vault()

# Store sensitive data
vault.set('db_host', 'db.example.com')
vault.set('db_user', 'admin')
vault.set('db_pass', 'password123')

# Retrieve and use
host = vault.get('db_host')
user = vault.get('db_user')
passwd = vault.get('db_pass')

# Connect to database
connect(host, user, passwd)

# Backup
vault.export('db_backup.vault', password='secure_password')
```

### Example 3: Custom Command

```python
from src.core.command_base import CommandBase

class GreetCommand(CommandBase):
    def __init__(self):
        super().__init__()
        self.name = "greet"
        self.description = "Greet the user"
        self.usage = "greet <name>"
    
    def execute(self, args):
        if not args:
            print("Please provide a name")
            return 1
        
        name = args[0]
        print(f"Hello, {name}!")
        return 0

def main(args):
    cmd = GreetCommand()
    return cmd.execute(args)
```

### Example 4: Execute Multiple Commands

```python
from src.core.shell import GhostShell

shell = GhostShell()

commands = [
    'status',
    'engine status',
    'vault list',
    'todo list'
]

results = shell.execute_batch(commands)

for i, result in enumerate(results):
    print(f"\n=== {commands[i]} ===")
    print(result.output)
    if result.return_code != 0:
        print(f"ERROR: {result.error}")
```

---

## Error Handling

```python
from src.core.errors import GhostShellError, VaultError

try:
    vault = Vault()
    value = vault.get('missing_key')
except VaultError as e:
    print(f"Vault error: {e}")
except GhostShellError as e:
    print(f"Ghost Shell error: {e}")
```

---

## Best Practices

1. **Always use Vault for sensitive data**
   ```python
   # Good
   vault.set('api_key', key)
   
   # Bad - security risk
   global api_key = key
   ```

2. **Check command execution status**
   ```python
   result = shell.execute('command')
   if result.return_code != 0:
       print(f"Failed: {result.error}")
   ```

3. **Use proper logging**
   ```python
   logger.info("Operation started")
   logger.error("Operation failed")
   ```

4. **Handle errors gracefully**
   ```python
   try:
       result = shell.execute(cmd)
   except GhostShellError as e:
       logger.error(f"Command failed: {e}")
       return False
   ```

---

**Last Updated:** 2026-02-11  
**Version:** v6.0-Ghost-Kernel
