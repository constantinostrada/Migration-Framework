# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/GETCOMPY.cbl`
- **File Size**: 1,071 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-24 23:42:44
- **Confidence Score**: 0.90

## Functional Summary
The GETCOMPY module is a COBOL program designed to set a specific value, 'CICS Bank Sample Application', to the COMPANY-NAME field within the DFHCOMMAREA structure and then return control to the CICS environment.

## API-Like Specification
- **Function Name**: GETCOMPY
- **Inputs**:
  - DFHCOMMAREA
- **Outputs**:
  - COMPANY-NAME

## Data Flow
- Step 1: DFHCOMMAREA is passed as input to the PROCEDURE DIVISION.
- Step 2: The string 'CICS Bank Sample Application' is moved to COMPANY-NAME.
- Step 3: Control is returned to CICS with the EXEC CICS RETURN statement.

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:42:44.662176
