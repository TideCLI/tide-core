"""
Planning Tools - Task planning and context management for Tide
Tools: planner, context_manager
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .base import Tool, ToolResult, ToolParameter


class PlannerTool(Tool):
    """Task planning and tracking for multi-step operations"""
    name = "planner"
    description = "Create and manage a task plan for complex multi-step operations"
    category = "planning"
    requires_confirmation = False

    parameters = [
        ToolParameter("action", "string", "Action: create, update, complete, fail, get, clear", True),
        ToolParameter("goal", "string", "The overall goal (for 'create')", False, ""),
        ToolParameter("tasks", "array", "List of task description strings (for 'create')", False, []),
        ToolParameter("task_id", "integer", "Task number to update (1-indexed)", False, 0),
        ToolParameter("status", "string", "New status: pending, in_progress, completed, failed", False, ""),
        ToolParameter("note", "string", "Note to add to the task", False, "")
    ]

    def __init__(self, working_dir: str = "."):
        super().__init__(working_dir)
        self._plan = None
        self._plan_file = Path(working_dir) / ".tide" / "plan.json"
        self._load_plan()

    def _load_plan(self):
        """Load plan from file if exists"""
        if self._plan_file.exists():
            try:
                with open(self._plan_file, 'r') as f:
                    self._plan = json.load(f)
            except Exception:
                self._plan = None

    def _save_plan(self):
        """Save plan to file"""
        self._plan_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._plan_file, 'w') as f:
            json.dump(self._plan, f, indent=2)

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        try:
            action = params.get("action", "").lower()

            if action == "create":
                result = self._create_plan(params)
            elif action == "update":
                result = self._update_task(params)
            elif action == "complete":
                result = self._complete_task(params)
            elif action == "fail":
                result = self._fail_task(params)
            elif action == "get":
                result = self._get_plan()
            elif action == "clear":
                result = self._clear_plan()
            else:
                result.error = f"Unknown action: {action}. Use: create, update, complete, fail, get, clear"
                result.success = False

        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()

        return result

    def _create_plan(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        goal = params.get("goal", "")
        tasks = params.get("tasks", [])

        if not goal:
            result.error = "Goal is required for creating a plan"
            result.success = False
            return result

        if not tasks:
            result.error = "At least one task is required"
            result.success = False
            return result

        self._plan = {
            "goal": goal,
            "tasks": [
                {
                    "id": i + 1,
                    "description": task,
                    "status": "pending",
                    "note": ""
                }
                for i, task in enumerate(tasks)
            ],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self._save_plan()

        result.output = self._format_plan()
        result.metadata = {"task_count": len(tasks), "goal": goal}
        return result

    def _update_task(self, params: Dict) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        if not self._plan:
            result.error = "No plan exists. Create one first."
            result.success = False
            return result

        task_id = params.get("task_id", 0)
        status = params.get("status", "")
        note = params.get("note", "")

        task = self._find_task(task_id)
        if not task:
            result.error = f"Task {task_id} not found"
            result.success = False
            return result

        if status:
            task["status"] = status
        if note:
            task["note"] = note

        self._plan["updated_at"] = datetime.now().isoformat()
        self._save_plan()

        result.output = self._format_plan()
        return result

    def _complete_task(self, params: Dict) -> ToolResult:
        params["status"] = "completed"
        return self._update_task(params)

    def _fail_task(self, params: Dict) -> ToolResult:
        params["status"] = "failed"
        return self._update_task(params)

    def _get_plan(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        if not self._plan:
            result.output = "No active plan."
            return result

        result.output = self._format_plan()
        result.metadata = {
            "goal": self._plan["goal"],
            "total": len(self._plan["tasks"]),
            "completed": sum(1 for t in self._plan["tasks"] if t["status"] == "completed"),
            "pending": sum(1 for t in self._plan["tasks"] if t["status"] == "pending"),
            "failed": sum(1 for t in self._plan["tasks"] if t["status"] == "failed")
        }
        return result

    def _clear_plan(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        self._plan = None
        if self._plan_file.exists():
            self._plan_file.unlink()
        result.output = "Plan cleared."
        return result

    def _find_task(self, task_id: int):
        if not self._plan:
            return None
        for task in self._plan["tasks"]:
            if task["id"] == task_id:
                return task
        return None

    def _format_plan(self) -> str:
        if not self._plan:
            return "No active plan."

        status_icons = {
            "pending": "[ ]",
            "in_progress": "[~]",
            "completed": "[x]",
            "failed": "[!]"
        }

        total = len(self._plan["tasks"])
        completed = sum(1 for t in self._plan["tasks"] if t["status"] == "completed")
        progress = int((completed / total) * 100) if total > 0 else 0

        lines = [
            f"Goal: {self._plan['goal']}",
            f"Progress: {completed}/{total} ({progress}%)",
            f"{'=' * 40}",
            ""
        ]

        for task in self._plan["tasks"]:
            icon = status_icons.get(task["status"], "[ ]")
            lines.append(f"  {icon} {task['id']}. {task['description']}")
            if task.get("note"):
                lines.append(f"       Note: {task['note']}")

        return '\n'.join(lines)


class ContextManagerTool(Tool):
    """Manage conversation context and token usage"""
    name = "context_manager"
    description = "Track token usage, pin important facts, and manage context window"
    category = "planning"
    requires_confirmation = False

    # Approximate tokens per word (English average)
    TOKENS_PER_WORD = 1.3
    DEFAULT_CONTEXT_WINDOW = 8192

    parameters = [
        ToolParameter("action", "string", "Action: status, pin, unpin, list_pins, summarize, scratchpad", True),
        ToolParameter("content", "string", "Content to pin or add to scratchpad", False, ""),
        ToolParameter("label", "string", "Label for the pinned item", False, "")
    ]

    def __init__(self, working_dir: str = "."):
        super().__init__(working_dir)
        self._pins = []        # List of {"label": "", "content": ""}
        self._scratchpad = []  # List of notes
        self._context_window = self.DEFAULT_CONTEXT_WINDOW
        self._data_file = Path(working_dir) / ".tide" / "context.json"
        self._load()

    def _load(self):
        if self._data_file.exists():
            try:
                with open(self._data_file, 'r') as f:
                    data = json.load(f)
                    self._pins = data.get("pins", [])
                    self._scratchpad = data.get("scratchpad", [])
            except Exception:
                pass

    def _save(self):
        self._data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._data_file, 'w') as f:
            json.dump({
                "pins": self._pins,
                "scratchpad": self._scratchpad
            }, f, indent=2)

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        try:
            action = params.get("action", "").lower()
            content = params.get("content", "")
            label = params.get("label", "")

            if action == "status":
                result = self._get_status()
            elif action == "pin":
                result = self._pin(content, label)
            elif action == "unpin":
                result = self._unpin(label)
            elif action == "list_pins":
                result = self._list_pins()
            elif action == "scratchpad":
                result = self._add_to_scratchpad(content)
            elif action == "summarize":
                result = self._suggest_summarize()
            else:
                result.error = f"Unknown action: {action}"
                result.success = False

        except Exception as e:
            result.error = str(e)
            result.success = False
        finally:
            result.set_finished()

        return result

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count from text"""
        words = len(text.split())
        return int(words * self.TOKENS_PER_WORD)

    def estimate_messages_tokens(self, messages) -> int:
        """Estimate tokens in a list of messages (called externally by agent)"""
        total = 0
        for msg in messages:
            if hasattr(msg, 'content'):
                total += self._estimate_tokens(msg.content)
            elif isinstance(msg, dict):
                total += self._estimate_tokens(msg.get('content', ''))
        return total

    def _get_status(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        # Report what we can about reserved tokens
        pin_tokens = sum(self._estimate_tokens(p["content"]) for p in self._pins)
        scratch_tokens = sum(self._estimate_tokens(s) for s in self._scratchpad)
        reserved = pin_tokens + scratch_tokens

        available = self._context_window - reserved
        usage_pct = int((reserved / self._context_window) * 100)

        # Progress bar
        bar_len = 30
        filled = int(bar_len * reserved / self._context_window)
        bar = '=' * filled + '-' * (bar_len - filled)

        lines = [
            f"Context Window: {self._context_window} tokens",
            f"Reserved (pins + scratchpad): ~{reserved} tokens",
            f"Available: ~{available} tokens",
            f"Usage: [{bar}] {usage_pct}%",
            f"",
            f"Pinned items: {len(self._pins)}",
            f"Scratchpad notes: {len(self._scratchpad)}"
        ]

        result.output = '\n'.join(lines)
        result.metadata = {
            "context_window": self._context_window,
            "reserved_tokens": reserved,
            "available_tokens": available,
            "pins": len(self._pins),
            "scratchpad": len(self._scratchpad)
        }
        return result

    def _pin(self, content: str, label: str) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        if not content:
            result.error = "Content is required to pin"
            result.success = False
            return result

        label = label or f"pin_{len(self._pins) + 1}"
        self._pins.append({"label": label, "content": content})
        self._save()

        result.output = f"Pinned: [{label}] {content[:80]}"
        result.metadata = {"total_pins": len(self._pins)}
        return result

    def _unpin(self, label: str) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        if not label:
            result.error = "Label is required to unpin"
            result.success = False
            return result

        before = len(self._pins)
        self._pins = [p for p in self._pins if p["label"] != label]
        self._save()

        if len(self._pins) < before:
            result.output = f"Unpinned: {label}"
        else:
            result.output = f"Pin not found: {label}"
        return result

    def _list_pins(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        if not self._pins:
            result.output = "No pinned items."
            return result

        lines = ["Pinned items:\n"]
        for p in self._pins:
            lines.append(f"  [{p['label']}] {p['content'][:100]}")

        result.output = '\n'.join(lines)
        return result

    def _add_to_scratchpad(self, content: str) -> ToolResult:
        result = ToolResult(tool_name=self.name)

        if not content:
            # Return current scratchpad
            if not self._scratchpad:
                result.output = "Scratchpad is empty."
            else:
                lines = ["Scratchpad:\n"]
                for i, note in enumerate(self._scratchpad, 1):
                    lines.append(f"  {i}. {note[:100]}")
                result.output = '\n'.join(lines)
            return result

        self._scratchpad.append(content)
        self._save()
        result.output = f"Added to scratchpad ({len(self._scratchpad)} notes total)"
        return result

    def _suggest_summarize(self) -> ToolResult:
        result = ToolResult(tool_name=self.name)
        result.output = (
            "To manage context, consider:\n"
            "1. Clear old conversation with 'clear' command in CLI\n"
            "2. Pin important facts before clearing: context_manager pin \"key fact\"\n"
            "3. Pinned items persist across conversation clears\n\n"
            "Current pins and scratchpad will be preserved."
        )
        return result

    def get_pinned_context(self) -> str:
        """Called by agent to get pinned context for system prompt"""
        if not self._pins:
            return ""

        lines = ["\n\nIMPORTANT CONTEXT (pinned):"]
        for p in self._pins:
            lines.append(f"- [{p['label']}]: {p['content']}")
        return '\n'.join(lines)
