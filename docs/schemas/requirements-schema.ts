/**
 * Requirements Schema - IEEE 29148-2018 Standard
 *
 * Defines the structure for functional and non-functional requirements
 * extracted from Software Design Documents (SDD).
 */

// ============================================
// ENUMS
// ============================================

export type Priority = "high" | "medium" | "low";

export type VerificationMethod =
  | "test"           // Automated testing
  | "inspection"     // Code review, manual check
  | "demonstration"  // User acceptance testing
  | "analysis";      // Static analysis, performance profiling

export type NFRCategory =
  | "performance"
  | "security"
  | "usability"
  | "reliability"
  | "maintainability"
  | "scalability"
  | "compatibility";

// ============================================
// FUNCTIONAL REQUIREMENT
// ============================================

export interface FunctionalRequirement {
  // Unique identifier (e.g., "FR-001")
  id: string;

  // Short descriptive title
  title: string;

  // Detailed description (should start with "The system shall...")
  description: string;

  // Module this requirement belongs to
  module: string;

  // Priority level
  priority: Priority;

  // Source from SDD (e.g., "3. Component Design - CRECUST.cbl")
  source: string;

  // Business rules enforced by this requirement (e.g., ["BR-CUST-001"])
  business_rules?: string[];

  // Testable acceptance criteria (1-3 bullet points)
  acceptance_criteria: string[];

  // How this requirement will be verified
  verification_method: VerificationMethod;

  // Related legacy components (for reference)
  related_legacy_components?: string[];

  // Estimated complexity (0.0 - 1.0)
  estimated_complexity: number;

  // Timestamp of creation
  created_at?: string;
}

// ============================================
// NON-FUNCTIONAL REQUIREMENT
// ============================================

export interface NonFunctionalRequirement {
  // Unique identifier (e.g., "NFR-001")
  id: string;

  // Short descriptive title
  title: string;

  // Detailed description (should start with "The system shall...")
  description: string;

  // Category of NFR
  category: NFRCategory;

  // Module this requirement applies to
  module: string;

  // Priority level
  priority: Priority;

  // Source from SDD
  source: string;

  // Testable acceptance criteria
  acceptance_criteria: string[];

  // How this requirement will be verified
  verification_method: VerificationMethod;

  // Related legacy components (for reference)
  related_legacy_components?: string[];

  // Estimated complexity (0.0 - 1.0)
  estimated_complexity: number;

  // Timestamp of creation
  created_at?: string;
}

// ============================================
// REQUIREMENTS COLLECTION
// ============================================

export interface RequirementsCollection {
  // Project name
  project_name: string;

  // SDD source
  sdd_source: string;

  // All functional requirements
  functional_requirements: FunctionalRequirement[];

  // All non-functional requirements
  non_functional_requirements: NonFunctionalRequirement[];

  // Total count
  total_fr: number;
  total_nfr: number;

  // Generation metadata
  generated_at: string;
  generated_by: string; // "sdd-analyzer"
}

// ============================================
// EXAMPLE USAGE
// ============================================

/*
{
  "project_name": "Legacy Banking System",
  "sdd_source": "docs/input/p08_sdd_legacy/legacy_sdd_complete.md",
  "functional_requirements": [
    {
      "id": "FR-001",
      "title": "Customer Creation with Credit Assessment",
      "description": "The system shall allow creation of new customer accounts with mandatory credit assessment validation",
      "module": "Customer",
      "priority": "high",
      "source": "3. Component Design - CRECUST.cbl",
      "business_rules": ["BR-CUST-001: Credit assessment required (score >= 700)"],
      "acceptance_criteria": [
        "Customer record is created in DB2_CUSTOMER_MASTER table",
        "Credit assessment is performed before account creation",
        "Unique customer ID is generated and validated",
        "Customer data includes: name, address, contact, credit score"
      ],
      "verification_method": "test",
      "related_legacy_components": ["CRECUST.cbl"],
      "estimated_complexity": 0.7,
      "created_at": "2026-01-01T10:00:00Z"
    }
  ],
  "non_functional_requirements": [
    {
      "id": "NFR-001",
      "title": "Transaction Processing Performance",
      "description": "The system shall process transactions within 2 seconds",
      "category": "performance",
      "module": "Transaction",
      "priority": "high",
      "source": "3. Component Design - DBCRFUN.cbl",
      "acceptance_criteria": [
        "95th percentile response time <= 2 seconds",
        "Support 1000 concurrent transactions",
        "No performance degradation under load"
      ],
      "verification_method": "test",
      "related_legacy_components": ["DBCRFUN.cbl"],
      "estimated_complexity": 0.8,
      "created_at": "2026-01-01T10:00:00Z"
    }
  ],
  "total_fr": 15,
  "total_nfr": 8,
  "generated_at": "2026-01-01T10:00:00Z",
  "generated_by": "sdd-analyzer"
}
*/
