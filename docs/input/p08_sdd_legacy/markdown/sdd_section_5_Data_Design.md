# 5 Data Design

## Introduction
This section provides a detailed description of the data design within the Legacy Banking System, focusing on the actual database schemas, data models, and data flow processes as implemented.

## Database Design

### DB2_CUSTOMER_MASTER.DDL
- **Purpose**: Defines the DB2 table, indexes, and storage for the Customer Master data, including customer demographics, address, and status information.
- **Source Files**: `/app/db2/ddl/DB2_CUSTOMER_MASTER.DDL`
- **Key Features**:
  - Table creation for Customer Master
  - Index creation for efficient data retrieval
  - Tablespace and storage group definition

### CUSTMAST.CPY
- **Purpose**: Standardized record layout for the Customer Master File/Table, used by COBOL programs for data access and manipulation.
- **Source Files**: `/app/cobol/copybooks/CUSTMAST.CPY`
- **Key Features**:
  - Defines field lengths and data types
  - Groups related data elements for customer records

## Data Flow Design

### DATAMIG.CBL
- **Purpose**: Migrates customer data from legacy flat files to the DB2 Customer Master table, including data transformation and cleansing.
- **Source Files**: `/app/cobol/programs/DATAMIG.CBL`
- **Key Features**:
  - Reads legacy customer data
  - Transforms and cleanses data
  - Inserts data into DB2 Customer Master

### PRDCUST01.CBL
- **Purpose**: Processes daily customer updates from flat files and applies them to the DB2 Customer Master table.
- **Source Files**: `/app/cobol/programs/PRDCUST01.CBL`
- **Key Features**:
  - Validates incoming customer data
  - Updates or inserts customer records
  - Logs errors for invalid transactions

## Summary
- **Key Decisions**: Use of DB2 for customer data storage, Batch processing for data migration and updates
- **Trade-offs**: Complexity of data transformation vs. data integrity, Batch processing latency vs. real-time updates
- **Future Considerations**: Potential migration to a more modern database system, Real-time data processing enhancements

## Implementation
- **Development Guidance**:
  - Ensure all data transformations adhere to business rules
  - Regularly review and update DDL scripts for schema changes
  - Monitor batch processing jobs for performance issues
- **Testing Approach**: Comprehensive testing of data migration and update processes, including validation of data integrity and error handling.
- **Deployment Notes**: Coordinate deployment of database changes with application updates to ensure compatibility.

## Modernization
- **Current Technology**: COBOL programs and DB2 database running on a mainframe environment.
- **Modernization Options**:
  - Consider migrating to a relational database with cloud support
  - Explore microservices architecture for data processing
- **Refactoring Opportunities**:
  - Refactor COBOL programs for improved maintainability
  - Optimize data transformation logic for performance