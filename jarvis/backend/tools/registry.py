from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from jarvis.backend.db.repositories import ToolLogRepository
from jarvis.backend.tools.permissions import PermissionLayer, PermissionLevel


ToolHandler = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: ToolHandler

    def openai_schema(self) -> dict[str, Any]:
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ToolRegistry:
    def __init__(
        self,
        permissions: PermissionLayer | None = None,
        logs: ToolLogRepository | None = None,
    ) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self.permissions = permissions or PermissionLayer()
        self.logs = logs or ToolLogRepository()

    def register(self, definition: ToolDefinition) -> None:
        self._tools[definition.name] = definition

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.openai_schema() for tool in self._tools.values()]

    def run(self, name: str, args: dict[str, Any], confirmed: bool = False) -> dict[str, Any]:
        if name not in self._tools:
            result = {"error": f"Unknown tool: {name}"}
            self.logs.add(name, args, result, "error")
            return result

        decision = self.permissions.decide(name, args)
        if decision.level == PermissionLevel.DENY:
            result = {"error": decision.reason}
            self.logs.add(name, args, result, "denied")
            return result

        if decision.level == PermissionLevel.CONFIRM and not confirmed:
            result = {"requires_confirmation": True, "reason": decision.reason}
            self.logs.add(name, args, result, "needs_confirmation")
            return result

        handler = self._tools[name].handler
        accepted = set(inspect.signature(handler).parameters)
        filtered_args = {key: value for key, value in args.items() if key in accepted}
        try:
            result = handler(**filtered_args)
            self.logs.add(name, args, result, "ok")
            return result
        except Exception as exc:  # noqa: BLE001 - tools must fail as data, not crash the agent.
            result = {"error": str(exc)}
            self.logs.add(name, args, result, "error")
            return result

