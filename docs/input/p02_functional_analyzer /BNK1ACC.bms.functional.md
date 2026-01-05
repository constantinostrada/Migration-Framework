# Functional Analysis Report

## File Information
- **File Path**: `src/base/bms_src/BNK1ACC.bms`
- **File Size**: 2,675 bytes
- **File Type**: .bms
- **Analysis Date**: 2025-11-24 23:38:10
- **Confidence Score**: 0.90

## Functional Summary
The BNK1ACC module is a CICS BMS map definition used to display account information for a given customer in a CICS Banking Sample Application. It provides a user interface for entering a customer number and displays account details such as sort code, account number, account type, available balance, and actual balance.

## API-Like Specification
- **Function Name**: BNK1ACC
- **Inputs**:
  - Customer number
- **Outputs**:
  - Account details including sort code, account number, account type, available balance, actual balance

## Data Flow
- Step 1: User inputs customer number
- Step 2: System retrieves account information for the customer
- Step 3: Account information is displayed on the screen

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:38:10.452434
