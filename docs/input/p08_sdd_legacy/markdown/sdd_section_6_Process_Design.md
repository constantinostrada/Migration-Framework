# 6 Process Design

## Introduction
This section documents the actual design of business processes and workflows within the Legacy Banking System. It provides a detailed analysis of the existing business process designs, transaction flow designs, and the actual implementation of these processes in the legacy system.

## 6.1 Business Process Design
This subsection covers the design of business processes and operational workflows as implemented in the legacy system. It includes detailed descriptions of the components involved, their functionalities, and the business logic they implement.

### INQCUST.cbl - Customer Inquiry Program
- **Purpose**: Retrieves comprehensive customer details based on a provided customer identification number.
- **Inputs**: Customer number
- **Outputs**: OUTPUT-DATA structure, INQCUST-INQ-SUCCESS, INQCUST-INQ-FAIL-CD
- **Business Logic**: Validates customer number input, generates random customer numbers for special cases, retrieves last active customer number, queries and retrieves customer data from storage.

### INQACCCU.cbl - Account Inquiry Program
- **Purpose**: Retrieves all associated account records for a given customer by querying a DB2 database.
- **Inputs**: Customer number
- **Outputs**: RETURNED-DATA structure
- **Business Logic**: Validates customer number, uses DB2 cursor for account retrieval, fetches up to 20 account records per customer.

## 6.2 Transaction Flow Design
This subsection details the design of transaction processing flows, focusing on the actual implementation of transaction logic and validation rules.

### GETCOMPY.cbl - Company Name Utility Program
- **Purpose**: Sets a global company name variable for use within the CICS environment.
- **Outputs**: COMPANY-NAME variable in DFHCOMMAREA
- **Business Logic**: Sets company name to 'CICS Bank Sample Application', returns control to the calling program.

## Summary
- **Key Decisions**: Use of COBOL for business logic implementation, DB2 for data retrieval and storage.
- **Trade-offs**: Limited modernization due to COBOL and CICS constraints, complexity in handling special customer number cases.
- **Future Considerations**: Potential migration to modern programming languages, enhancements in data retrieval efficiency.

## Implementation
- **Development Guidance**: Ensure COBOL code adheres to existing standards, maintain clear documentation of business logic, avoid hardcoding values where possible.
- **Testing Approach**: Testing involves validating customer and account retrieval processes, ensuring correct handling of special cases and database interactions.
- **Deployment Notes**: Deployment requires careful configuration of CICS and DB2 environments to ensure compatibility with existing infrastructure.

## Modernization
- **Current Technology**: The system is built on a COBOL and CICS technology stack, with DB2 for database management.
- **Modernization Options**: Consider migrating to Java or .NET for improved maintainability, explore cloud-based database solutions for scalability.
- **Refactoring Opportunities**: Simplify business logic by reducing special case handling, improve error handling mechanisms.