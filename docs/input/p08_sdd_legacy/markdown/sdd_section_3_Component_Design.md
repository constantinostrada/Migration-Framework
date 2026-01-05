# 3 Component Design

## Introduction
This section provides a detailed design of individual system components within the Legacy Banking System. It covers the actual implementation details of customer management, account management, transaction processing, and utility components.

## Customer Management Components

### CRECUST.cbl - Customer Account Creation Program
- **Purpose**: Handles the creation of customer accounts, including credit assessment and data storage.
- **Inputs**: Customer details
- **Outputs**: Customer account records
- **Business Logic**: Ensures customer details are captured and stored securely with credit assessment.

### CUSTVAL.CBL - Customer Validation Program
- **Purpose**: Validates customer master data against business rules before updates or transactions.
- **Inputs**: WS-CUSTOMER-RECORD
- **Outputs**: WS-VALIDATION-STATUS
- **Business Logic**: Validates customer ID, address, and credit limit.

## Account Management Components

### CREACC.cbl - Account Creation Program
- **Purpose**: Facilitates the creation of new accounts for existing customers, enforcing account limits.
- **Inputs**: Existing customer ID
- **Outputs**: New account details
- **Business Logic**: Enforces a maximum of nine accounts per customer.

## Transaction Processing Components

### DBCRFUN.cbl - Transaction Processing Program
- **Purpose**: Handles transaction processing with compliance to banking regulations.
- **Inputs**: Transaction details
- **Outputs**: Processed transaction records
- **Business Logic**: Processes transactions within 2 seconds, supporting up to 1000 concurrent transactions.

## Utility and Support Components

### SYSUTIL.ASM - Utility Subroutine
- **Purpose**: Provides utility functions for date and time conversions.
- **Inputs**: Date values
- **Outputs**: Converted date formats
- **Business Logic**: Validates input dates for correctness.

## Summary
- **Key Decisions**: Use of COBOL for core processing, Assembler for performance-critical utilities
- **Trade-offs**: Legacy constraints vs. modernization needs
- **Future Considerations**: Potential migration to modern platforms

## Implementation
- **Development Guidance**: Adhere to existing COBOL standards, Ensure data integrity during processing
- **Testing Approach**: Unit and integration testing for all components
- **Deployment Notes**: Ensure compatibility with existing CICS environment

## Modernization
- **Current Technology**: COBOL, CICS, Assembler
- **Modernization Options**: Consider Java or .NET for new developments, Explore cloud-based solutions
- **Refactoring Opportunities**: Improve modularity, Enhance error handling mechanisms