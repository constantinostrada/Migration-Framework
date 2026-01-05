# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_copy/NEWCUSNO.cpy`
- **File Size**: 804 bytes
- **File Type**: .cpy
- **Analysis Date**: 2025-11-24 23:37:40
- **Confidence Score**: 0.90

## Functional Summary
This module defines a structure for handling customer number operations, including obtaining a new customer number, rolling back a transaction, and retrieving the current customer number.

## API-Like Specification
- **Function Name**: NEWCUSNO-FUNCTION
- **Inputs**:
  - NEWCUSNO-FUNCTION
- **Outputs**:
  - CUSTOMER-NUMBER
  - NEWCUSNO-SUCCESS
  - NEWCUSNO-FAIL-CODE

## Data Flow
- Step 1: Initialize NEWCUSNO-FUNCTION with a specific value ('G', 'R', 'C')
- Step 2: Based on the value, perform operations related to customer number
- Step 3: Set CUSTOMER-NUMBER, NEWCUSNO-SUCCESS, or NEWCUSNO-FAIL-CODE accordingly

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:37:40.845214
