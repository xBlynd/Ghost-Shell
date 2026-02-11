#!/usr/bin/env python3
"""
PREFLIGHT - Ghost Shell Environment Validator
Runs before shell initialization to ensure all dependencies are met.
"""
import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path

class PreflightCheck:
    def __init__(self):
        self.ROOT = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.os_type = platform.system()
        
    def check_python_version(self):
        """Verify Python 3.8+"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.issues.append(f"Python 3.8+ required. Found: {version.major}.{version.minor}")
        else:
            print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    
    def check_core_modules(self):
        """Verify required Python modules"""
        required = {
            'threading': 'Threading support',
            'queue': 'Message queues',
            'hashlib': 'Cryptography',
            'json': 'Config parsing',
            'pathlib': 'File operations'
        }
        
        for module, desc in required.items():
            try:
                __import__(module)
                print(f"✓ {desc} ({module})")
            except ImportError:
                self.issues.append(f"Missing critical module: {module}")
    
    def check_optional_modules(self):
        """Check for optional but recommended modules"""
        optional = {
            'cryptography': 'Vault encryption (Fernet)',
            'requests': 'Network operations',
            'psutil': 'System monitoring'
        }
        
        for module, desc in optional.items():
            try:
                __import__(module)
                print(f"✓ {desc} ({module})")
            except ImportError:
                self.warnings.append(f"Optional module missing: {module} - {desc}")
    
    def check_folder_structure(self):
        """Verify Ghost Shell folder structure"""
        required_folders = [
            'src/core',
            'src/commands',
            'data/vault',
            'data/config',
            'library'
        ]
        
        for folder in required_folders:
            path = self.ROOT / folder
            if not path.exists():
                print(f"⚠ Creating missing folder: {folder}")
                path.mkdir(parents=True, exist_ok=True)
            else:
                print(f"✓ {folder}")
    
    def check_os_specific_tools(self):
        """Check for OS-specific dependencies"""
        if self.os_type == "Linux":
            tools = {'notify-send': 'Desktop notifications'}
            for tool, desc in tools.items():
                if shutil.which(tool):
                    print(f"✓ {desc} ({tool})")
                else:
                    self.warnings.append(f"Optional tool missing: {tool} - {desc}")
        
        elif self.os_type == "Windows":
            # PowerShell is always available on Windows
            print("✓ PowerShell (notifications)")
    
    def check_permissions(self):
        """Verify write permissions"""
        test_file = self.ROOT / 'data' / '.preflight_test'
        try:
            test_file.write_text("test")
            test_file.unlink()
            print("✓ Write permissions")
        except Exception as e:
            self.issues.append(f"Cannot write to data folder: {e}")
    
    def run(self):
        """Execute all preflight checks"""
        print("=== Ghost Shell Preflight Check ===\n")
        print(f"OS: {self.os_type} {platform.release()}")
        print(f"Root: {self.ROOT}\n")
        
        self.check_python_version()
        self.check_core_modules()
        self.check_optional_modules()
        self.check_folder_structure()
        self.check_os_specific_tools()
        self.check_permissions()
        
        print("\n=== Preflight Results ===")
        
        if self.warnings:
            print("\n⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.issues:
            print("\n❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  - {issue}")
            print("\nGhost Shell cannot start. Fix issues above.")
            return False
        
        print("\n✓ All critical checks passed. Ghost Shell is ready.")
        return True

if __name__ == "__main__":
    checker = PreflightCheck()
    success = checker.run()
    sys.exit(0 if success else 1)
