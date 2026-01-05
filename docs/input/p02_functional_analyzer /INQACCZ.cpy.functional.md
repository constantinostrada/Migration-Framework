# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_copy/INQACCZ.cpy`
- **File Size**: 1,856 bytes
- **File Type**: .cpy
- **Analysis Date**: 2025-11-24 23:37:58
- **Confidence Score**: 0.90

## Functional Summary
The module defines a data structure for account inquiry operations, encapsulating customer and account information, including account type, interest rate, balance details, and statement dates.

## API-Like Specification
- **Function Name**: INQACC-COMMAREA
- **Inputs**:
  - INQACC-CUSTNO
  - INQACC-SCODE
  - INQACC-ACCNO
- **Outputs**:
  - INQACC-ACC-TYPE
  - INQACC-INT-RATE
  - INQACC-AVAIL-BAL
  - INQACC-ACTUAL-BAL

## Data Flow
- Step 1: Initialization of account inquiry data structure
- Step 2: Population of customer and account details
- Step 3: Output of account information for further processing

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:37:58.590360
