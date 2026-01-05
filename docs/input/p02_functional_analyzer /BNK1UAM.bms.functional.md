# Functional Analysis Report

## File Information
- **File Path**: `src/base/bms_src/BNK1UAM.bms`
- **File Size**: 6,450 bytes
- **File Type**: .bms
- **Analysis Date**: 2025-11-24 23:39:11
- **Confidence Score**: 0.90

## Functional Summary
The BNK1UAM module is a BMS map definition for a CICS Banking Sample Application. It is designed to update account information by providing a user interface for inputting and displaying account details such as account number, customer number, sort code, account type, interest rate, overdraft limit, and balance information.

## API-Like Specification
- **Function Name**: BNK1UAM
- **Inputs**:
  - ACCOUNT NUMBER
  - Account Type
  - Interest Rate
  - Overdraft Limit
- **Outputs**:
  - Customer Number
  - Sort Code
  - Account Number
  - Account Opened Date
  - Last Statement Date
  - Next Statement Date
  - Available Balance
  - Actual Balance

## Data Flow
- Step 1: User inputs account number and other editable fields
- Step 2: System retrieves and displays associated account information
- Step 3: User updates fields and submits changes

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:39:11.678930
