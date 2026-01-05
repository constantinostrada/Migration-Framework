#!/usr/bin/env python3
"""
Unit tests for StateManager.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.state_manager import StateManager, Phase


class TestStateManager(unittest.TestCase):
    """Tests for StateManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_project(self):
        """Test creating a new project."""
        project_id = self.state_manager.create_project("Test Project")

        self.assertIsNotNone(project_id)
        self.assertTrue(project_id.startswith("test-project"))

        # Verify state file was created
        state = self.state_manager.get_project_state(project_id)
        self.assertIsNotNone(state)
        self.assertEqual(state["project_name"], "Test Project")
        self.assertEqual(state["current_phase"], "ANALYSIS")

    def test_set_active_project(self):
        """Test setting active project."""
        project_id = self.state_manager.create_project("Test Project")

        active_id = self.state_manager.get_active_project_id()
        self.assertEqual(active_id, project_id)

    def test_update_state(self):
        """Test updating project state."""
        project_id = self.state_manager.create_project("Test Project")

        self.state_manager.update_state({
            "last_action": "Test action",
            "progress": 25
        }, project_id)

        state = self.state_manager.get_project_state(project_id)
        self.assertEqual(state["last_action"], "Test action")
        self.assertEqual(state["progress"], 25)

    def test_advance_phase(self):
        """Test advancing to next phase."""
        project_id = self.state_manager.create_project("Test Project")

        # Initial phase should be ANALYSIS
        state = self.state_manager.get_project_state(project_id)
        self.assertEqual(state["current_phase"], "ANALYSIS")

        # Advance to FEEDBACK
        self.state_manager.advance_phase(project_id)
        state = self.state_manager.get_project_state(project_id)
        self.assertEqual(state["current_phase"], "FEEDBACK")
        self.assertEqual(state["phases_status"]["ANALYSIS"], "completed")

    def test_calculate_progress(self):
        """Test progress calculation."""
        project_id = self.state_manager.create_project("Test Project")

        # Complete ANALYSIS phase
        self.state_manager.update_state({
            "phases_status": {"ANALYSIS": "completed"},
            "phase_progress": {"ANALYSIS": 100}
        }, project_id)

        progress = self.state_manager.calculate_progress(project_id)
        self.assertGreater(progress, 0)

    def test_record_checkpoint(self):
        """Test checkpoint recording."""
        project_id = self.state_manager.create_project("Test Project")

        self.state_manager.record_checkpoint("test_trigger", project_id)

        state = self.state_manager.get_project_state(project_id)
        self.assertIsNotNone(state["last_checkpoint"])
        self.assertEqual(state["files_modified_since_checkpoint"], 0)

    def test_log_mcp_usage(self):
        """Test MCP usage logging."""
        project_id = self.state_manager.create_project("Test Project")

        self.state_manager.log_mcp_usage(
            mcp_name="context7",
            queries=["test query 1", "test query 2"],
            findings="Test findings",
            project_id=project_id
        )

        state = self.state_manager.get_project_state(project_id)
        self.assertEqual(len(state["mcp_usage_log"]), 1)
        self.assertEqual(state["mcp_usage_log"][0]["mcp"], "context7")

    def test_log_agent_invocation(self):
        """Test agent invocation logging."""
        project_id = self.state_manager.create_project("Test Project")

        self.state_manager.log_agent_invocation(
            agent_name="business-rules-analyzer",
            task="Extract rules",
            status="completed",
            deliverables=["rules.md", "rules.json"],
            project_id=project_id
        )

        state = self.state_manager.get_project_state(project_id)
        self.assertEqual(len(state["agent_invocations"]), 1)

    def test_add_remove_blocker(self):
        """Test blocker management."""
        project_id = self.state_manager.create_project("Test Project")

        # Add blocker
        self.state_manager.add_blocker("Test blocker", project_id)
        state = self.state_manager.get_project_state(project_id)
        self.assertIn("Test blocker", state["blockers"])

        # Remove blocker
        self.state_manager.remove_blocker("Test blocker", project_id)
        state = self.state_manager.get_project_state(project_id)
        self.assertNotIn("Test blocker", state["blockers"])

    def test_multiple_projects(self):
        """Test multiple project support."""
        project1 = self.state_manager.create_project("Project 1")
        project2 = self.state_manager.create_project("Project 2")

        # Both projects should exist
        projects = self.state_manager.get_projects()
        self.assertEqual(len(projects["projects"]), 2)

        # Active project should be the last created
        self.assertEqual(self.state_manager.get_active_project_id(), project2)

        # Can switch active project
        self.state_manager.set_active_project(project1)
        self.assertEqual(self.state_manager.get_active_project_id(), project1)


if __name__ == "__main__":
    unittest.main()
