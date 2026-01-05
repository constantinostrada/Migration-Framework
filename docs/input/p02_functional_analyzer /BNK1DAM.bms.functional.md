# Functional Analysis Report

## File Information
- **File Path**: `src/base/bms_src/BNK1DAM.bms`
- **File Size**: 6,061 bytes
- **File Type**: .bms
- **Analysis Date**: 2025-11-24 23:38:05
- **Confidence Score**: 0.80

## Functional Summary
The BNK1DAM module is a CICS BMS mapset designed to display account information for a banking application. It provides a user interface for entering an account number and displays various account details such as customer number, sort code, account type, interest rate, account opening date, overdraft limit, last and next statement dates, available balance, and actual balance.

## API-Like Specification
- **Function Name**: BNK1DAM
- **Inputs**:
  - ACCOUNT NUMBER
- **Outputs**:
  - Customer Number
  - Sort Code
  - Account Number
  - Account Type
  - Interest Rate
  - Account Opened Date
  - Overdraft Limit
  - Last Statement Date
  - Next Statement Date
  - Available Balance
  - Actual Balance

## Data Flow
- Step 1: User inputs account number
- Step 2: System retrieves account details from database
- Step 3: Account details are displayed on the screen

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:38:05.026308
