from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any


class PermissionLevel(StrEnum):
    SAFE = "safe"
    CONFIRM = "confirm"
    DENY = "deny"


@dataclass(frozen=True)
class PermissionDecision:
    level: PermissionLevel
    reason: str


class PermissionLayer:
    destructive_names = {"close_app", "delete_file", "run_process"}

    def decide(self, tool_name: str, args: dict[str, Any]) -> PermissionDecision:
        if tool_name in self.destructive_names:
            return PermissionDecision(PermissionLevel.CONFIRM, "Destructive or disruptive action.")

        if tool_name == "read_file":
            path = Path(str(args.get("path", ""))).expanduser()
            if not path.exists():
                return PermissionDecision(PermissionLevel.DENY, "File does not exist.")
            if path.is_dir():
                return PermissionDecision(PermissionLevel.DENY, "Path is a directory.")

        if tool_name == "open_file":
            path = Path(str(args.get("path", ""))).expanduser()
            if not path.exists():
                return PermissionDecision(PermissionLevel.DENY, "File does not exist.")

        return PermissionDecision(PermissionLevel.SAFE, "Allowed.")

