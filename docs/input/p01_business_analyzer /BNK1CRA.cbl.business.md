# Business Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/BNK1CRA.cbl`
- **File Size**: 37,728 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-20 00:36:40
- **Confidence Score**: 0.85

## Business Summary
The program supports credit and debit transactions within a banking application. It handles user interactions, validates input data, and processes financial transactions by interfacing with other systems.

## Business Entities
- Customer
- Account
- Transaction

## Business Rules
1. Account number must be numeric and non-zero.
2. Amount must be numeric and can have up to two decimal places.
3. Sign must be '+' or '-' for credit or debit respectively.
4. Sufficient funds must be available for debit transactions.

## Business Dependencies
- CICS for transaction processing
- DBCRFUN subprogram for credit/debit operations
- BNK1CDM mapset for user interface

## Business Workflows
- User inputs are validated and processed for credit or debit transactions.
- Successful transactions update account balances and display confirmation.
- Error conditions trigger specific error messages and transaction rollback.

## Data Transformations
- Conversion of string input to numeric values for transaction amounts.
- Calculation of available and actual balances after transactions.

## Error Handling
- Invalid key presses result in error messages.
- Transaction failures due to insufficient funds or invalid data trigger specific error messages.
- CICS response codes are checked and handled for transaction failures.

## Extracted Constants

### Business Constants
- Session Ended
- Invalid key pressed.
- Amount successfully applied to the account.

### Validation Rules
- Account number must be numeric.
- Amount must be numeric with up to two decimal places.
- Sign must be '+' or '-'.

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p01_business_analyzer
- **Analysis Timestamp**: 2025-11-20T00:36:40.857768
