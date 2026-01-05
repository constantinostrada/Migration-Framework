# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_copy/ACCTCTRL.cpy`
- **File Size**: 1,545 bytes
- **File Type**: .cpy
- **Analysis Date**: 2025-11-24 23:35:46
- **Confidence Score**: 0.80

## Functional Summary
The module defines a COBOL copybook structure for an account control record, which includes fields for identifying and managing account control data such as sort codes, account numbers, and status flags.

## API-Like Specification
- **Function Name**: ACCOUNT-CONTROL-RECORD
- **Outputs**:
  - ACCOUNT-CONTROL-EYE-CATCHER
  - ACCOUNT-CONTROL-KEY
  - NUMBER-OF-ACCOUNTS
  - LAST-ACCOUNT-NUMBER
  - ACCOUNT-CONTROL-SUCCESS-FLAG
  - ACCOUNT-CONTROL-FAIL-CODE

## Data Flow
- Step 1: Initialization of account control fields
- Step 2: Validation of eye-catcher value
- Step 3: Setting success or failure flags

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:35:46.239539
