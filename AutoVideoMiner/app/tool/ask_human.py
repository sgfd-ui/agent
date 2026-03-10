from __future__ import annotations


class AskHumanTool:
    def request_help(self, message: str) -> None:
        print(f"[HITL REQUIRED] {message}")
