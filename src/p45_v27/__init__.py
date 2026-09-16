"""P45 v2.7 isolated storage foundation.

Stage 3 intentionally contains storage, integrity, export, and legacy read-only
adapters only. Research calculators and selection logic are not implemented.
"""

from .database import StoragePaths, initialize_storage

__all__ = ["StoragePaths", "initialize_storage"]
__version__ = "2.7.0-storage-stage3"

