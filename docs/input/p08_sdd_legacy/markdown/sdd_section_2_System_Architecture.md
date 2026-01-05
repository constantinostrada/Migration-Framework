# 2 System Architecture

## Introduction
This section provides a comprehensive overview of the actual system architecture of the Legacy Banking System, detailing the high-level design, major components, and the technology stack in use.

## 2.1 Architectural Overview
This subsection describes the high-level system architecture, including the design patterns and system layers implemented in the Legacy Banking System.

### SYSARCH.CBL - Central Orchestrator
- **Purpose**: Manages the flow and interaction between major system components.
- **Source Files**: `/app/core/src/SYSARCH.CBL`
- **Key Features**: `INITIALIZE-SYSTEM-CONTEXT`, `DISPATCH-TRANSACTION-PROCESSOR`
- **Interfaces**: `WS-TRANSACTION-RECORD`, `WS-PROCESSED-TRANSACTION-STATUS`

## 2.2 System Components
This subsection details the major components of the system, their relationships, and dependencies.

### MASTER.JCL - Batch Processing Script
- **Purpose**: Defines the structure and execution sequence of the daily batch processing cycle.
- **Source Files**: `/app/batch/jcl/MASTER.JCL`
- **Key Features**: `DEFINE-JOB-STEPS`, `MANAGE-JOB-DEPENDENCIES`
- **Interfaces**: `INPUT-DATASETS`, `OUTPUT-DATASETS`

### DATADEF.CPY - Data Definition Copybook
- **Purpose**: Defines standard record layouts and data structures for core business entities.
- **Source Files**: `/app/common/copybooks/DATADEF.CPY`
- **Key Features**: `DEFINE-RECORD-STRUCTURES`, `SPECIFY-DATA-TYPES`

## 2.3 Technology Architecture
This subsection outlines the technology stack and platform architecture of the system.

### DBDSCHEM.DBD - IMS Database Description
- **Purpose**: Defines the physical and logical structure of a critical IMS database.
- **Source Files**: `/app/db/ims/DBDSCHEM.DBD`
- **Key Features**: `DEFINE-DATABASE-TYPE`, `DEFINE-SEGMENT-HIERARCHY`

### CONFIG.PLI - Configuration Management Program
- **Purpose**: Reads and parses system-wide configuration parameters.
- **Source Files**: `/app/sys/config/CONFIG.PLI`
- **Key Features**: `READ-CONFIGURATION-FILE`, `PARSE-PARAMETERS`
- **Interfaces**: `SYSIN`, `GLOBAL-CONFIGURATION-TABLE`

## 2.4 Deployment Architecture
This subsection describes the system deployment and runtime environment.

## 2.5 Performance Architecture
This subsection covers the performance characteristics and scalability design of the system.

## Summary
- **Key Decisions**: Centralized control for transaction processing, Batch processing architecture for end-of-day operations
- **Trade-offs**: Legacy constraints limit modernization efforts, Batch processing introduces latency but ensures data consistency
- **Future Considerations**: Potential migration to modern platforms, Refactoring opportunities for improved maintainability

## Implementation
- **Development Guidance**: Ensure compatibility with COBOL and CICS, Maintain data integrity across batch processes, Avoid hardcoding configuration parameters
- **Testing Approach**: Comprehensive testing of batch processes and transaction handling, including performance testing under load.
- **Deployment Notes**: Deployment requires careful configuration of JCL scripts and IMS databases, with attention to resource allocation and job dependencies.

## Modernization
- **Current Technology**: COBOL, CICS, IMS, JCL, PL/I
- **Modernization Options**: Consider migration to Java or .NET, Explore cloud-based database solutions
- **Refactoring Opportunities**: Modularize monolithic COBOL programs, Enhance error handling and logging mechanisms