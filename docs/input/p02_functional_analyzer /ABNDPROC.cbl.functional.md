# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/ABNDPROC.cbl`
- **File Size**: 5,911 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-24 23:40:28
- **Confidence Score**: 0.90

## Functional Summary
The ABNDPROC program processes application abends by writing them to a centralized VSAM KSDS datastore, allowing centralized viewing of abend records.

## API-Like Specification
- **Function Name**: ABNDPROC
- **Inputs**:
  - DFHCOMMAREA
- **Outputs**:
  - WS-ABND-AREA

## Data Flow
- Step 1: DFHCOMMAREA is received as input
- Step 2: DFHCOMMAREA is moved to WS-ABND-AREA
- Step 3: WS-ABND-AREA is written to the ABNDFILE VSAM datastore

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:40:28.933478
