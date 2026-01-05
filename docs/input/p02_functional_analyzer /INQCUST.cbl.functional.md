# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/INQCUST.cbl`
- **File Size**: 22,784 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-24 23:39:43
- **Confidence Score**: 0.90

## Functional Summary
The INQCUST program retrieves customer information based on a provided customer number. It returns the customer data if found, or a record set to low values if not found. The program handles errors by issuing an appropriate abend.

## API-Like Specification
- **Function Name**: INQCUST
- **Inputs**:
  - INQCUST-CUSTNO
  - SORTCODE
- **Outputs**:
  - INQCUST-EYE
  - INQCUST-SCODE
  - INQCUST-CUSTNO
  - INQCUST-NAME
  - INQCUST-ADDR
  - INQCUST-DOB
  - INQCUST-CREDIT-SCORE
  - INQCUST-CS-REVIEW-DT

## Data Flow
- Initialize working storage variables
- Check if customer number is 0 or 9s and retrieve last customer number if needed
- Generate random customer number if required
- Read customer data from VSAM file
- Populate output commarea with customer data if found
- Handle errors and abends

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:39:43.406293
