# Functional Analysis Report

## File Information
- **File Path**: `etc/install/base/buildjcl/BNK1MAI.jcl`
- **File Size**: 224 bytes
- **File Type**: .jcl
- **Analysis Date**: 2025-11-24 23:26:58
- **Confidence Score**: 0.90

## Functional Summary
The JCL script is used to compile and link-edit a BMS map named BNK1MAI. It includes a library order and a default member inclusion, and executes a procedure named MAPGEN with specific parameters.

## API-Like Specification
- **Function Name**: BNK1MAI
- **Inputs**:
  - PROC=MAPGEN
  - MEMBER=BNK1MAI
  - RMODE=ANY
  - OUTC='*'

## Data Flow
- Step 1: Include library order CBSA.CICSBSA.BUILDJCL
- Step 2: Include member DEFAULT
- Step 3: Execute MAPGEN procedure with parameters

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:26:58.132188
