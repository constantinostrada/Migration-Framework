# Functional Analysis Report

## File Information
- **File Path**: `src/base/bms_src/BNK1CCM.bms`
- **File Size**: 6,691 bytes
- **File Type**: .bms
- **Analysis Date**: 2025-11-24 23:38:25
- **Confidence Score**: 0.90

## Functional Summary
The BNK1CCM module is a BMS map definition for a CICS Banking Sample Application. It is designed to create a new customer by capturing customer details such as name, address, date of birth, and other related information through a 3270 terminal interface.

## API-Like Specification
- **Function Name**: BNK1CCM
- **Inputs**:
  - Customer Title
  - First Name
  - Middle Initials
  - Family Name
  - Customer Address Line 1
  - Customer Address Line 2
  - Customer Address Line 3
  - Customer Date of Birth
  - Sort Code
  - Customer Number
  - Credit Score
  - Credit Score Review Date
- **Outputs**:
  - Confirmation message
  - Error message

## Data Flow
- Step 1: User inputs customer details via 3270 terminal
- Step 2: Data is captured in unprotected fields for processing
- Step 3: Outputs are displayed as messages on the terminal

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:38:25.003873
