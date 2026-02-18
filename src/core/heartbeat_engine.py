"""
Engine 11: Heartbeat Engine - The Immune System
=================================================
Memory usage, thread health, engine status, self-diagnostics.
Boot diagnostics: py_compile checks, required directory verification.

Compartmentalization:
- Read-only monitoring
- Can trigger alerts but does NOT directly fix issues (use repair_missing_dirs for that)
"""

import threading
import sys
import os
import time
import py_compile
import glob as glob_module


# Directories that must exist for Ghost Shell to function correctly
REQUIRED_DIRS = [
    "data/vault",
    "data/vault/journal",
    "data/vault/todos",
    "data/config",
    "data/keys",
    "data/logs",
    "data/cache",
    "data/queue",
    "data/session",
    "library",
    "src/commands/custom",
]


class HeartbeatEngine:
    """The Immune System - health monitoring and boot diagnostics."""

    ENGINE_NAME = "heartbeat"
    ENGINE_VERSION = "2.0.0"

    def __init__(self, kernel):
        self.kernel = kernel
        self.root_dir = kernel.root_dir
        self.boot_time = time.time()
        self._last_diagnostics = None

    # =========================================================================
    # BOOT DIAGNOSTICS
    # =========================================================================

    def run_boot_diagnostics(self):
        """
        Run all boot-time checks. Returns a structured report dict.
        Called by kernel during boot. Warnings are printed by kernel.
        """
        report = {
            "syntax_errors": self.check_python_modules(),
            "missing_dirs": self.check_required_dirs(),
            "timestamp": time.time(),
            "clean": True,
        }
        report["clean"] = (
            len(report["syntax_errors"]) == 0 and
            len(report["missing_dirs"]) == 0
        )
        self._last_diagnostics = report
        return report

    def check_python_modules(self):
        """
        py_compile all .py files under src/.
        Returns list of dicts: [{file, error}] for files with syntax errors.
        """
        errors = []
        src_dir = os.path.join(self.root_dir, "src")

        if not os.path.exists(src_dir):
            return errors

        # Walk src/ tree
        for dirpath, dirnames, filenames in os.walk(src_dir):
            # Skip __pycache__ dirs
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for filename in filenames:
                if not filename.endswith(".py"):
                    continue
                filepath = os.path.join(dirpath, filename)
                try:
                    py_compile.compile(filepath, doraise=True)
                except py_compile.PyCompileError as e:
                    # Make path relative for cleaner output
                    rel_path = os.path.relpath(filepath, self.root_dir)
                    errors.append({
                        "file": rel_path,
                        "error": str(e).split('\n')[0],  # First line only
                    })
                except Exception as e:
                    rel_path = os.path.relpath(filepath, self.root_dir)
                    errors.append({"file": rel_path, "error": str(e)})

        return errors

    def check_required_dirs(self):
        """
        Verify all required directories exist.
        Returns list of missing dir paths (relative to root_dir).
        """
        missing = []
        for rel_dir in REQUIRED_DIRS:
            full_path = os.path.join(self.root_dir, rel_dir)
            if not os.path.exists(full_path):
                missing.append(rel_dir)
        return missing

    def repair_missing_dirs(self, missing=None):
        """
        Create any missing required directories.
        If missing is None, re-checks automatically.
        Returns list of directories that were created.
        """
        if missing is None:
            missing = self.check_required_dirs()

        created = []
        for rel_dir in missing:
            full_path = os.path.join(self.root_dir, rel_dir)
            try:
                os.makedirs(full_path, exist_ok=True)
                created.append(rel_dir)
            except Exception:
                pass
        return created

    def get_last_diagnostics(self):
        """Return the most recent boot diagnostics report, or None."""
        return self._last_diagnostics

    # =========================================================================
    # RUNTIME HEALTH
    # =========================================================================

    def check_health(self):
        """Full system health check."""
        return {
            "uptime_seconds": round(time.time() - self.boot_time, 1),
            "threads": threading.active_count(),
            "thread_names": [t.name for t in threading.enumerate()],
            "memory": self._get_memory(),
            "engines": self._check_engines(),
            "python": sys.version,
            "status": self._overall_status(),
        }

    def _get_memory(self):
        """Get memory usage. Uses psutil if available, falls back to basic."""
        try:
            import psutil
            proc = psutil.Process()
            mem = proc.memory_info()
            return {
                "rss_mb": round(mem.rss / (1024 * 1024), 2),
                "vms_mb": round(mem.vms / (1024 * 1024), 2),
                "source": "psutil",
            }
        except ImportError:
            # Fallback: read from /proc on Linux
            try:
                with open(f"/proc/{os.getpid()}/status", 'r') as f:
                    for line in f:
                        if line.startswith("VmRSS:"):
                            kb = int(line.split()[1])
                            return {
                                "rss_mb": round(kb / 1024, 2),
                                "source": "proc",
                            }
            except Exception:
                pass

            return {"rss_mb": "unknown", "source": "unavailable"}

    def _check_engines(self):
        """Check which engines are loaded vs failed."""
        loaded = []
        failed = []
        for name, engine in self.kernel.engines.items():
            if engine is not None:
                loaded.append(name)
            else:
                failed.append(name)
        return {
            "loaded": loaded,
            "failed": failed,
            "total": len(self.kernel.engines),
        }

    def _overall_status(self):
        """Determine overall system health."""
        engines = self._check_engines()

        if len(engines["failed"]) == 0:
            return "HEALTHY"
        elif any(e in engines["failed"] for e in ["ghost_core", "security"]):
            return "CRITICAL"
        elif len(engines["failed"]) > 3:
            return "DEGRADED"
        else:
            return "OPERATIONAL"
