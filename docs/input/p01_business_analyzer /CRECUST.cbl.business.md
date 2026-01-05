# Business Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/CRECUST.cbl`
- **File Size**: 49,194 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-20 00:41:21
- **Confidence Score**: 0.85

## Business Summary
The program processes customer information by determining the appropriate datastore (VSAM or DB2), performing credit checks with multiple agencies, and updating customer records. It handles customer data creation and transaction logging in a legacy system.

## Business Entities
- Customer
- Credit Score
- Transaction
- Datastore

## Business Rules
1. If no credit data is returned, set credit score to 0 and mark review date as today.
2. If customer data write fails, decrement and dequeue the named counter.
3. Date of birth must be valid and customer age must not exceed 150 years.

## Business Dependencies
- BMS application for customer data input
- VSAM and DB2 datastores for data storage
- Credit agencies for credit score checks

## Business Workflows
- Customer data retrieval and processing
- Credit score checking and aggregation
- Customer record creation and transaction logging

## Data Transformations
- Aggregation and averaging of credit scores
- Conversion of date formats for processing

## Error Handling
- Handles errors in credit check responses by setting default values and logging errors.
- Retries on system ID errors during datastore operations.
- Validates date of birth and handles invalid entries.

## Extracted Constants

### Business Constants
- SORTCODE
- CUSTOMER
- PROCTRAN

### Validation Rules
- COMM-BIRTH-YEAR must be greater than 1600
- Customer age must not exceed 150 years

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p01_business_analyzer
- **Analysis Timestamp**: 2025-11-20T00:41:21.303909
