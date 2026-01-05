# 8 Operational Design

## Introduction
This section provides a detailed description of the operational design of the Legacy Banking System, focusing on the actual deployment, monitoring, and maintenance procedures implemented. It covers the deployment procedures, monitoring tools, and maintenance plans that are currently in place within the system.

## 8.1 Deployment Procedures
This subsection details the actual deployment and release management processes implemented in the Legacy Banking System.

### OPR_PLAN.CBL - Operational Planning Program
- **Purpose**: Manages scheduling and resource allocation for daily operational tasks.
- **Source Files**: `/app/legacy/programs/OPR_PLAN.CBL`
- **Key Features**:
  - Read operational task definitions
  - Allocate resources to tasks
  - Generate daily/weekly operational schedules
- **Interfaces**:
  - Input: `OPR_TASK_DEF_FILE`
  - Output: `DAILY_SCHEDULE_FILE`

### PROC_MGR.CBL - Procedure Management Program
- **Purpose**: Stores, retrieves, and validates standard operating procedures.
- **Source Files**: `/app/legacy/programs/PROC_MGR.CBL`
- **Key Features**:
  - Store new procedure definitions
  - Retrieve procedures by ID or type
  - Validate procedure step sequences
- **Interfaces**:
  - Input: `PROC_DEFINITION_INPUT`
  - Output: `PROC_MASTER_FILE`

## 8.2 Monitoring and Maintenance
This subsection describes the system monitoring and maintenance procedures currently implemented.

### MAINT_SCHD.JCL - Maintenance Scheduling Script
- **Purpose**: Automates execution of routine system maintenance jobs.
- **Source Files**: `/app/legacy/jcl/MAINT_SCHD.JCL`
- **Key Features**:
  - Define and execute job steps for maintenance tasks
  - Specify execution order and dependencies
  - Allocate system resources
- **Interfaces**:
  - Input: System parameters
  - Output: Job completion status

### INCIDENT_RPT.CBL - Incident Reporting Program
- **Purpose**: Processes and stores incident reports related to operational failures.
- **Source Files**: `/app/legacy/programs/INCIDENT_RPT.CBL`
- **Key Features**:
  - Receive and validate incident data
  - Assign unique incident IDs
  - Generate incident summary reports
- **Interfaces**:
  - Input: `INCIDENT_INPUT_FILE`
  - Output: `INCIDENT_MASTER_FILE`

## Summary
- **Key Decisions**: Use of COBOL and JCL for operational task management and maintenance.
- **Trade-offs**: Reliance on legacy technologies limits modernization but ensures stability and compliance with existing processes.
- **Future Considerations**: Consider migrating to more modern scheduling and maintenance tools to improve efficiency and reduce operational overhead.

## Implementation
- **Development Guidance**: Ensure all operational tasks are defined with clear dependencies and resource requirements.
- **Testing Approach**: Testing involves validating the scheduling and maintenance processes through simulated operational scenarios and verifying output files.
- **Deployment Notes**: Deployment requires careful coordination to ensure minimal disruption to ongoing operations, with a focus on off-peak hours.

## Modernization
- **Current Technology**: The system operates within a COBOL and CICS environment, utilizing JCL for batch processing.
- **Modernization Options**: Consider transitioning to a modern scheduling platform like Apache Airflow.
- **Refactoring Opportunities**: Refactor COBOL programs to improve readability and maintainability.