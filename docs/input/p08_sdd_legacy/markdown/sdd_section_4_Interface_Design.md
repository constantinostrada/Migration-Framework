# 4 Interface Design

## Introduction
This section documents the actual user and system interfaces implemented in the Legacy Banking System. It covers the design and implementation of user interfaces for customer account management and system interfaces for data processing and transaction handling.

## 4.1 User Interface Design
This subsection details the user interface components responsible for customer account interactions, including screen layouts, user input handling, and error management.

### BNK1CAC.cbl - Customer Account Inquiry and Update
- **Purpose**: Handles customer account inquiries and updates, processing user input from a CICS map.
- **Inputs**: EIBAID, BNK1CAO
- **Outputs**: MESSAGEO, WS-COMM-AREA
- **Key Features**:
  - Processes user input from CICS map
  - Handles navigation and error messages

### BNK1CCS.cbl - Customer Creation and Update
- **Purpose**: Manages customer creation and updates, validating input data and handling errors.
- **Inputs**: BNK1CCI
- **Outputs**: MESSAGEO, ABNDINFO-REC
- **Key Features**:
  - Validates customer data
  - Handles CICS map errors

## 4.2 System Interface Design
This subsection describes the system interfaces and APIs used for data exchange and transaction processing.

### BNK1UAC.cbl - User Account Management
- **Purpose**: Handles user account management, processing inquiries and updates via CICS maps.
- **Inputs**: EIBAID, COMM-EYE
- **Outputs**: BNK1UAO, ABNDINFO-REC
- **Key Features**:
  - Processes account-related transactions
  - Handles user commands and errors

## Summary
- **Key Decisions**: Use of CICS maps for user interface interactions, Structured error handling with ABEND procedures
- **Trade-offs**: Limited modernization due to COBOL and CICS constraints
- **Future Considerations**: Potential migration to modern UI frameworks

## Implementation
- **Development Guidance**:
  - Ensure CICS map definitions are up-to-date
  - Follow structured programming practices
  - Implement robust error handling
- **Testing Approach**: Conduct functional testing for user interfaces and system interfaces, focusing on input validation and error handling.
- **Deployment Notes**: Ensure CICS regions are configured correctly for deployment and that all mapsets are available.

## Modernization
- **Current Technology**: COBOL and CICS environment
- **Modernization Options**: Consider migrating to web-based interfaces, Explore API-based integrations for system interfaces
- **Refactoring Opportunities**: Simplify complex EVALUATE statements, Enhance error logging mechanisms