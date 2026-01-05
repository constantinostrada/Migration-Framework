/**
 * Tasks Schema - Clean Architecture Migration Framework
 *
 * Defines the structure for atomic, executable tasks that guide
 * AI agents through the implementation of a migration project.
 *
 * This schema supports:
 * - Clean Architecture (Domain, Application, Infrastructure layers)
 * - TDD (Test-Driven Development)
 * - Traceability (FR/NFR → Task → Code → Tests)
 * - Multi-agent coordination
 */

// ============================================
// ENUMS
// ============================================

export type TaskType =
  | "analysis"          // SDD analysis
  | "contracts"         // OpenAPI, TypeScript, SQL generation
  | "tests"             // Test generation (TDD)
  | "implementation"    // Code implementation
  | "e2e_testing"       // E2E testing and validation
  | "ui_design"         // UI design research (shadcn-ui-agent)
  | "deployment";       // Deployment and configuration

export type TaskStatus =
  | "pending"           // Not started
  | "in_progress"       // Currently being worked on
  | "blocked"           // Blocked by dependencies or errors
  | "completed"         // Successfully completed
  | "failed";           // Failed (needs review)

export type Priority = "high" | "medium" | "low";

export type ImplementationLayer =
  | "domain"                    // Domain layer (entities, value objects, domain services)
  | "application"               // Application layer (use cases, DTOs, interfaces)
  | "use_case"                  // Alias for application (backward compatibility)
  | "infrastructure_backend"    // Infrastructure layer - Backend (ORM, API, repositories)
  | "infrastructure_frontend"   // Infrastructure layer - Frontend (Next.js, React, UI)
  | "cross_layer"               // Spans multiple layers
  | null;                       // Not applicable (e.g., analysis tasks)

export type AgentRole =
  | "orchestrator"
  | "sdd-analyzer"
  | "qa-test-generator"
  | "domain-agent"
  | "use-case-agent"
  | "infrastructure-agent"
  | "shadcn-ui-agent"
  | "e2e-qa-agent"
  | null;  // No owner yet (pending auto-assignment)

export type TestScenario =
  | "happy_path"        // Normal flow, everything works
  | "error_case"        // Error handling
  | "edge_case"         // Edge cases and boundaries
  | "boundary"          // Boundary value testing
  | "business_rule";    // Business rule validation

// ============================================
// TEST SPECIFICATIONS (TDD)
// ============================================

export interface TestCase {
  // Test name (e.g., "test_create_customer_success")
  name: string;

  // Type of scenario
  scenario: TestScenario;

  // Description of what is being tested
  description: string;

  // Arrange: Setup instructions
  arrange: string;

  // Act: Action to perform
  act: string;

  // Assert: Expected outcome
  assert: string;
}

export interface UnitTestSpec {
  // Path to test file (e.g., "tests/unit/domain/test_customer.py")
  file_path: string;

  // Test cases for this file
  test_cases: TestCase[];

  // Mocks required (e.g., ["Session", "uuid4"])
  mocks_required?: string[];
}

export interface IntegrationTestSpec {
  // Path to test file
  file_path: string;

  // Test cases
  test_cases: TestCase[];

  // Dependencies required (e.g., ["test_database", "api_client"])
  dependencies_required?: string[];
}

export interface E2ETestSpec {
  // Path to Playwright test file
  file_path: string;

  // Test cases (user flows)
  test_cases: TestCase[];

  // Pages/components involved
  pages_involved?: string[];
}

export interface TestStrategy {
  // Unit tests (domain, application logic)
  unit_tests: UnitTestSpec[];

  // Integration tests (API, database)
  integration_tests: IntegrationTestSpec[];

  // E2E tests (full user flows)
  e2e_tests?: E2ETestSpec[];

  // Target code coverage (e.g., 0.90 = 90%)
  coverage_target: number;
}

// ============================================
// LAYER DEPENDENCIES
// ============================================

export interface LayerDependencies {
  // Task IDs from domain layer this task depends on
  domain?: string[];

  // Task IDs from use_case layer this task depends on
  use_case?: string[];

  // Task IDs from infrastructure layer this task depends on
  infrastructure?: string[];
}

// ============================================
// EXECUTION METRICS
// ============================================

export interface ExecutionMetrics {
  // Actual time spent on task
  actual_time_spent?: string;

  // Number of tests generated
  tests_generated?: number;

  // Number of tests passed
  tests_passed?: number;

  // Number of tests failed
  tests_failed?: number;

  // E2E test iterations run
  e2e_iterations?: number;

  // E2E test pass rate (0.0 - 1.0)
  e2e_pass_rate?: number;

  // Lines of code written
  lines_of_code?: number;

  // Files created/modified
  files_modified?: number;
}

// ============================================
// TASK CONTRACT
// ============================================

export interface Task {
  // ============================================
  // BASIC INFORMATION
  // ============================================

  // Unique task ID (e.g., "TASK-003-DOMAIN")
  id: string;

  // Short title (e.g., "Create Customer Domain Entity")
  title: string;

  // Detailed description with explicit instructions
  // Should include: file paths, function names, exact structures
  description: string;

  // Type of task
  type: TaskType;

  // Module this task belongs to (e.g., "Customer", "Account")
  module: string;

  // Phase in the migration process (e.g., "PHASE-02-Core")
  phase: string;

