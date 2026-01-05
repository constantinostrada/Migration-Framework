#!/usr/bin/env python3
"""
Framework Logger - Comprehensive logging for hooks, agents, and validation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class FrameworkLogger:
    """Centralized logging for the migration framework."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.log_dir = self.base_path / "docs" / "state" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self, log_type: str) -> Path:
        """Get the log file path for a specific log type."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"{log_type}-{today}.jsonl"

    def _write_log(self, log_type: str, entry: Dict[str, Any]):
        """Write a log entry."""
        entry["timestamp"] = datetime.now().isoformat()
        log_file = self._get_log_file(log_type)

        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def log_hook_execution(self, hook_name: str, trigger: str, result: str,
                           details: Optional[Dict] = None):
        """Log a hook execution."""
        self._write_log("hooks", {
            "hook": hook_name,
            "trigger": trigger,
            "result": result,  # "allow", "block", "warn"
            "details": details or {}
        })

    def log_mcp_usage(self, agent_name: str, mcp_name: str, queries: List[str],
                      findings_summary: str = "", phase: str = ""):
        """Log MCP usage by an agent."""
        self._write_log("mcp-usage", {
            "agent": agent_name,
            "mcp": mcp_name,
            "queries": queries,
            "findings_summary": findings_summary,
            "phase": phase,
            "query_count": len(queries)
        })

    def log_agent_invocation(self, agent_name: str, task: str, status: str,
                             deliverables: List[str] = None, duration_ms: int = 0,
                             error: str = None):
        """Log a sub-agent invocation."""
        self._write_log("agents", {
            "agent": agent_name,
            "task": task,
            "status": status,  # "started", "completed", "failed"
            "deliverables": deliverables or [],
            "duration_ms": duration_ms,
            "error": error
        })

    def log_validation(self, validation_type: str, entity: str, result: str,
                       mismatches: List[Dict] = None):
        """Log a validation result."""
        self._write_log("validations", {
            "type": validation_type,
            "entity": entity,
            "result": result,  # "pass", "fail", "warn"
            "mismatch_count": len(mismatches) if mismatches else 0,
            "mismatches": mismatches or []
        })

    def log_phase_transition(self, from_phase: str, to_phase: str, trigger: str,
                             deliverables_completed: List[str] = None):
        """Log a phase transition."""
        self._write_log("phases", {
            "from_phase": from_phase,
            "to_phase": to_phase,
            "trigger": trigger,
            "deliverables_completed": deliverables_completed or []
        })

    def log_checkpoint(self, trigger: str, phase: str, progress: int,
                       files_modified: int):
        """Log a checkpoint creation."""
        self._write_log("checkpoints", {
            "trigger": trigger,
            "phase": phase,
            "progress": progress,
            "files_modified_since_last": files_modified
        })

    def log_user_decision(self, decision_id: str, question: str, answer: str,
                          context: str = ""):
        """Log a user decision."""
        self._write_log("decisions", {
            "decision_id": decision_id,
            "question": question,
            "answer": answer,
            "context": context
        })

    def log_error(self, component: str, error_type: str, message: str,
                  stack_trace: str = None):
        """Log an error."""
        self._write_log("errors", {
            "component": component,
            "error_type": error_type,
            "message": message,
            "stack_trace": stack_trace
        })

    def get_recent_logs(self, log_type: str, limit: int = 50) -> List[Dict]:
        """Get recent log entries of a specific type."""
        log_file = self._get_log_file(log_type)

        if not log_file.exists():
            return []

        logs = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return logs[-limit:]

    def get_mcp_usage_summary(self, phase: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of MCP usage."""
        logs = self.get_recent_logs("mcp-usage", limit=1000)

        if phase:
            logs = [l for l in logs if l.get("phase") == phase]

        summary = {
            "total_invocations": len(logs),
            "by_mcp": {},
            "by_agent": {},
            "total_queries": 0
        }

        for log in logs:
            mcp = log.get("mcp", "unknown")
            agent = log.get("agent", "unknown")
            queries = log.get("query_count", 0)

            summary["by_mcp"][mcp] = summary["by_mcp"].get(mcp, 0) + 1
            summary["by_agent"][agent] = summary["by_agent"].get(agent, 0) + 1
            summary["total_queries"] += queries

        return summary

    def get_agent_summary(self, phase: Optional[str] = None) -> Dict[str, Any]:
        """Get a summary of agent invocations."""
        logs = self.get_recent_logs("agents", limit=1000)

        summary = {
            "total_invocations": len(logs),
            "by_agent": {},
            "by_status": {"completed": 0, "failed": 0, "started": 0},
            "total_deliverables": 0
        }

        for log in logs:
            agent = log.get("agent", "unknown")
            status = log.get("status", "unknown")
            deliverables = len(log.get("deliverables", []))

            if agent not in summary["by_agent"]:
                summary["by_agent"][agent] = {"invocations": 0, "completed": 0, "failed": 0}

            summary["by_agent"][agent]["invocations"] += 1
            if status in summary["by_status"]:
                summary["by_status"][status] += 1
                summary["by_agent"][agent][status] = summary["by_agent"][agent].get(status, 0) + 1

            summary["total_deliverables"] += deliverables

        return summary

    def generate_session_report(self) -> str:
        """Generate a human-readable session report."""
        checkpoint_logs = self.get_recent_logs("checkpoints", limit=10)
        agent_logs = self.get_recent_logs("agents", limit=20)
        mcp_logs = self.get_recent_logs("mcp-usage", limit=20)
        error_logs = self.get_recent_logs("errors", limit=10)

        report = f"""# Session Activity Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Checkpoints

"""
        for log in checkpoint_logs[-5:]:
            report += f"- [{log.get('timestamp', 'N/A')}] Phase: {log.get('phase')}, Progress: {log.get('progress')}%\n"

        report += "\n## Agent Invocations\n\n"
        for log in agent_logs[-10:]:
            status_emoji = "✅" if log.get('status') == "completed" else "❌" if log.get('status') == "failed" else "🔄"
            report += f"- {status_emoji} **{log.get('agent')}**: {log.get('task', 'N/A')}\n"

        report += "\n## MCP Usage\n\n"
        mcp_summary = self.get_mcp_usage_summary()
        for mcp, count in mcp_summary.get("by_mcp", {}).items():
            report += f"- **{mcp}**: {count} invocations\n"

        if error_logs:
            report += "\n## Errors\n\n"
            for log in error_logs[-5:]:
                report += f"- [{log.get('component')}] {log.get('message')}\n"

        return report
