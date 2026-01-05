# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_copy/ABNDINFO.cpy`
- **File Size**: 1,334 bytes
- **File Type**: .cpy
- **Analysis Date**: 2025-11-24 23:37:06
- **Confidence Score**: 0.90

## Functional Summary
The module defines a COBOL copybook structure for storing information related to system abends (abnormal ends). It includes fields for keys, application and transaction identifiers, timestamps, error codes, and a freeform text field.

## API-Like Specification
- **Function Name**: None
- **Inputs**:
  - ABND-VSAM-KEY
  - ABND-APPLID
  - ABND-TRANID
  - ABND-DATE
  - ABND-TIME
  - ABND-CODE
  - ABND-PROGRAM
  - ABND-RESPCODE
  - ABND-RESP2CODE
  - ABND-SQLCODE
  - ABND-FREEFORM

## Data Flow
- Step 1: Data is structured into a COBOL copybook format
- Step 2: Fields are populated with abend-related information

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:37:06.607245
