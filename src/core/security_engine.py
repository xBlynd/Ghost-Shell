"""
SecurityEngine - Authentication & Encryption
Handles vault encryption keys, session management, and 2FA.
"""
import os
import hashlib
import secrets
from pathlib import Path
from threading import Lock
import time

# Optional but recommended
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

ROOT = Path(__file__).parent.parent.parent

class SecurityEngine:
    """
    The Gatekeeper - Manages authentication and encryption.
    """
    
    def __init__(self):
        self.encryption_key = None  # RAM ONLY - NEVER DISK
        self.salt = None
        self.session_start = None
        self.lock = Lock()
        self.idle_timeout = 300  # 5 minutes
        self.last_activity = time.time()
    
    def initialize(self):
        """Load or generate salt (salt is NOT secret, can be stored)"""
        salt_file = ROOT / 'data' / 'config' / '.salt'
        
        if salt_file.exists():
            self.salt = salt_file.read_bytes()
        else:
            self.salt = os.urandom(32)  # 256-bit salt
            salt_file.parent.mkdir(parents=True, exist_ok=True)
            salt_file.write_bytes(self.salt)
        
        print("SecurityEngine initialized")
    
    def derive_key(self, password: str) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        This is SLOW on purpose (100k iterations) to resist brute force.
        """
        if not CRYPTO_AVAILABLE:
            # Fallback to simple SHA256 (NOT RECOMMENDED but works)
            return hashlib.sha256(password.encode() + self.salt).digest()
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,  # Slow = secure
        )
        return kdf.derive(password.encode())
    
    def authenticate(self, password: str) -> bool:
        """
        Authenticate user and unlock vault.
        Stores encryption key in RAM.
        """
        try:
            key = self.derive_key(password)
            
            if CRYPTO_AVAILABLE:
                self.encryption_key = Fernet(Fernet.generate_key())  # For now, just validate
            else:
                self.encryption_key = key
            
            self.session_start = time.time()
            self.
