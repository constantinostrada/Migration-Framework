# Functional Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/BNKMENU.cbl`
- **File Size**: 42,448 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-24 23:42:18
- **Confidence Score**: 0.90

## Functional Summary
The BNKMENU program is the initial entry point for a banking menu system. It displays a menu map to the user, processes user input to select various banking operations, validates the input, and initiates corresponding transactions. It handles different user actions such as entering data, pressing function keys, and terminating the session.

## API-Like Specification
- **Function Name**: BNKMENU
- **Inputs**:
  - User input from map
  - CICS response codes
- **Outputs**:
  - Transaction initiation
  - Error messages

## Data Flow
- Step 1: Initialize CICS work area and response codes
- Step 2: Display menu map and receive user input
- Step 3: Validate input and initiate corresponding transaction
- Step 4: Handle errors and send appropriate messages

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p02_functional_analyzer
- **Analysis Timestamp**: 2025-11-24T23:42:18.003869
