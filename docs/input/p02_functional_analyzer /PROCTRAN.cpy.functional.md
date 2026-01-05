# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_copy/PROCTRAN.cpy`
- **File Size**: 5,728 bytes
- **File Type**: .cpy
- **Analysis Date**: 2025-11-24 23:35:10
- **Confidence Score**: 0.90

## Functional Summary
The module defines a COBOL copybook structure for processing transaction data. It includes fields for transaction identifiers, dates, times, references, types, descriptions, and amounts. The structure supports logical deletion and categorizes transactions into various types using condition names.

## API-Like Specification
- **Function Name**: PROC-TRAN-DATA
- **Inputs**:
  - PROC-TRAN-EYE-CATCHER
  - PROC-TRAN-ID
  - PROC-TRAN-DATE
  - PROC-TRAN-TIME
  - PROC-TRAN-REF
  - PROC-TRAN-TYPE
  - PROC-TRAN-DESC
  - PROC-TRAN-AMOUNT
- **Outputs**:
  - Processed transaction data structure

## Data Flow
- Step 1: Initialize transaction data structure
- Step 2: Populate fields with transaction details
- Step 3: Use condition names to interpret transaction types and logical deletion

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:35:10.502863
