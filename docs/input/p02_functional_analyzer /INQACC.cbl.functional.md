# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/INQACC.cbl`
- **File Size**: 33,042 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-24 23:41:18
- **Confidence Score**: 0.90

## Functional Summary
The INQACC program retrieves account information from a DB2 database based on an account number and sort code. It handles errors by abending if issues occur during database operations.

## API-Like Specification
- **Function Name**: INQACC
- **Inputs**:
  - INQACC-ACCNO
  - SORTCODE
- **Outputs**:
  - INQACC-EYE
  - INQACC-CUSTNO
  - INQACC-SCODE
  - INQACC-ACCNO
  - INQACC-ACC-TYPE
  - INQACC-INT-RATE
  - INQACC-OPENED
  - INQACC-OVERDRAFT
  - INQACC-LAST-STMT-DT
  - INQACC-NEXT-STMT-DT
  - INQACC-AVAIL-BAL
  - INQACC-ACTUAL-BAL

## Data Flow
- Step 1: Initialize OUTPUT-DATA and set up abend handling.
- Step 2: Retrieve account data from DB2 using a cursor if INQACC-ACCNO is not 99999999, otherwise retrieve the last account.
- Step 3: Populate the COMMAREA with retrieved account data or indicate failure.

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:41:18.647435
