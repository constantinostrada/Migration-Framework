# Business Analysis Report

## File Information
- **File Path**: `src/base/cobol_src/BNK1DCS.cbl`
- **File Size**: 65,395 bytes
- **File Type**: .cbl
- **Analysis Date**: 2025-11-20 00:41:05
- **Confidence Score**: 0.85

## Business Summary
The program supports customer management processes within a banking application, allowing for the display, update, and deletion of customer records based on user input. It interacts with customer data to perform these operations.

## Business Entities
- Customer
- Customer Record
- Customer Address
- Customer Credit Score

## Business Rules
1. Customer number must be numeric and not zero or '9999999999'.
2. Customer name must start with a valid title such as Mr, Mrs, Miss, Ms, Dr, Professor, Drs, Lord, Sir, Lady.
3. Customer address must not be all spaces.
4. Sort code and customer number combination must be valid.

## Business Dependencies
- INQCUST
- DELCUS
- UPDCUST

## Business Workflows
- Display customer details when the program is initiated.
- Delete customer record when PF5 is pressed.
- Update customer record when PF10 is pressed.
- Return to main menu when PF3 is pressed.
- Send termination message when PF12 is pressed.

## Data Transformations
- Splitting and formatting of customer address and date of birth for processing.
- Conversion of customer credit score from character to numeric format.

## Error Handling
- Handles invalid key presses by displaying an error message.
- Handles customer not found scenarios by displaying an appropriate message.
- Handles data store errors during delete and update operations.

## Extracted Constants

### Business Constants
- Session Ended
- Invalid key pressed.
- Please enter a customer number.
- Customer lookup successful.
- Customer and associated accounts were successfully deleted.
- Customer was updated successfully.

### Validation Rules
- Customer number must be numeric.
- Valid titles are: Mr, Mrs, Miss, Ms, Dr, Professor, Drs, Lord, Sir, Lady.
- Address must not be all spaces.

## Analysis Metadata
- **Model Used**: openai/gpt-4o
- **Framework Version**: 1.0.0-openrouter
- **Program ID**: p01_business_analyzer
- **Analysis Timestamp**: 2025-11-20T00:41:05.389893
