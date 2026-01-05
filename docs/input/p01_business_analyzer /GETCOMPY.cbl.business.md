# Business Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/GETCOMPY.cbl`
- **File Size**: 1,071 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-20 00:40:24
- **Confidence Score**: 0.90

## Business Summary
The program GETCOMPY is part of a CICS Bank Sample Application and appears to set the company name within a CICS transaction context. It primarily handles the movement of a static string to a variable and returns control to CICS.

## Business Entities
- COMPANY-NAME

## Business Rules
None identified

## Business Dependencies
- CICS

## Business Workflows
- Setting company name in a CICS transaction

## Data Transformations
- Move 'CICS Bank Sample Application' to COMPANY-NAME

## Extracted Constants

### Business Constants
- CICS Bank Sample Application

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p01_business_analyzer
- **Analysis Timestamp**: 2025-11-20T00:40:24.038703
