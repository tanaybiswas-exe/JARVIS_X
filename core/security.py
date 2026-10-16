from enum import Enum
from pathlib import Path
from typing import Set
from backend.core.config import WORKSPACE_PATH

class PermissionLevel(str, Enum):
    SAFE = "SAFE"
    CONFIRM = "CONFIRM"
    RESTRICTED = "RESTRICTED"

class SecurityController:
    DISALLOWED_PROCESS_NAMES: Set[str] = {
        "cmd.exe", "powershell.exe", "bash.exe", "regedit.exe", "format.com"
    }

    @staticmethod
    def validate_file_path(target_path: str) -> Path:
        resolved = Path(target_path).resolve()
        if not str(resolved).startswith(str(WORKSPACE_PATH)):
            raise PermissionError(
                f"Security Sandbox Violation: Path {resolved} is outside the allowed workspace: {WORKSPACE_PATH}"
            )
        return resolved

    @classmethod
    def validate_application_name(cls, app_name: str) -> str:
        clean_name = app_name.strip().lower()
        if clean_name in cls.DISALLOWED_PROCESS_NAMES:
            raise PermissionError(f"Security Alert: Execution of {clean_name} is restricted.")
        return app_name