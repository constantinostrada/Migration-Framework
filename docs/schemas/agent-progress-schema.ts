/**
 * Agent Progress Schema - Clean Architecture Migration Framework v4.3
 *
 * Defines the structure for tracking agent progress independently.
 * Each implementation agent maintains its own progress file.
 *
 * Key changes in v4.3:
 * - Agents auto-assign tasks (no orchestrator assignment)
 * - Each agent has its own progress.json file
 * - Agents read tasks.json and claim ownership
 * - No FDD approval (autonomous workflow)
 */

// ============================================
// ENUMS
// ============================================

export type TaskProgressStatus =
  | "identified"      // Agent identified this task as theirs
  | "claimed"         // Agent claimed ownership
  | "in_progress"     // Currently implementing
  | "testing"         // Running tests
  | "completed"       // Successfully completed
  | "failed";         // Failed (needs review)

export type AgentRole =
  | "domain-agent"
  | "use-case-agent"
  | "infrastructure-agent";

// ============================================
// TASK PROGRESS ENTRY
// ============================================

export interface TaskProgressEntry {
  // Task ID from tasks.json
  task_id: string;

  // Agent that owns this task
  owner: AgentRole;

  // Current status in agent's workflow
  status: TaskProgressStatus;

  // When agent started working on this task
  started_at: string;

  // When agent completed this task
  completed_at: string | null;

  // Files created/modified by this task
  files_generated: string[];

  // Test results
  tests_passed: boolean | null;
  test_count?: number;
  test_failures?: number;
  test_coverage?: string;

  // Implementation notes (brief summary)
  notes: string;

  // Error message if failed
  error_message?: string;
}

// ============================================
// AGENT PROGRESS FILE
// ============================================

export interface AgentProgress {
  // Agent name
  agent_name: AgentRole;

  // Agent role description
  agent_role: string;

  // Last time this file was updated
  last_updated: string;

  // Total tasks owned by this agent
  total_tasks: number;

  // Tasks breakdown
  tasks_completed: number;
  tasks_in_progress: number;
  tasks_failed: number;

  // All tasks tracked by this agent
  tasks: TaskProgressEntry[];

  // Summary notes from agent
  summary?: string;
}

// ============================================
// EXAMPLE USAGE
// ============================================

/*
{
  "agent_name": "domain-agent",
  "agent_role": "Implements Domain Layer (entities, value objects, domain services)",
  "last_updated": "2026-01-02T11:30:00Z",
  "total_tasks": 3,
  "tasks_completed": 2,
  "tasks_in_progress": 1,
  "tasks_failed": 0,
  "tasks": [
    {
      "task_id": "TASK-CUSTOMER-PHASE2-001",
      "owner": "domain-agent",
      "status": "completed",
      "started_at": "2026-01-02T10:00:00Z",
      "completed_at": "2026-01-02T11:00:00Z",
      "files_generated": [
        "backend/app/domain/customer/entity.py",
        "backend/app/domain/customer/value_objects.py",
        "backend/app/domain/customer/services.py"
      ],
      "tests_passed": true,
      "test_count": 8,
      "test_failures": 0,
      "test_coverage": "95%",
      "notes": "Implemented Customer entity with UUID v4 ID. Credit score calculation uses simple formula (income > $2000). All 8 unit tests pass."
    },
    {
      "task_id": "TASK-CUSTOMER-PHASE2-002",
      "owner": "domain-agent",
      "status": "in_progress",
      "started_at": "2026-01-02T11:15:00Z",
      "completed_at": null,
      "files_generated": ["backend/app/domain/customer/validators.py"],
      "tests_passed": null,
      "notes": "Working on domain validators for customer data validation"
    }
  ],
  "summary": "Domain layer for Customer module: 2/3 tasks completed. Implemented core entities and value objects. All tests passing with 95% coverage."
}
*/
