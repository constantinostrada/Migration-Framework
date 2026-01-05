# 9 Implementation Details

## Introduction
This section provides a detailed account of the technical specifics and configuration details of the Legacy Banking System. It covers the actual technology stack, configurations, constraints, and limitations as implemented in the system.

## 9.1 Technology Specifics
This subsection details the technology stack and configurations used in the Legacy Banking System, including specific programs and their functionalities.

### MavenWrapperDownloader.java - Java Program
- **Purpose**: Responsible for downloading the Maven Wrapper JAR file, managing the setup of the Maven build environment.
- **Source Files**: `.mvn/wrapper/MavenWrapperDownloader.java`
- **Key Features**:
  - Reads configuration from maven-wrapper.properties
  - Determines download URL (default or custom)
- **Interfaces**:
  - Command line argument (base directory for the project)
  - maven-wrapper.properties file (optional, for custom URL)

### BNK1DAC.cbl - COBOL Program
- **Purpose**: Handles the display of account information and facilitates account deletion within the CICS environment.
- **Source Files**: `src/base/cobol_src/BNK1DAC.cbl`
- **Key Features**:
  - Receives and validates CICS terminal input
  - Displays account details on a BMS map
- **Interfaces**:
  - CICS terminal input
  - DFHCOMMAREA for inter-program communication

### GETCOMPY.cbl - COBOL Program
- **Purpose**: Provides a standardized company name string to calling programs within the CICS environment.
- **Source Files**: `src/base/cobol_src/GETCOMPY.cbl`
- **Key Features**:
  - Sets the COMPANY-NAME field in the DFHCOMMAREA
- **Interfaces**:
  - Implicit call from a parent CICS program

## 9.2 Constraints and Limitations
This subsection outlines the design constraints and system limitations inherent in the Legacy Banking System.

### COBOL and CICS Environment - Legacy Constraint
- **Description**: The system operates within a COBOL and CICS environment, limiting modernization efforts.
- **Source Files**: All components
- **Key Features**:
  - COBOL and CICS impose constraints on modernization
  - Legacy technology stack
- **Interfaces**:
  - CICS transaction processing

## Summary
- **Key Decisions**:
  - Continued use of COBOL and CICS due to existing infrastructure
  - Standardization of company name across applications
- **Trade-offs**:
  - Maintaining legacy systems limits modernization but ensures stability
  - Use of procedural programming limits flexibility but ensures compatibility
- **Future Considerations**:
  - Potential migration to modern platforms
  - Refactoring opportunities to improve code quality

## Implementation
- **Development Guidance**:
  - Maintain existing COBOL and CICS standards
  - Ensure compatibility with legacy systems
  - Avoid introducing new dependencies that are not supported by the current environment
- **Testing Approach**: Testing is primarily manual, focusing on transaction processing and data integrity checks.
- **Deployment Notes**: Deployment requires careful coordination with existing CICS transaction schedules and database updates.

## Modernization
- **Current Technology**: The system uses COBOL, CICS, and Java for specific components.
- **Modernization Options**:
  - Consider migrating to a microservices architecture
  - Evaluate cloud-based solutions for scalability
- **Refactoring Opportunities**:
  - Simplify complex COBOL logic
  - Enhance error handling mechanisms