# Functional Analysis Report

## File Information
- **File Path**: `src/base/bms_src/BNK1CAM.bms`
- **File Size**: 5,857 bytes
- **File Type**: .bms
- **Analysis Date**: 2025-11-24 23:38:17
- **Confidence Score**: 0.90

## Functional Summary
The BNK1CAM module is a BMS map definition for a CICS Banking Sample Application. It facilitates the creation of a new account for an existing customer by providing a user interface for data entry on a 3270 terminal.

## API-Like Specification
- **Function Name**: BNK1CAM
- **Inputs**:
  - Customer number
  - Account Type
  - Interest Rate
  - Overdraft Limit
- **Outputs**:
  - Account number
  - Sort code
  - Account Opened Date
  - Last Statement Date
  - Next Statement Date
  - Available Balance
  - Actual Balance

## Data Flow
- Step 1: User inputs Customer number, Account Type, Interest Rate, and Overdraft Limit.
- Step 2: System processes the input data to create a new account.
- Step 3: Outputs such as Account number, Sort code, and balance details are displayed.

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:38:17.299418
