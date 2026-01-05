# Functional Analysis Report

## File Information
- **File Path**: `src/base/bms_src/BNK1DCM.bms`
- **File Size**: 5,489 bytes
- **File Type**: .bms
- **Analysis Date**: 2025-11-24 23:39:17
- **Confidence Score**: 0.90

## Functional Summary
The BNK1DCM module is a BMS map definition for a CICS application that displays customer information. It is designed to interact with a 3270 terminal, allowing users to input a customer number and view associated customer details such as name, address, date of birth, and credit score.

## API-Like Specification
- **Function Name**: BNK1DCM
- **Inputs**:
  - CUSTOMER NUMBER
- **Outputs**:
  - Customer Name
  - Customer Address
  - Customer D.O.B.
  - Credit Score
  - CS Review Date

## Data Flow
- Step 1: User inputs CUSTOMER NUMBER
- Step 2: System retrieves customer details based on input
- Step 3: Customer details are displayed on the terminal

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:39:17.467182
