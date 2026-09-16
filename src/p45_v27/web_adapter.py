"""Safe Web V1 projection for TRIO ORBIT prospective operation."""
from __future__ import annotations
from pathlib import Path
from typing import Any
from .prospective_web import ProspectiveOrbitService

EXPECTED_STATUS = "P45_TRIO_ORBIT_PROSPECTIVE_WEB_V1"

class FrozenWebAdapter:
    """Compatibility name retained for the existing p45_v27 server."""
    def __init__(self, project_root: Path) -> None:
        self.service = ProspectiveOrbitService(project_root)

    def read(self) -> dict[str, Any]:
        value = self.service.read()
        value["engine_status"] = EXPECTED_STATUS
        return value