  // Priority
  priority: Priority;

  // ============================================
  // CLEAN ARCHITECTURE
  // ============================================

  // Which architectural layer this task implements
  implementation_layer: ImplementationLayer;

  // Execution order within its layer (1, 2, 3...)
  execution_order?: number;

  // Dependencies on other layers
  layer_dependencies?: LayerDependencies;

  // ============================================
  // AGENT OWNERSHIP (v4.3 - Auto-Assignment)
  // ============================================

  // Agent that owns this task (auto-assigned by agent, not orchestrator)
  // null = pending auto-assignment, agent will claim ownership
  owner: AgentRole;

  // Current status
  status: TaskStatus;

  // ============================================
  // DEPENDENCIES AND TRACEABILITY
  // ============================================

  // Task IDs that must be completed before this one
  dependencies: string[];

  // Related functional/non-functional requirements (e.g., ["FR-001", "NFR-002"])
  related_requirements: string[];

  // Business rules implemented (e.g., ["BR-CUST-001: Credit score >= 700"])
  business_rules?: string[];

  // ============================================
  // TDD - TEST SPECIFICATIONS
  // ============================================

  // Comprehensive test strategy (added by qa-test-generator)
  test_strategy?: TestStrategy;

  // Acceptance criteria for completion
  acceptance_criteria?: string[];

  // Commands to validate implementation
  validation_commands?: string[];

  // ============================================
  // DELIVERABLES
  // ============================================

  // Files that will be created/modified
  deliverables: string[];

  // ============================================
  // ESTIMATION
  // ============================================

  // Estimated time to complete (e.g., "45 minutes")
  effort_estimate: string;

  // Estimated complexity (0.0 - 1.0)
  estimated_complexity?: number;

  // Skills required (e.g., ["Python", "FastAPI", "DDD"])
  skills_required: string[];

  // ============================================
  // EXECUTION STATE
  // ============================================

  // When task was created
  created_at: string;

  // When task started
  started_at?: string;

  // When task completed
  completed_at?: string;

  // Execution metrics
  execution_metrics?: ExecutionMetrics;

  // Error message if failed
  error_message?: string;

  // Notes from agent execution
  execution_notes?: string;
}

// ============================================
// TASK COLLECTION
// ============================================

export interface TaskCollection {
  // Project name
  project_name: string;

  // Framework version
  framework_version: string;

  // Total number of tasks
  total_tasks: number;

  // All tasks
  tasks: Task[];

  // Generation metadata
  generated_at: string;
  generated_by: string; // "orchestrator"

  // Execution summary
  summary?: {
    pending: number;
    in_progress: number;
    completed: number;
    failed: number;
    blocked: number;
  };
}

// ============================================
// EXAMPLE USAGE
// ============================================

/*
{
  "project_name": "Legacy Banking System",
  "framework_version": "4.1-clean-arch",
  "total_tasks": 18,
  "tasks": [
    {
      "id": "TASK-003-DOMAIN",
      "title": "Create Customer Domain Entity",
      "description": "Create domain/entities/customer.py with Customer entity...",
      "type": "implementation",
      "module": "Customer",
      "phase": "PHASE-02-Core",
      "priority": "high",
      "implementation_layer": "domain",
      "execution_order": 1,
      "owner": "domain-agent",
      "status": "completed",
      "dependencies": ["TASK-001", "TASK-002"],
      "layer_dependencies": {},
      "related_requirements": ["FR-001", "FR-002"],
      "business_rules": ["BR-CUST-001: Credit score >= 700"],
      "test_strategy": {
        "unit_tests": [
          {
            "file_path": "tests/unit/domain/test_customer_entity.py",
            "test_cases": [
              {
                "name": "test_customer_creation_valid",
                "scenario": "happy_path",
                "description": "Should create customer with valid data",
                "arrange": "Valid customer data with credit_score=750",
                "act": "Customer.create(...)",
                "assert": "Customer created, can_open_account() returns True"
              }
            ],
            "mocks_required": []
          }
        ],
        "integration_tests": [],
        "coverage_target": 0.90
      },
      "acceptance_criteria": [
        "Customer entity has NO framework dependencies",
        "Business rule BR-CUST-001 enforced",
        "Unit tests pass 100%"
      ],
      "validation_commands": [
        "pytest tests/unit/domain/test_customer_entity.py -v"
      ],
      "deliverables": [
        "backend/app/domain/entities/customer.py",
        "backend/app/domain/value_objects/email.py",
        "backend/app/domain/value_objects/credit_score.py"
      ],
      "effort_estimate": "30 minutes",
      "estimated_complexity": 0.6,
      "skills_required": ["Python", "DDD", "Clean Architecture"],
      "created_at": "2026-01-01T10:00:00Z",
      "started_at": "2026-01-01T10:15:00Z",
      "completed_at": "2026-01-01T10:45:00Z",
      "execution_metrics": {
        "actual_time_spent": "30 minutes",
        "tests_generated": 5,
        "tests_passed": 5,
        "tests_failed": 0,
        "lines_of_code": 120,
        "files_modified": 3
      }
    }
  ],
  "generated_at": "2026-01-01T10:00:00Z",
  "generated_by": "orchestrator",
  "summary": {
    "pending": 5,
    "in_progress": 1,
    "completed": 10,
    "failed": 0,
    "blocked": 0
  }
}
*/
