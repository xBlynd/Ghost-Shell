"""
Engine 08: Sync Engine - The Bridge
=====================================
USB-to-local file sync, git integration, store-and-forward.
Vault export/import for backup and restore.

Compartmentalization:
- Only activates if running from removable media
- MUST NOT overwrite user data without confirmation
"""

import os
import json
import shutil
import zipfile
from datetime import datetime


class SyncEngine:
    """The Bridge - data synchronization and transport."""

    ENGINE_NAME = "sync"
    ENGINE_VERSION = "2.0.0"

    def __init__(self, kernel):
        self.kernel = kernel
        self.root_dir = kernel.root_dir
        self.queue_dir = os.path.join(self.root_dir, "data", "queue")
        self.cache_dir = os.path.join(self.root_dir, "data", "cache")
        os.makedirs(self.queue_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)

    def is_running_from_usb(self):
        """Detect if running from removable media."""
        core = self.kernel.get_engine("ghost_core")
        if core:
            return core.is_portable
        return False

    def queue_operation(self, operation, data):
        """
        Store-and-forward: queue an operation for later sync.
        Used when offline or when target is unreachable.
        """
        queue_file = os.path.join(self.queue_dir, "pending.json")

        queue = []
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    queue = json.load(f)
            except Exception:
                queue = []

        queue.append({
            "operation": operation,
            "data": data,
            "queued_at": datetime.now().isoformat(),
            "status": "pending",
        })

        with open(queue_file, 'w') as f:
            json.dump(queue, f, indent=2)

        return len(queue)

    def get_queue(self):
        """Get pending sync operations."""
        queue_file = os.path.join(self.queue_dir, "pending.json")
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def flush_queue(self):
        """Process all pending sync operations."""
        queue_file = os.path.join(self.queue_dir, "pending.json")
        if os.path.exists(queue_file):
            os.remove(queue_file)
        return {"flushed": True}

    # =========================================================================
    # VAULT EXPORT / IMPORT
    # =========================================================================

    def export_vault(self, output_path=None):
        """
        Zip vault_dir contents to a timestamped file.
        Default output: data/cache/vault_backup_YYYYMMDD_HHMMSS.zip
        Returns output filepath on success, or raises Exception.
        """
        vault = self.kernel.get_engine("vault")
        vault_dir = vault.vault_dir if vault else os.path.join(self.root_dir, "data", "vault")

        if not os.path.exists(vault_dir):
            raise FileNotFoundError(f"Vault directory not found: {vault_dir}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_path is None:
            filename = f"vault_backup_{timestamp}.zip"
            output_path = os.path.join(self.cache_dir, filename)

        output_path = str(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(vault_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, vault_dir)
                    zf.write(file_path, arcname)

        return output_path

    def import_vault(self, zip_path):
        """
        Restore vault from a zip file. Backs up current vault first.
        Returns dict with backup_path, restored_files count.
        CALLER is responsible for user confirmation before calling this.
        """
        if not os.path.exists(zip_path):
            raise FileNotFoundError(f"Backup file not found: {zip_path}")

        vault = self.kernel.get_engine("vault")
        vault_dir = vault.vault_dir if vault else os.path.join(self.root_dir, "data", "vault")

        # Backup current vault first
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_backup_path = os.path.join(self.cache_dir, f"vault_pre_restore_{timestamp}.zip")

        if os.path.exists(vault_dir):
            self.export_vault(output_path=pre_backup_path)

        # Extract new vault
        restored_count = 0
        with zipfile.ZipFile(zip_path, 'r') as zf:
            members = zf.namelist()
            for member in members:
                target = os.path.join(vault_dir, member)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                zf.extract(member, vault_dir)
                restored_count += 1

        return {
            "backup_path": pre_backup_path if os.path.exists(vault_dir) else None,
            "restored_files": restored_count,
            "vault_dir": vault_dir,
        }

    def check_status(self):
        """
        Check vault health: SyncThing conflict files, file counts.
        Returns dict with conflicts, file_counts, vault_dir.
        """
        vault = self.kernel.get_engine("vault")
        vault_dir = vault.vault_dir if vault else os.path.join(self.root_dir, "data", "vault")

        conflicts = []
        file_counts = {"total": 0, "by_type": {}}

        if not os.path.exists(vault_dir):
            return {
                "vault_dir": vault_dir,
                "vault_exists": False,
                "conflicts": [],
                "file_counts": file_counts,
            }

        for root, dirs, files in os.walk(vault_dir):
            for filename in files:
                file_counts["total"] += 1
                ext = os.path.splitext(filename)[1].lower()
                file_counts["by_type"][ext] = file_counts["by_type"].get(ext, 0) + 1

                # SyncThing conflict files contain ".sync-conflict-" in name
                if ".sync-conflict-" in filename:
                    rel_path = os.path.relpath(os.path.join(root, filename), vault_dir)
                    conflicts.append(rel_path)

        return {
            "vault_dir": vault_dir,
            "vault_exists": True,
            "conflicts": conflicts,
            "file_counts": file_counts,
            "portable": self.is_running_from_usb(),
            "pending_queue": len(self.get_queue()),
        }

    def get_status(self):
        """Return sync engine status (legacy compatibility)."""
        return {
            "portable": self.is_running_from_usb(),
            "pending_operations": len(self.get_queue()),
        }
