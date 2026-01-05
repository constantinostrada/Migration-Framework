#!/usr/bin/env python3
"""
Test Specification Enrichment Script
Enriches all implementation tasks in tasks.json with comprehensive test specifications.
"""

import json
from datetime import datetime
from typing import Dict, List, Any

# Load user decisions for business rules
USER_DECISIONS = {
    "credit_score_min": 650,
    "credit_score_formula": "(income - debt) / income * 850",
    "transaction_types": ["DEBIT", "CREDIT"],
    "password_hash": "bcrypt",
    "bcrypt_work_factor": 12,
    "session_timeout_minutes": 15,
    "overdraft_allowed": False,
    "retry_strategy": "no_automatic_retry",
    "encryption_algorithm": "AES-256-GCM",
    "max_accounts_per_customer": 9,
    "account_query_limit": 20
}

def get_domain_test_strategy(task: Dict[str, Any], module: str, business_rules: List[str]) -> Dict[str, Any]:
    """Generate test strategy for domain layer tasks."""

    strategies = {
        "Customer": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/domain/entities/test_customer.py",
                    "test_cases": [
                        {
                            "name": "test_create_customer_with_valid_data",
                            "scenario": "happy_path",
                            "description": "Should create customer entity with valid data and calculate credit score",
                            "arrange": f"Prepare valid customer data: name='John Doe', email='john@example.com', monthly_income=5000, total_debt=1000 (credit score = {USER_DECISIONS['credit_score_formula']} = 680)",
                            "act": "customer = Customer.create(customer_data)",
                            "assert": "Customer created successfully, credit_score=680, status='PENDING', can_activate() returns True (score >= 650)",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-001", "BR-CUST-004"]
                        },
                        {
                            "name": "test_customer_credit_score_below_minimum",
                            "scenario": "business_rule",
                            "description": f"Should reject customer with credit score < {USER_DECISIONS['credit_score_min']} (BR-CUST-001)",
                            "arrange": f"Create customer with monthly_income=3000, total_debt=2500 (credit score = 142)",
                            "act": "result = customer.can_activate()",
                            "assert": f"Returns False because score 142 < {USER_DECISIONS['credit_score_min']}",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-001"]
                        },
                        {
                            "name": "test_customer_credit_score_exactly_minimum",
                            "scenario": "boundary",
                            "description": f"Should accept customer with credit score exactly {USER_DECISIONS['credit_score_min']}",
                            "arrange": f"Create customer with income/debt ratio that results in exactly {USER_DECISIONS['credit_score_min']} score",
                            "act": "result = customer.can_activate()",
                            "assert": "Returns True, score meets minimum threshold",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-001"]
                        },
                        {
                            "name": "test_customer_credit_score_maximum_value",
                            "scenario": "boundary",
                            "description": "Should handle maximum credit score (850)",
                            "arrange": "Create customer with monthly_income=10000, total_debt=0 (perfect score = 850)",
                            "act": "customer = Customer.create(customer_data)",
                            "assert": "Customer created with credit_score=850",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-001"]
                        },
                        {
                            "name": "test_customer_duplicate_email",
                            "scenario": "error_case",
                            "description": "Should enforce unique email constraint (BR-CUST-003)",
                            "arrange": "Create first customer with email='john@example.com', then attempt to create second customer with same email",
                            "act": "Customer.create(customer_data_with_duplicate_email)",
                            "assert": "Raises DuplicateEmailError with message 'Email already exists'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-003"]
                        },
                        {
                            "name": "test_customer_invalid_email_format",
                            "scenario": "error_case",
                            "description": "Should validate email format (BR-CUST-002)",
                            "arrange": "Prepare customer data with invalid email='invalid-email'",
                            "act": "Customer.create(customer_data)",
                            "assert": "Raises ValidationError with message 'Invalid email format'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-002"]
                        },
                        {
                            "name": "test_customer_required_fields_missing",
                            "scenario": "error_case",
                            "description": "Should enforce required fields (BR-CUST-004)",
                            "arrange": "Prepare customer data missing 'name' field",
                            "act": "Customer.create(customer_data)",
                            "assert": "Raises ValidationError with message 'Required field: name'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-004"]
                        },
                        {
                            "name": "test_customer_negative_income",
                            "scenario": "edge_case",
                            "description": "Should reject negative income values",
                            "arrange": "Prepare customer data with monthly_income=-1000",
                            "act": "Customer.create(customer_data)",
                            "assert": "Raises ValidationError with message 'Income must be positive'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-002"]
                        },
                        {
                            "name": "test_customer_negative_debt",
                            "scenario": "edge_case",
                            "description": "Should reject negative debt values",
                            "arrange": "Prepare customer data with total_debt=-500",
                            "act": "Customer.create(customer_data)",
                            "assert": "Raises ValidationError with message 'Debt must be non-negative'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-002"]
                        }
                    ],
                    "mocks_required": []
                },
                {
                    "file_path": "tests/unit/domain/value_objects/test_credit_score.py",
                    "test_cases": [
                        {
                            "name": "test_calculate_credit_score_valid",
                            "scenario": "happy_path",
                            "description": f"Should calculate credit score using formula: {USER_DECISIONS['credit_score_formula']}",
                            "arrange": "monthly_income=5000, total_debt=1000",
                            "act": "score = CreditScore.calculate(monthly_income, total_debt)",
                            "assert": "score.value == 680",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-001"]
                        },
                        {
                            "name": "test_credit_score_is_acceptable",
                            "scenario": "business_rule",
                            "description": f"Should validate score >= {USER_DECISIONS['credit_score_min']}",
                            "arrange": "score_value = 700",
                            "act": "score = CreditScore(score_value); result = score.is_acceptable()",
                            "assert": "Returns True",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-001"]
                        },
                        {
                            "name": "test_credit_score_below_minimum",
                            "scenario": "business_rule",
                            "description": "Should mark score below minimum as unacceptable",
                            "arrange": f"score_value = {USER_DECISIONS['credit_score_min'] - 1}",
                            "act": "score = CreditScore(score_value); result = score.is_acceptable()",
                            "assert": "Returns False",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-001"]
                        }
                    ],
                    "mocks_required": []
                },
                {
                    "file_path": "tests/unit/domain/value_objects/test_email.py",
                    "test_cases": [
                        {
                            "name": "test_email_valid_format",
                            "scenario": "happy_path",
                            "description": "Should accept valid email formats",
                            "arrange": "email_str = 'user@example.com'",
                            "act": "email = Email(email_str)",
                            "assert": "Email created, email.value == 'user@example.com'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-002"]
                        },
                        {
                            "name": "test_email_invalid_format",
                            "scenario": "error_case",
                            "description": "Should reject invalid email formats",
                            "arrange": "email_str = 'invalid-email'",
                            "act": "Email(email_str)",
                            "assert": "Raises ValueError with message 'Invalid email format'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-002"]
                        },
                        {
                            "name": "test_email_empty",
                            "scenario": "error_case",
                            "description": "Should reject empty email",
                            "arrange": "email_str = ''",
                            "act": "Email(email_str)",
                            "assert": "Raises ValueError with message 'Email cannot be empty'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-CUST-002"]
                        }
                    ],
                    "mocks_required": []
                }
            ],
            "coverage_target": 0.95
        },
        "Account": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/domain/entities/test_account.py",
                    "test_cases": [
                        {
                            "name": "test_create_account_with_valid_data",
                            "scenario": "happy_path",
                            "description": "Should create account entity linked to customer",
                            "arrange": "Prepare valid account data: customer_id='cust-123', account_type='CHECKING', initial_balance=1000",
                            "act": "account = Account.create(account_data)",
                            "assert": "Account created successfully, status='ACTIVE', balance=1000",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-ACC-003", "BR-ACC-004"]
                        },
                        {
                            "name": "test_account_debit_sufficient_balance",
                            "scenario": "happy_path",
                            "description": "Should allow debit when balance sufficient",
                            "arrange": "Create account with balance=1000",
                            "act": "account.debit(500)",
                            "assert": "Balance updated to 500, transaction succeeds",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-TXN-005"]
                        },
                        {
                            "name": "test_account_debit_insufficient_balance_no_overdraft",
                            "scenario": "business_rule",
                            "description": f"Should reject debit when balance insufficient (overdraft={USER_DECISIONS['overdraft_allowed']})",
                            "arrange": "Create account with balance=100",
                            "act": "account.debit(200)",
                            "assert": "Raises InsufficientBalanceError, balance remains 100",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-TXN-005"]
                        },
                        {
                            "name": "test_account_debit_exactly_balance",
                            "scenario": "boundary",
                            "description": "Should allow debit of exact balance amount",
                            "arrange": "Create account with balance=1000",
                            "act": "account.debit(1000)",
                            "assert": "Balance updated to 0, transaction succeeds",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-TXN-005"]
                        },
                        {
                            "name": "test_account_credit_positive_amount",
                            "scenario": "happy_path",
                            "description": "Should allow credit with positive amount",
                            "arrange": "Create account with balance=1000",
                            "act": "account.credit(500)",
                            "assert": "Balance updated to 1500, transaction succeeds",
                            "mocks_required": [],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_account_credit_negative_amount",
                            "scenario": "error_case",
                            "description": "Should reject credit with negative amount",
                            "arrange": "Create account with balance=1000",
                            "act": "account.credit(-500)",
                            "assert": "Raises ValidationError with message 'Credit amount must be positive'",
                            "mocks_required": [],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_account_status_transitions",
                            "scenario": "business_rule",
                            "description": "Should enforce valid status transitions (BR-ACC-004)",
                            "arrange": "Create account with status='ACTIVE'",
                            "act": "account.close()",
                            "assert": "Status updated to 'CLOSED', cannot perform transactions",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-ACC-004"]
                        },
                        {
                            "name": "test_account_transactions_on_closed_account",
                            "scenario": "error_case",
                            "description": "Should reject transactions on closed account",
                            "arrange": "Create account with status='CLOSED'",
                            "act": "account.debit(100)",
                            "assert": "Raises AccountClosedError",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-ACC-004"]
                        }
                    ],
                    "mocks_required": []
                }
            ],
            "coverage_target": 0.95
        },
        "Transaction": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/domain/entities/test_transaction.py",
                    "test_cases": [
                        {
                            "name": "test_create_debit_transaction",
                            "scenario": "happy_path",
                            "description": f"Should create DEBIT transaction (supported type: {USER_DECISIONS['transaction_types']})",
                            "arrange": "Prepare transaction data: account_id='acc-123', type='DEBIT', amount=500",
                            "act": "transaction = Transaction.create(transaction_data)",
                            "assert": "Transaction created with type='DEBIT', amount=500, status='PENDING'",
                            "mocks_required": [],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_create_credit_transaction",
                            "scenario": "happy_path",
                            "description": "Should create CREDIT transaction",
                            "arrange": "Prepare transaction data: account_id='acc-123', type='CREDIT', amount=1000",
                            "act": "transaction = Transaction.create(transaction_data)",
                            "assert": "Transaction created with type='CREDIT', amount=1000, status='PENDING'",
                            "mocks_required": [],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_transaction_unsupported_type",
                            "scenario": "error_case",
                            "description": f"Should reject unsupported transaction types (only {USER_DECISIONS['transaction_types']} allowed)",
                            "arrange": "Prepare transaction data with type='TRANSFER'",
                            "act": "Transaction.create(transaction_data)",
                            "assert": f"Raises ValidationError with message 'Unsupported transaction type. Allowed: {USER_DECISIONS['transaction_types']}'",
                            "mocks_required": [],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_transaction_negative_amount",
                            "scenario": "error_case",
                            "description": "Should reject negative transaction amounts",
                            "arrange": "Prepare transaction data with amount=-100",
                            "act": "Transaction.create(transaction_data)",
                            "assert": "Raises ValidationError with message 'Amount must be positive'",
                            "mocks_required": [],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_transaction_zero_amount",
                            "scenario": "boundary",
                            "description": "Should reject zero amount transactions",
                            "arrange": "Prepare transaction data with amount=0",
                            "act": "Transaction.create(transaction_data)",
                            "assert": "Raises ValidationError with message 'Amount must be greater than zero'",
                            "mocks_required": [],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_transaction_complete_success",
                            "scenario": "happy_path",
                            "description": "Should mark transaction as completed",
                            "arrange": "Create pending transaction",
                            "act": "transaction.complete()",
                            "assert": "Status updated to 'COMPLETED', completed_at timestamp set",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-TXN-004"]
                        },
                        {
                            "name": "test_transaction_fail",
                            "scenario": "error_case",
                            "description": f"Should mark transaction as failed (no retry: {USER_DECISIONS['retry_strategy']})",
                            "arrange": "Create pending transaction",
                            "act": "transaction.fail(reason='Insufficient balance')",
                            "assert": "Status updated to 'FAILED', failure_reason set, no automatic retry",
                            "mocks_required": [],
                            "business_rules_validated": []
                        }
                    ],
                    "mocks_required": []
                }
            ],
            "coverage_target": 0.95
        },
        "Authentication": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/domain/entities/test_user.py",
                    "test_cases": [
                        {
                            "name": "test_create_user_with_valid_data",
                            "scenario": "happy_path",
                            "description": "Should create user entity with hashed password",
                            "arrange": "Prepare user data: username='john_doe', password='SecurePass123!', role='CUSTOMER'",
                            "act": "user = User.create(user_data)",
                            "assert": "User created, password is hashed (not plaintext), role='CUSTOMER'",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-001", "BR-AUTH-004"]
                        },
                        {
                            "name": "test_user_verify_password_correct",
                            "scenario": "happy_path",
                            "description": "Should verify correct password",
                            "arrange": "Create user with password='SecurePass123!'",
                            "act": "result = user.verify_password('SecurePass123!')",
                            "assert": "Returns True",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-001"]
                        },
                        {
                            "name": "test_user_verify_password_incorrect",
                            "scenario": "error_case",
                            "description": "Should reject incorrect password",
                            "arrange": "Create user with password='SecurePass123!'",
                            "act": "result = user.verify_password('WrongPassword')",
                            "assert": "Returns False",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-001"]
                        },
                        {
                            "name": "test_user_password_never_plaintext",
                            "scenario": "business_rule",
                            "description": f"Should hash password using {USER_DECISIONS['password_hash']} (BR-AUTH-004)",
                            "arrange": "Create user with password='MyPassword123'",
                            "act": "Inspect user.password_hash",
                            "assert": f"password_hash starts with '$2b$' ({USER_DECISIONS['password_hash']} prefix), original password not stored",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-004"]
                        }
                    ],
                    "mocks_required": []
                },
                {
                    "file_path": "tests/unit/domain/value_objects/test_session.py",
                    "test_cases": [
                        {
                            "name": "test_create_session",
                            "scenario": "happy_path",
                            "description": "Should create session with expiration time",
                            "arrange": "user_id='user-123'",
                            "act": "session = Session.create(user_id)",
                            "assert": f"Session created with token (UUID), expires_at = now + {USER_DECISIONS['session_timeout_minutes']} minutes",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-003"]
                        },
                        {
                            "name": "test_session_is_expired",
                            "scenario": "business_rule",
                            "description": f"Should detect expired session after {USER_DECISIONS['session_timeout_minutes']} minutes",
                            "arrange": f"Create session with expires_at = now - 1 minute (past {USER_DECISIONS['session_timeout_minutes']} minute timeout)",
                            "act": "result = session.is_expired()",
                            "assert": "Returns True",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-003"]
                        },
                        {
                            "name": "test_session_not_expired",
                            "scenario": "happy_path",
                            "description": "Should detect active session within timeout",
                            "arrange": f"Create session with expires_at = now + {USER_DECISIONS['session_timeout_minutes'] - 1} minutes",
                            "act": "result = session.is_expired()",
                            "assert": "Returns False",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-003"]
                        },
                        {
                            "name": "test_session_refresh",
                            "scenario": "happy_path",
                            "description": "Should refresh session expiration",
                            "arrange": "Create session about to expire",
                            "act": "session.refresh()",
                            "assert": f"expires_at updated to now + {USER_DECISIONS['session_timeout_minutes']} minutes",
                            "mocks_required": [],
                            "business_rules_validated": ["BR-AUTH-003"]
                        }
                    ],
                    "mocks_required": []
                }
            ],
            "coverage_target": 0.95
        }
    }

    # Return strategy for the module or empty if not defined
    return strategies.get(module, {
        "unit_tests": [],
        "coverage_target": 0.95
    })

def get_use_case_test_strategy(task: Dict[str, Any], module: str, business_rules: List[str]) -> Dict[str, Any]:
    """Generate test strategy for use case layer tasks."""

    strategies = {
        "Customer": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/application/use_cases/test_create_customer.py",
                    "test_cases": [
                        {
                            "name": "test_create_customer_success",
                            "scenario": "happy_path",
                            "description": "Should create customer successfully with valid data and acceptable credit score",
                            "arrange": f"Mock ICustomerRepository: exists_by_email returns False, save returns Customer entity. Prepare valid CustomerCreateDTO with monthly_income=5000, total_debt=1000 (score=680 >= {USER_DECISIONS['credit_score_min']})",
                            "act": "result = await use_case.execute(dto)",
                            "assert": "CustomerDTO returned with id, credit_score=680, status='ACTIVE', repository.save called once, repository.exists_by_email called with correct email",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-001", "BR-CUST-002", "BR-CUST-003"]
                        },
                        {
                            "name": "test_create_customer_duplicate_email",
                            "scenario": "error_case",
                            "description": "Should raise DuplicateEmailError when email exists (BR-CUST-003)",
                            "arrange": "Mock repository.exists_by_email to return True",
                            "act": "await use_case.execute(dto)",
                            "assert": "DuplicateEmailError raised with error code 'CUST-003', repository.save NOT called",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-003"]
                        },
                        {
                            "name": "test_create_customer_low_credit_score",
                            "scenario": "business_rule",
                            "description": f"Should raise CreditAssessmentFailedError when score < {USER_DECISIONS['credit_score_min']} (BR-CUST-001)",
                            "arrange": f"Mock repository, prepare DTO with monthly_income=3000, total_debt=2500 (score=142 < {USER_DECISIONS['credit_score_min']})",
                            "act": "await use_case.execute(dto)",
                            "assert": "CreditAssessmentFailedError raised with error code 'CUST-001', message contains score 142, repository.save NOT called",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-001"]
                        },
                        {
                            "name": "test_create_customer_invalid_email_format",
                            "scenario": "error_case",
                            "description": "Should raise ValidationError for invalid email format (BR-CUST-002)",
                            "arrange": "Prepare DTO with email='invalid-email'",
                            "act": "await use_case.execute(dto)",
                            "assert": "ValidationError raised with error code 'CUST-002', repository methods NOT called",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-002"]
                        },
                        {
                            "name": "test_create_customer_missing_required_fields",
                            "scenario": "error_case",
                            "description": "Should raise ValidationError when required fields missing (BR-CUST-004)",
                            "arrange": "Prepare DTO missing 'name' field",
                            "act": "await use_case.execute(dto)",
                            "assert": "ValidationError raised with error code 'CUST-004', message 'Required field: name'",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-004"]
                        }
                    ],
                    "mocks_required": ["ICustomerRepository"]
                },
                {
                    "file_path": "tests/unit/application/use_cases/test_get_customer.py",
                    "test_cases": [
                        {
                            "name": "test_get_customer_by_id_exists",
                            "scenario": "happy_path",
                            "description": "Should retrieve customer by valid ID",
                            "arrange": "Mock repository.find_by_id to return Customer entity",
                            "act": "result = await use_case.execute(customer_id='cust-123')",
                            "assert": "CustomerDTO returned with correct data, repository.find_by_id called once with 'cust-123'",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_get_customer_by_id_not_found",
                            "scenario": "error_case",
                            "description": "Should raise CustomerNotFoundError when ID doesn't exist (BR-CUST-003)",
                            "arrange": "Mock repository.find_by_id to return None",
                            "act": "await use_case.execute(customer_id='nonexistent')",
                            "assert": "CustomerNotFoundError raised with error code 'CUST-404', message contains 'nonexistent'",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-003"]
                        }
                    ],
                    "mocks_required": ["ICustomerRepository"]
                },
                {
                    "file_path": "tests/unit/application/use_cases/test_update_customer.py",
                    "test_cases": [
                        {
                            "name": "test_update_customer_success",
                            "scenario": "happy_path",
                            "description": "Should update customer data successfully",
                            "arrange": "Mock repository.find_by_id returns Customer, save returns updated Customer. Prepare UpdateCustomerDTO with new address",
                            "act": "result = await use_case.execute(customer_id='cust-123', dto=update_dto)",
                            "assert": "CustomerDTO returned with updated address, repository.save called once",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-002"]
                        },
                        {
                            "name": "test_update_customer_not_found",
                            "scenario": "error_case",
                            "description": "Should raise CustomerNotFoundError when customer doesn't exist",
                            "arrange": "Mock repository.find_by_id to return None",
                            "act": "await use_case.execute(customer_id='nonexistent', dto=update_dto)",
                            "assert": "CustomerNotFoundError raised, repository.save NOT called",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_update_customer_invalid_data",
                            "scenario": "error_case",
                            "description": "Should raise ValidationError for invalid update data",
                            "arrange": "Mock repository, prepare DTO with invalid email format",
                            "act": "await use_case.execute(customer_id='cust-123', dto=update_dto)",
                            "assert": "ValidationError raised with error code 'CUST-002'",
                            "mocks_required": ["ICustomerRepository"],
                            "business_rules_validated": ["BR-CUST-002"]
                        }
                    ],
                    "mocks_required": ["ICustomerRepository"]
                }
            ],
            "coverage_target": 0.90
        },
        "Account": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/application/use_cases/test_create_account.py",
                    "test_cases": [
                        {
                            "name": "test_create_account_success",
                            "scenario": "happy_path",
                            "description": "Should create account for existing customer within account limit",
                            "arrange": f"Mock IAccountRepository: count_by_customer returns 3 (< {USER_DECISIONS['max_accounts_per_customer']}), save returns Account. Mock ICustomerRepository: find_by_id returns Customer",
                            "act": "result = await use_case.execute(dto)",
                            "assert": "AccountDTO returned with id, status='ACTIVE', repositories called correctly",
                            "mocks_required": ["IAccountRepository", "ICustomerRepository"],
                            "business_rules_validated": ["BR-ACC-001", "BR-ACC-003"]
                        },
                        {
                            "name": "test_create_account_customer_not_found",
                            "scenario": "error_case",
                            "description": "Should raise CustomerNotFoundError when customer doesn't exist (BR-ACC-003)",
                            "arrange": "Mock ICustomerRepository.find_by_id to return None",
                            "act": "await use_case.execute(dto)",
                            "assert": "CustomerNotFoundError raised with error code 'CUST-404', account repository NOT called",
                            "mocks_required": ["IAccountRepository", "ICustomerRepository"],
                            "business_rules_validated": ["BR-ACC-003"]
                        },
                        {
                            "name": "test_create_account_max_accounts_exceeded",
                            "scenario": "business_rule",
                            "description": f"Should raise MaxAccountsExceededError when customer has {USER_DECISIONS['max_accounts_per_customer']} accounts (BR-ACC-001)",
                            "arrange": f"Mock IAccountRepository.count_by_customer to return {USER_DECISIONS['max_accounts_per_customer']}",
                            "act": "await use_case.execute(dto)",
                            "assert": f"MaxAccountsExceededError raised with error code 'ACC-001', message 'Maximum {USER_DECISIONS['max_accounts_per_customer']} accounts per customer', save NOT called",
                            "mocks_required": ["IAccountRepository", "ICustomerRepository"],
                            "business_rules_validated": ["BR-ACC-001"]
                        },
                        {
                            "name": "test_create_account_exactly_at_limit",
                            "scenario": "boundary",
                            "description": f"Should reject account creation when customer has exactly {USER_DECISIONS['max_accounts_per_customer']} accounts",
                            "arrange": f"Mock count_by_customer to return {USER_DECISIONS['max_accounts_per_customer']}",
                            "act": "await use_case.execute(dto)",
                            "assert": "MaxAccountsExceededError raised",
                            "mocks_required": ["IAccountRepository", "ICustomerRepository"],
                            "business_rules_validated": ["BR-ACC-001"]
                        }
                    ],
                    "mocks_required": ["IAccountRepository", "ICustomerRepository"]
                },
                {
                    "file_path": "tests/unit/application/use_cases/test_get_accounts_by_customer.py",
                    "test_cases": [
                        {
                            "name": "test_get_accounts_by_customer_success",
                            "scenario": "happy_path",
                            "description": f"Should retrieve accounts for customer with pagination (limit {USER_DECISIONS['account_query_limit']})",
                            "arrange": "Mock IAccountRepository.find_by_customer to return list of 5 Account entities",
                            "act": "result = await use_case.execute(customer_id='cust-123')",
                            "assert": f"List of AccountDTOs returned (max {USER_DECISIONS['account_query_limit']}), repository.find_by_customer called with limit={USER_DECISIONS['account_query_limit']}",
                            "mocks_required": ["IAccountRepository"],
                            "business_rules_validated": ["BR-ACC-002"]
                        },
                        {
                            "name": "test_get_accounts_customer_no_accounts",
                            "scenario": "edge_case",
                            "description": "Should return empty list when customer has no accounts",
                            "arrange": "Mock repository.find_by_customer to return empty list",
                            "act": "result = await use_case.execute(customer_id='cust-456')",
                            "assert": "Empty list returned, no error raised",
                            "mocks_required": ["IAccountRepository"],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_get_accounts_respects_pagination_limit",
                            "scenario": "business_rule",
                            "description": f"Should enforce pagination limit of {USER_DECISIONS['account_query_limit']} accounts (BR-ACC-002)",
                            "arrange": f"Mock repository to have customer with 25 accounts",
                            "act": "result = await use_case.execute(customer_id='cust-789')",
                            "assert": f"Exactly {USER_DECISIONS['account_query_limit']} accounts returned, pagination metadata provided",
                            "mocks_required": ["IAccountRepository"],
                            "business_rules_validated": ["BR-ACC-002"]
                        }
                    ],
                    "mocks_required": ["IAccountRepository"]
                }
            ],
            "coverage_target": 0.90
        },
        "Transaction": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/application/use_cases/test_process_transaction.py",
                    "test_cases": [
                        {
                            "name": "test_process_debit_transaction_sufficient_balance",
                            "scenario": "happy_path",
                            "description": "Should process DEBIT transaction when balance sufficient",
                            "arrange": "Mock IAccountRepository.find_by_id returns Account with balance=1000. Mock ITransactionRepository.save. Prepare TransactionDTO with type='DEBIT', amount=500",
                            "act": "result = await use_case.execute(dto)",
                            "assert": "Transaction completed, account balance updated to 500, transaction saved with status='COMPLETED'",
                            "mocks_required": ["IAccountRepository", "ITransactionRepository"],
                            "business_rules_validated": ["BR-TXN-005"]
                        },
                        {
                            "name": "test_process_debit_insufficient_balance",
                            "scenario": "business_rule",
                            "description": f"Should reject DEBIT when balance insufficient (overdraft={USER_DECISIONS['overdraft_allowed']}, BR-TXN-005)",
                            "arrange": "Mock account with balance=100, prepare transaction with amount=200",
                            "act": "await use_case.execute(dto)",
                            "assert": "InsufficientBalanceError raised with error code 'TXN-005', transaction saved with status='FAILED', account balance unchanged",
                            "mocks_required": ["IAccountRepository", "ITransactionRepository"],
                            "business_rules_validated": ["BR-TXN-005"]
                        },
                        {
                            "name": "test_process_credit_transaction",
                            "scenario": "happy_path",
                            "description": "Should process CREDIT transaction",
                            "arrange": "Mock account with balance=1000, prepare transaction with type='CREDIT', amount=500",
                            "act": "result = await use_case.execute(dto)",
                            "assert": "Transaction completed, account balance updated to 1500, transaction saved with status='COMPLETED'",
                            "mocks_required": ["IAccountRepository", "ITransactionRepository"],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_transaction_account_not_found",
                            "scenario": "error_case",
                            "description": "Should raise AccountNotFoundError when account doesn't exist",
                            "arrange": "Mock IAccountRepository.find_by_id to return None",
                            "act": "await use_case.execute(dto)",
                            "assert": "AccountNotFoundError raised with error code 'ACC-404', transaction saved with status='FAILED'",
                            "mocks_required": ["IAccountRepository", "ITransactionRepository"],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_transaction_on_closed_account",
                            "scenario": "error_case",
                            "description": "Should reject transaction on closed account (BR-ACC-004)",
                            "arrange": "Mock account with status='CLOSED'",
                            "act": "await use_case.execute(dto)",
                            "assert": "AccountClosedError raised with error code 'ACC-004', transaction saved with status='FAILED'",
                            "mocks_required": ["IAccountRepository", "ITransactionRepository"],
                            "business_rules_validated": ["BR-ACC-004"]
                        },
                        {
                            "name": "test_transaction_no_automatic_retry",
                            "scenario": "business_rule",
                            "description": f"Should NOT automatically retry failed transactions (retry_strategy={USER_DECISIONS['retry_strategy']})",
                            "arrange": "Mock account operation to fail (e.g., database error)",
                            "act": "await use_case.execute(dto)",
                            "assert": "TransactionFailedError raised, transaction marked 'FAILED', NO automatic retry attempted",
                            "mocks_required": ["IAccountRepository", "ITransactionRepository"],
                            "business_rules_validated": []
                        },
                        {
                            "name": "test_transaction_audit_logging",
                            "scenario": "business_rule",
                            "description": "Should create complete audit trail for transaction (BR-TXN-004)",
                            "arrange": "Mock repositories, prepare valid transaction",
                            "act": "result = await use_case.execute(dto)",
                            "assert": "Transaction saved with: timestamp, user_id, account_id, type, amount, status, audit fields populated",
                            "mocks_required": ["IAccountRepository", "ITransactionRepository"],
                            "business_rules_validated": ["BR-TXN-004"]
                        }
                    ],
                    "mocks_required": ["IAccountRepository", "ITransactionRepository"]
                }
            ],
            "coverage_target": 0.90
        },
        "Authentication": {
            "unit_tests": [
                {
                    "file_path": "tests/unit/application/use_cases/test_authenticate_user.py",
                    "test_cases": [
                        {
                            "name": "test_authenticate_user_success",
                            "scenario": "happy_path",
                            "description": "Should authenticate user with valid credentials",
                            "arrange": "Mock IUserRepository.find_by_username returns User with valid password hash. Mock ISessionRepository.create_session",
                            "act": "result = await use_case.execute(username='john_doe', password='SecurePass123!')",
                            "assert": f"SessionDTO returned with token, expires_at = now + {USER_DECISIONS['session_timeout_minutes']} minutes, user authenticated",
                            "mocks_required": ["IUserRepository", "ISessionRepository"],
                            "business_rules_validated": ["BR-AUTH-001", "BR-AUTH-003"]
                        },
                        {
                            "name": "test_authenticate_user_invalid_username",
                            "scenario": "error_case",
                            "description": "Should raise AuthenticationError for invalid username",
                            "arrange": "Mock IUserRepository.find_by_username to return None",
                            "act": "await use_case.execute(username='nonexistent', password='password')",
                            "assert": "AuthenticationError raised with error code 'AUTH-001', message 'Invalid credentials', session NOT created",
                            "mocks_required": ["IUserRepository", "ISessionRepository"],
                            "business_rules_validated": ["BR-AUTH-001"]
                        },
                        {
                            "name": "test_authenticate_user_invalid_password",
                            "scenario": "error_case",
                            "description": "Should raise AuthenticationError for invalid password",
                            "arrange": "Mock repository returns User, but password verification fails",
                            "act": "await use_case.execute(username='john_doe', password='WrongPassword')",
                            "assert": "AuthenticationError raised with error code 'AUTH-001', session NOT created, failed attempt logged",
                            "mocks_required": ["IUserRepository", "ISessionRepository"],
                            "business_rules_validated": ["BR-AUTH-001"]
                        }
                    ],
                    "mocks_required": ["IUserRepository", "ISessionRepository"]
                },
                {
                    "file_path": "tests/unit/application/use_cases/test_validate_session.py",
                    "test_cases": [
                        {
                            "name": "test_validate_session_active",
                            "scenario": "happy_path",
                            "description": "Should validate active session within timeout",
                            "arrange": f"Mock ISessionRepository.find_by_token returns Session with expires_at = now + {USER_DECISIONS['session_timeout_minutes'] - 1} minutes",
                            "act": "result = await use_case.execute(token='valid-token')",
                            "assert": "Returns UserDTO, session is valid",
                            "mocks_required": ["ISessionRepository", "IUserRepository"],
                            "business_rules_validated": ["BR-AUTH-003"]
                        },
                        {
                            "name": "test_validate_session_expired",
                            "scenario": "business_rule",
                            "description": f"Should reject expired session (timeout={USER_DECISIONS['session_timeout_minutes']} minutes, BR-AUTH-003)",
                            "arrange": "Mock repository returns Session with expires_at = now - 1 minute (expired)",
                            "act": "await use_case.execute(token='expired-token')",
                            "assert": "SessionExpiredError raised with error code 'AUTH-003', user must re-authenticate",
                            "mocks_required": ["ISessionRepository", "IUserRepository"],
                            "business_rules_validated": ["BR-AUTH-003"]
                        },
                        {
                            "name": "test_validate_session_not_found",
                            "scenario": "error_case",
                            "description": "Should reject invalid session token",
                            "arrange": "Mock repository.find_by_token to return None",
                            "act": "await use_case.execute(token='invalid-token')",
                            "assert": "SessionNotFoundError raised with error code 'AUTH-404'",
                            "mocks_required": ["ISessionRepository", "IUserRepository"],
                            "business_rules_validated": []
                        }
                    ],
                    "mocks_required": ["ISessionRepository", "IUserRepository"]
                }
            ],
            "coverage_target": 0.90
        }
    }

    return strategies.get(module, {
        "unit_tests": [],
        "coverage_target": 0.90
    })

def get_infrastructure_test_strategy(task: Dict[str, Any], module: str, layer: str) -> Dict[str, Any]:
    """Generate test strategy for infrastructure layer tasks."""

    if layer == "infrastructure_db":
        # Database/Repository integration tests
        strategies = {
            "Customer": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/repositories/test_customer_repository.py",
                        "test_cases": [
                            {
                                "name": "test_save_customer_success",
                                "scenario": "happy_path",
                                "description": "Should persist customer to database",
                                "arrange": "Create Customer entity with valid data, initialize test database",
                                "act": "repository.save(customer)",
                                "assert": "Customer persisted to DB, ID generated, timestamps set, can be retrieved",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_find_by_id_exists",
                                "scenario": "happy_path",
                                "description": "Should retrieve customer by ID from database",
                                "arrange": "Save customer to DB with id='cust-123'",
                                "act": "result = repository.find_by_id('cust-123')",
                                "assert": "Customer entity returned with correct data",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_find_by_id_not_found",
                                "scenario": "error_case",
                                "description": "Should return None when customer ID doesn't exist",
                                "arrange": "Empty database",
                                "act": "result = repository.find_by_id('nonexistent')",
                                "assert": "Returns None",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_exists_by_email_true",
                                "scenario": "happy_path",
                                "description": "Should detect duplicate email (BR-CUST-003)",
                                "arrange": "Save customer with email='john@example.com'",
                                "act": "result = repository.exists_by_email('john@example.com')",
                                "assert": "Returns True",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-CUST-003"]
                            },
                            {
                                "name": "test_exists_by_email_false",
                                "scenario": "happy_path",
                                "description": "Should return False for unique email",
                                "arrange": "Empty database",
                                "act": "result = repository.exists_by_email('unique@example.com')",
                                "assert": "Returns False",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_update_customer",
                                "scenario": "happy_path",
                                "description": "Should update existing customer",
                                "arrange": "Save customer, modify customer entity",
                                "act": "repository.save(modified_customer)",
                                "assert": "Customer updated in DB, updated_at timestamp changed",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            }
                        ],
                        "dependencies_required": ["test_database", "SQLAlchemy"]
                    }
                ],
                "coverage_target": 0.85
            },
            "Account": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/repositories/test_account_repository.py",
                        "test_cases": [
                            {
                                "name": "test_save_account_with_foreign_key",
                                "scenario": "happy_path",
                                "description": "Should persist account linked to customer (BR-ACC-003)",
                                "arrange": "Create and save Customer entity, create Account entity with customer_id",
                                "act": "repository.save(account)",
                                "assert": "Account persisted with foreign key to customer, referential integrity maintained",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-ACC-003"]
                            },
                            {
                                "name": "test_save_account_invalid_customer_id",
                                "scenario": "error_case",
                                "description": "Should reject account with nonexistent customer_id",
                                "arrange": "Create Account entity with customer_id='nonexistent'",
                                "act": "repository.save(account)",
                                "assert": "IntegrityError raised (foreign key violation)",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-ACC-003"]
                            },
                            {
                                "name": "test_count_by_customer",
                                "scenario": "business_rule",
                                "description": f"Should count accounts per customer for max limit validation (BR-ACC-001, max={USER_DECISIONS['max_accounts_per_customer']})",
                                "arrange": "Create customer with 5 accounts",
                                "act": "count = repository.count_by_customer(customer_id)",
                                "assert": "Returns 5",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-ACC-001"]
                            },
                            {
                                "name": "test_find_by_customer_with_pagination",
                                "scenario": "business_rule",
                                "description": f"Should retrieve accounts with pagination limit {USER_DECISIONS['account_query_limit']} (BR-ACC-002)",
                                "arrange": "Create customer with 25 accounts",
                                "act": f"accounts = repository.find_by_customer(customer_id, limit={USER_DECISIONS['account_query_limit']})",
                                "assert": f"Returns exactly {USER_DECISIONS['account_query_limit']} accounts",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-ACC-002"]
                            }
                        ],
                        "dependencies_required": ["test_database", "SQLAlchemy"]
                    }
                ],
                "coverage_target": 0.85
            },
            "Transaction": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/repositories/test_transaction_repository.py",
                        "test_cases": [
                            {
                                "name": "test_save_transaction_with_audit_trail",
                                "scenario": "business_rule",
                                "description": "Should persist transaction with complete audit trail (BR-TXN-004)",
                                "arrange": "Create Transaction entity with all audit fields",
                                "act": "repository.save(transaction)",
                                "assert": "Transaction persisted with timestamp, user_id, account_id, type, amount, status, all audit fields present",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-TXN-004"]
                            },
                            {
                                "name": "test_find_by_account",
                                "scenario": "happy_path",
                                "description": "Should retrieve transaction history for account",
                                "arrange": "Create account with 10 transactions",
                                "act": "transactions = repository.find_by_account(account_id)",
                                "assert": "Returns list of 10 transactions ordered by timestamp desc",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            }
                        ],
                        "dependencies_required": ["test_database", "SQLAlchemy"]
                    }
                ],
                "coverage_target": 0.85
            },
            "Authentication": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/repositories/test_user_repository.py",
                        "test_cases": [
                            {
                                "name": "test_save_user_with_hashed_password",
                                "scenario": "business_rule",
                                "description": f"Should persist user with {USER_DECISIONS['password_hash']} hashed password (BR-AUTH-004)",
                                "arrange": "Create User entity with hashed password",
                                "act": "repository.save(user)",
                                "assert": f"User persisted, password_hash stored (bcrypt format), plaintext password NOT stored",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-AUTH-004"]
                            },
                            {
                                "name": "test_find_by_username",
                                "scenario": "happy_path",
                                "description": "Should retrieve user by username",
                                "arrange": "Save user with username='john_doe'",
                                "act": "result = repository.find_by_username('john_doe')",
                                "assert": "User entity returned",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            }
                        ],
                        "dependencies_required": ["test_database", "SQLAlchemy"]
                    },
                    {
                        "file_path": "tests/integration/infrastructure/repositories/test_session_repository.py",
                        "test_cases": [
                            {
                                "name": "test_create_session_with_expiration",
                                "scenario": "business_rule",
                                "description": f"Should create session with {USER_DECISIONS['session_timeout_minutes']} minute expiration (BR-AUTH-003)",
                                "arrange": "Prepare session data for user_id='user-123'",
                                "act": "session = repository.create_session(user_id)",
                                "assert": f"Session persisted with token, expires_at = now + {USER_DECISIONS['session_timeout_minutes']} minutes",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-AUTH-003"]
                            },
                            {
                                "name": "test_find_by_token",
                                "scenario": "happy_path",
                                "description": "Should retrieve session by token",
                                "arrange": "Create session with token='abc-123'",
                                "act": "result = repository.find_by_token('abc-123')",
                                "assert": "Session entity returned",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_delete_expired_sessions",
                                "scenario": "business_rule",
                                "description": "Should cleanup expired sessions",
                                "arrange": "Create 5 expired sessions and 3 active sessions",
                                "act": "repository.delete_expired_sessions()",
                                "assert": "5 expired sessions deleted, 3 active sessions remain",
                                "dependencies_required": ["test_database"],
                                "business_rules_validated": ["BR-AUTH-003"]
                            }
                        ],
                        "dependencies_required": ["test_database", "SQLAlchemy"]
                    }
                ],
                "coverage_target": 0.85
            }
        }
        return strategies.get(module, {
            "integration_tests": [],
            "coverage_target": 0.85
        })

    elif layer == "infrastructure_api":
        # API endpoint integration tests
        strategies = {
            "Customer": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/api/test_customer_api.py",
                        "test_cases": [
                            {
                                "name": "test_post_customers_success",
                                "scenario": "happy_path",
                                "description": "Should create customer via API and return 201",
                                "arrange": f"TestClient with test database, prepare valid CustomerCreate payload with monthly_income=5000, total_debt=1000 (score=680 >= {USER_DECISIONS['credit_score_min']})",
                                "act": "response = client.post('/api/v1/customers', json=payload)",
                                "assert": "Status 201, response body contains customer with id, credit_score=680, status='ACTIVE', created_at, updated_at. Customer exists in database.",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-CUST-001", "BR-CUST-002", "BR-CUST-004"]
                            },
                            {
                                "name": "test_post_customers_invalid_email",
                                "scenario": "error_case",
                                "description": "Should return 400 for invalid email format (BR-CUST-002)",
                                "arrange": "Prepare payload with email='invalid-email'",
                                "act": "response = client.post('/api/v1/customers', json=payload)",
                                "assert": "Status 400, response contains error_code='CUST-002', message mentions invalid email",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-CUST-002"]
                            },
                            {
                                "name": "test_post_customers_duplicate_email",
                                "scenario": "error_case",
                                "description": "Should return 409 with error code CUST-003 for duplicate email",
                                "arrange": "Create customer via API with email='john@example.com', prepare payload with same email",
                                "act": "response = client.post('/api/v1/customers', json=payload)",
                                "assert": "Status 409, response contains error_code='CUST-003', message mentions duplicate email",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-CUST-003"]
                            },
                            {
                                "name": "test_post_customers_low_credit_score",
                                "scenario": "business_rule",
                                "description": f"Should return 422 when credit score < {USER_DECISIONS['credit_score_min']} (BR-CUST-001)",
                                "arrange": f"Prepare payload with monthly_income=3000, total_debt=2500 (score=142 < {USER_DECISIONS['credit_score_min']})",
                                "act": "response = client.post('/api/v1/customers', json=payload)",
                                "assert": "Status 422, error_code='CUST-001', message mentions credit assessment failed with score 142",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-CUST-001"]
                            },
                            {
                                "name": "test_get_customers_by_id_success",
                                "scenario": "happy_path",
                                "description": "Should retrieve customer by ID",
                                "arrange": "Create customer via API, save customer_id",
                                "act": "response = client.get(f'/api/v1/customers/{customer_id}')",
                                "assert": "Status 200, response contains customer data",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_get_customers_by_id_not_found",
                                "scenario": "error_case",
                                "description": "Should return 404 when customer not found",
                                "arrange": "No customer in database",
                                "act": "response = client.get('/api/v1/customers/nonexistent')",
                                "assert": "Status 404, error_code='CUST-404', message mentions customer not found",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_put_customers_success",
                                "scenario": "happy_path",
                                "description": "Should update customer via API",
                                "arrange": "Create customer, prepare update payload with new address",
                                "act": "response = client.put(f'/api/v1/customers/{customer_id}', json=update_payload)",
                                "assert": "Status 200, response contains updated customer with new address",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-CUST-002"]
                            }
                        ],
                        "dependencies_required": ["FastAPI TestClient", "test_database"]
                    }
                ],
                "coverage_target": 0.85
            },
            "Account": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/api/test_account_api.py",
                        "test_cases": [
                            {
                                "name": "test_post_accounts_success",
                                "scenario": "happy_path",
                                "description": "Should create account via API",
                                "arrange": f"Create customer via API, prepare AccountCreate payload (customer has < {USER_DECISIONS['max_accounts_per_customer']} accounts)",
                                "act": "response = client.post('/api/v1/accounts', json=payload)",
                                "assert": "Status 201, response contains account with id, customer_id, status='ACTIVE', balance",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-ACC-001", "BR-ACC-003"]
                            },
                            {
                                "name": "test_post_accounts_customer_not_found",
                                "scenario": "error_case",
                                "description": "Should return 404 when customer doesn't exist (BR-ACC-003)",
                                "arrange": "Prepare payload with customer_id='nonexistent'",
                                "act": "response = client.post('/api/v1/accounts', json=payload)",
                                "assert": "Status 404, error_code='CUST-404', message mentions customer not found",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-ACC-003"]
                            },
                            {
                                "name": "test_post_accounts_max_limit_exceeded",
                                "scenario": "business_rule",
                                "description": f"Should return 422 when customer has {USER_DECISIONS['max_accounts_per_customer']} accounts (BR-ACC-001)",
                                "arrange": f"Create customer with exactly {USER_DECISIONS['max_accounts_per_customer']} accounts, prepare payload for new account",
                                "act": "response = client.post('/api/v1/accounts', json=payload)",
                                "assert": f"Status 422, error_code='ACC-001', message mentions maximum {USER_DECISIONS['max_accounts_per_customer']} accounts exceeded",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-ACC-001"]
                            },
                            {
                                "name": "test_get_accounts_by_customer",
                                "scenario": "business_rule",
                                "description": f"Should retrieve accounts with pagination limit {USER_DECISIONS['account_query_limit']} (BR-ACC-002)",
                                "arrange": "Create customer with 5 accounts",
                                "act": "response = client.get(f'/api/v1/customers/{customer_id}/accounts')",
                                "assert": f"Status 200, response contains list of 5 accounts (max {USER_DECISIONS['account_query_limit']})",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-ACC-002"]
                            }
                        ],
                        "dependencies_required": ["FastAPI TestClient", "test_database"]
                    }
                ],
                "coverage_target": 0.85
            },
            "Transaction": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/api/test_transaction_api.py",
                        "test_cases": [
                            {
                                "name": "test_post_transactions_debit_success",
                                "scenario": "happy_path",
                                "description": "Should process DEBIT transaction via API",
                                "arrange": "Create account with balance=1000, prepare TransactionCreate payload with type='DEBIT', amount=500",
                                "act": "response = client.post('/api/v1/transactions', json=payload)",
                                "assert": "Status 201, transaction completed, account balance=500, response contains transaction with status='COMPLETED'",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-TXN-005"]
                            },
                            {
                                "name": "test_post_transactions_debit_insufficient_balance",
                                "scenario": "business_rule",
                                "description": f"Should return 422 for insufficient balance (overdraft={USER_DECISIONS['overdraft_allowed']}, BR-TXN-005)",
                                "arrange": "Create account with balance=100, prepare payload with amount=200",
                                "act": "response = client.post('/api/v1/transactions', json=payload)",
                                "assert": "Status 422, error_code='TXN-005', message mentions insufficient balance, account balance unchanged",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-TXN-005"]
                            },
                            {
                                "name": "test_post_transactions_credit_success",
                                "scenario": "happy_path",
                                "description": "Should process CREDIT transaction via API",
                                "arrange": "Create account with balance=1000, prepare payload with type='CREDIT', amount=500",
                                "act": "response = client.post('/api/v1/transactions', json=payload)",
                                "assert": "Status 201, transaction completed, account balance=1500",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_post_transactions_unsupported_type",
                                "scenario": "error_case",
                                "description": f"Should return 400 for unsupported transaction type (only {USER_DECISIONS['transaction_types']} allowed)",
                                "arrange": "Prepare payload with type='TRANSFER'",
                                "act": "response = client.post('/api/v1/transactions', json=payload)",
                                "assert": f"Status 400, error message mentions unsupported type, allowed types: {USER_DECISIONS['transaction_types']}",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_post_transactions_account_not_found",
                                "scenario": "error_case",
                                "description": "Should return 404 when account doesn't exist",
                                "arrange": "Prepare payload with account_id='nonexistent'",
                                "act": "response = client.post('/api/v1/transactions', json=payload)",
                                "assert": "Status 404, error_code='ACC-404'",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_post_transactions_closed_account",
                                "scenario": "error_case",
                                "description": "Should return 422 for transactions on closed account (BR-ACC-004)",
                                "arrange": "Create account with status='CLOSED', prepare transaction payload",
                                "act": "response = client.post('/api/v1/transactions', json=payload)",
                                "assert": "Status 422, error_code='ACC-004', message mentions account closed",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-ACC-004"]
                            },
                            {
                                "name": "test_get_transactions_by_account",
                                "scenario": "happy_path",
                                "description": "Should retrieve transaction history",
                                "arrange": "Create account with 10 transactions",
                                "act": "response = client.get(f'/api/v1/accounts/{account_id}/transactions')",
                                "assert": "Status 200, response contains list of 10 transactions with audit trail",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-TXN-004"]
                            }
                        ],
                        "dependencies_required": ["FastAPI TestClient", "test_database"]
                    }
                ],
                "coverage_target": 0.85
            },
            "Authentication": {
                "integration_tests": [
                    {
                        "file_path": "tests/integration/infrastructure/api/test_auth_api.py",
                        "test_cases": [
                            {
                                "name": "test_post_auth_login_success",
                                "scenario": "happy_path",
                                "description": "Should authenticate user and return session token",
                                "arrange": "Create user via repository with username='john_doe', password='SecurePass123!', prepare login payload",
                                "act": "response = client.post('/api/v1/auth/login', json=payload)",
                                "assert": f"Status 200, response contains access_token, expires_in={USER_DECISIONS['session_timeout_minutes']*60} seconds, token_type='Bearer'",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-AUTH-001", "BR-AUTH-003"]
                            },
                            {
                                "name": "test_post_auth_login_invalid_credentials",
                                "scenario": "error_case",
                                "description": "Should return 401 for invalid credentials (BR-AUTH-001)",
                                "arrange": "Prepare login payload with incorrect username/password",
                                "act": "response = client.post('/api/v1/auth/login', json=payload)",
                                "assert": "Status 401, error_code='AUTH-001', message='Invalid credentials'",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-AUTH-001"]
                            },
                            {
                                "name": "test_get_protected_endpoint_with_valid_token",
                                "scenario": "happy_path",
                                "description": "Should allow access with valid session token",
                                "arrange": "Login to get token, prepare Authorization header",
                                "act": "response = client.get('/api/v1/customers/me', headers={'Authorization': f'Bearer {token}'})",
                                "assert": "Status 200, user data returned",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-AUTH-002"]
                            },
                            {
                                "name": "test_get_protected_endpoint_with_expired_token",
                                "scenario": "business_rule",
                                "description": f"Should return 401 for expired session (timeout={USER_DECISIONS['session_timeout_minutes']} min, BR-AUTH-003)",
                                "arrange": f"Create session manually with expires_at = now - 1 minute (past {USER_DECISIONS['session_timeout_minutes']} min timeout)",
                                "act": "response = client.get('/api/v1/customers/me', headers={'Authorization': f'Bearer {expired_token}'})",
                                "assert": "Status 401, error_code='AUTH-003', message mentions session expired",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": ["BR-AUTH-003"]
                            },
                            {
                                "name": "test_get_protected_endpoint_without_token",
                                "scenario": "error_case",
                                "description": "Should return 401 when no authorization header",
                                "arrange": "No authorization header",
                                "act": "response = client.get('/api/v1/customers/me')",
                                "assert": "Status 401, message mentions missing authentication",
                                "dependencies_required": ["TestClient", "test_database"],
                                "business_rules_validated": []
                            }
                        ],
                        "dependencies_required": ["FastAPI TestClient", "test_database"]
                    }
                ],
                "coverage_target": 0.85
            }
        }
        return strategies.get(module, {
            "integration_tests": [],
            "coverage_target": 0.85
        })

    elif layer == "infrastructure_frontend":
        # E2E tests for frontend
        strategies = {
            "Customer": {
                "e2e_tests": [
                    {
                        "file_path": "tests/e2e/test_customer_workflows.spec.ts",
                        "test_cases": [
                            {
                                "name": "test_create_customer_success_flow",
                                "scenario": "happy_path",
                                "description": "User can create customer with valid data",
                                "user_flow": "Navigate to /customers/new → Fill form with valid data (income=5000, debt=1000) → Click Create → See success message",
                                "steps": [
                                    "1. Navigate to http://localhost:3001/customers/new",
                                    "2. Fill input[name='name'] with 'John Doe'",
                                    "3. Fill input[name='email'] with 'john@example.com'",
                                    "4. Fill input[name='monthly_income'] with '5000'",
                                    "5. Fill input[name='total_debt'] with '1000'",
                                    "6. Click button[type='submit']",
                                    "7. Wait for navigation or success message"
                                ],
                                "expected_outcomes": [
                                    "Form submits successfully",
                                    "Success message displays 'Customer created successfully'",
                                    "Credit score 680 shown (calculated from income/debt)",
                                    "Status shows 'ACTIVE'",
                                    "Redirected to customer details page or customer list"
                                ],
                                "business_rules_validated": ["BR-CUST-001", "BR-CUST-002", "BR-CUST-004"]
                            },
                            {
                                "name": "test_create_customer_duplicate_email_error",
                                "scenario": "error_case",
                                "description": "User sees error when creating customer with duplicate email",
                                "user_flow": "Create customer with email → Try to create another with same email → See error message",
                                "steps": [
                                    "1. Create first customer with email='duplicate@example.com' (via API or UI)",
                                    "2. Navigate to /customers/new",
                                    "3. Fill form with same email='duplicate@example.com'",
                                    "4. Click submit",
                                    "5. Wait for error message"
                                ],
                                "expected_outcomes": [
                                    "Form submission fails",
                                    "Error message displays 'Email already exists' or similar",
                                    "Error code CUST-003 shown (if displayed in UI)",
                                    "User remains on form page",
                                    "Can correct and resubmit"
                                ],
                                "business_rules_validated": ["BR-CUST-003"]
                            },
                            {
                                "name": "test_create_customer_low_credit_score_error",
                                "scenario": "business_rule",
                                "description": f"User sees error when credit score < {USER_DECISIONS['credit_score_min']}",
                                "user_flow": "Fill form with income=3000, debt=2500 (score=142) → Submit → See credit assessment failure",
                                "steps": [
                                    "1. Navigate to /customers/new",
                                    "2. Fill form: name='Jane Doe', email='jane@example.com'",
                                    "3. Fill monthly_income='3000'",
                                    "4. Fill total_debt='2500' (results in score 142)",
                                    "5. Click submit",
                                    "6. Wait for error message"
                                ],
                                "expected_outcomes": [
                                    "Form submission fails",
                                    f"Error message displays 'Credit assessment failed' or 'Credit score (142) below minimum ({USER_DECISIONS['credit_score_min']})'",
                                    "Error code CUST-001 shown",
                                    "User can see calculated score (142)",
                                    "User remains on form to adjust values"
                                ],
                                "business_rules_validated": ["BR-CUST-001"]
                            },
                            {
                                "name": "test_view_customer_details",
                                "scenario": "happy_path",
                                "description": "User can view customer details",
                                "user_flow": "Navigate to customer list → Click customer → See details",
                                "steps": [
                                    "1. Create customer via API (save customer_id)",
                                    "2. Navigate to /customers",
                                    "3. Find customer in list",
                                    "4. Click customer row or view button",
                                    "5. Verify navigation to /customers/{customer_id}"
                                ],
                                "expected_outcomes": [
                                    "Customer details page loads",
                                    "All customer fields displayed (name, email, credit score, status)",
                                    "Credit score and status clearly visible",
                                    "Can navigate back to list"
                                ],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_form_validation_inline",
                                "scenario": "error_case",
                                "description": "User sees inline validation errors for invalid inputs",
                                "user_flow": "Fill form with invalid email → See inline error → Correct it → Error clears",
                                "steps": [
                                    "1. Navigate to /customers/new",
                                    "2. Fill email='invalid-email' (no @ symbol)",
                                    "3. Tab out of field or click elsewhere",
                                    "4. Observe inline validation error",
                                    "5. Correct to 'valid@example.com'",
                                    "6. Verify error clears"
                                ],
                                "expected_outcomes": [
                                    "Inline error appears next to email field",
                                    "Error message: 'Invalid email format'",
                                    "Submit button may be disabled",
                                    "After correction, error clears",
                                    "Can submit form"
                                ],
                                "business_rules_validated": ["BR-CUST-002"]
                            }
                        ]
                    }
                ],
                "coverage_target": 0.80
            },
            "Account": {
                "e2e_tests": [
                    {
                        "file_path": "tests/e2e/test_account_workflows.spec.ts",
                        "test_cases": [
                            {
                                "name": "test_create_account_for_customer",
                                "scenario": "happy_path",
                                "description": "User can create account for existing customer",
                                "user_flow": "Navigate to customer details → Click 'Add Account' → Fill form → Submit → See new account",
                                "steps": [
                                    "1. Create customer via API",
                                    "2. Navigate to /customers/{customer_id}",
                                    "3. Click 'Add Account' button",
                                    "4. Fill account form: type='CHECKING', initial_balance='1000'",
                                    "5. Click submit",
                                    "6. Wait for success"
                                ],
                                "expected_outcomes": [
                                    "Account created successfully",
                                    "Success message displays",
                                    "New account appears in customer's account list",
                                    "Account status shows 'ACTIVE'",
                                    "Balance shows '1000.00'"
                                ],
                                "business_rules_validated": ["BR-ACC-001", "BR-ACC-003", "BR-ACC-004"]
                            },
                            {
                                "name": "test_create_account_max_limit_error",
                                "scenario": "business_rule",
                                "description": f"User sees error when customer has {USER_DECISIONS['max_accounts_per_customer']} accounts",
                                "user_flow": f"Customer has {USER_DECISIONS['max_accounts_per_customer']} accounts → Try to create 10th → See error",
                                "steps": [
                                    f"1. Create customer with exactly {USER_DECISIONS['max_accounts_per_customer']} accounts (via API)",
                                    "2. Navigate to /customers/{customer_id}",
                                    "3. Click 'Add Account' button (or verify button disabled)",
                                    "4. If form opens, submit form",
                                    "5. Wait for error message"
                                ],
                                "expected_outcomes": [
                                    "'Add Account' button may be disabled with tooltip",
                                    "If form submits, error message displays",
                                    f"Error: 'Maximum {USER_DECISIONS['max_accounts_per_customer']} accounts per customer'",
                                    "Error code ACC-001 shown",
                                    "No new account created"
                                ],
                                "business_rules_validated": ["BR-ACC-001"]
                            },
                            {
                                "name": "test_view_account_list_pagination",
                                "scenario": "business_rule",
                                "description": f"User sees paginated account list (limit {USER_DECISIONS['account_query_limit']})",
                                "user_flow": "Customer with many accounts → View account list → See pagination",
                                "steps": [
                                    f"1. Create customer with {USER_DECISIONS['account_query_limit'] + 5} accounts (via API)",
                                    "2. Navigate to /customers/{customer_id}/accounts",
                                    "3. Observe account list",
                                    "4. Check for pagination controls",
                                    "5. Click 'Next' page if available"
                                ],
                                "expected_outcomes": [
                                    f"First page shows {USER_DECISIONS['account_query_limit']} accounts",
                                    "Pagination controls visible (Next, Previous, Page numbers)",
                                    f"Total count shows {USER_DECISIONS['account_query_limit'] + 5}",
                                    "Can navigate to next page",
                                    "Remaining 5 accounts shown on page 2"
                                ],
                                "business_rules_validated": ["BR-ACC-002"]
                            }
                        ]
                    }
                ],
                "coverage_target": 0.80
            },
            "Transaction": {
                "e2e_tests": [
                    {
                        "file_path": "tests/e2e/test_transaction_workflows.spec.ts",
                        "test_cases": [
                            {
                                "name": "test_debit_transaction_success",
                                "scenario": "happy_path",
                                "description": "User can perform DEBIT transaction with sufficient balance",
                                "user_flow": "Navigate to account → Click 'New Transaction' → Select DEBIT → Enter amount → Submit → See updated balance",
                                "steps": [
                                    "1. Create account with balance=1000 (via API)",
                                    "2. Navigate to /accounts/{account_id}",
                                    "3. Click 'New Transaction' button",
                                    "4. Select type='DEBIT' from dropdown",
                                    "5. Enter amount='500'",
                                    "6. Click submit",
                                    "7. Wait for success"
                                ],
                                "expected_outcomes": [
                                    "Transaction submits successfully",
                                    "Success message displays",
                                    "Account balance updates to '500.00'",
                                    "Transaction appears in transaction history with status='COMPLETED'",
                                    "Timestamp shown"
                                ],
                                "business_rules_validated": ["BR-TXN-005"]
                            },
                            {
                                "name": "test_debit_transaction_insufficient_balance",
                                "scenario": "business_rule",
                                "description": f"User sees error for DEBIT with insufficient balance (overdraft={USER_DECISIONS['overdraft_allowed']})",
                                "user_flow": "Account with balance=100 → Try DEBIT 200 → See error",
                                "steps": [
                                    "1. Create account with balance=100 (via API)",
                                    "2. Navigate to /accounts/{account_id}",
                                    "3. Click 'New Transaction'",
                                    "4. Select type='DEBIT'",
                                    "5. Enter amount='200' (> balance)",
                                    "6. Click submit",
                                    "7. Wait for error"
                                ],
                                "expected_outcomes": [
                                    "Form submission fails",
                                    "Error message: 'Insufficient balance'",
                                    "Error code TXN-005 shown",
                                    "Account balance remains 100.00 (unchanged)",
                                    "Transaction marked 'FAILED' in history",
                                    f"No overdraft allowed (policy: {USER_DECISIONS['overdraft_allowed']})"
                                ],
                                "business_rules_validated": ["BR-TXN-005"]
                            },
                            {
                                "name": "test_credit_transaction_success",
                                "scenario": "happy_path",
                                "description": "User can perform CREDIT transaction",
                                "user_flow": "Navigate to account → New transaction → Select CREDIT → Enter amount → Submit → See increased balance",
                                "steps": [
                                    "1. Create account with balance=1000",
                                    "2. Navigate to /accounts/{account_id}",
                                    "3. Click 'New Transaction'",
                                    "4. Select type='CREDIT'",
                                    "5. Enter amount='500'",
                                    "6. Click submit"
                                ],
                                "expected_outcomes": [
                                    "Transaction completes",
                                    "Account balance updates to '1500.00'",
                                    "Transaction shows in history with type='CREDIT', status='COMPLETED'"
                                ],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_transaction_type_dropdown_limited",
                                "scenario": "business_rule",
                                "description": f"Transaction type dropdown only shows {USER_DECISIONS['transaction_types']}",
                                "user_flow": "Open transaction form → Check type dropdown options",
                                "steps": [
                                    "1. Navigate to /accounts/{account_id}",
                                    "2. Click 'New Transaction'",
                                    "3. Inspect type dropdown options"
                                ],
                                "expected_outcomes": [
                                    f"Dropdown contains exactly 2 options: {USER_DECISIONS['transaction_types']}",
                                    "No 'TRANSFER' option available",
                                    "User decision implemented correctly"
                                ],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_view_transaction_history",
                                "scenario": "happy_path",
                                "description": "User can view transaction history with audit trail",
                                "user_flow": "Account with transactions → Navigate to history → See all transactions with details",
                                "steps": [
                                    "1. Create account with 10 transactions (via API)",
                                    "2. Navigate to /accounts/{account_id}/transactions",
                                    "3. Observe transaction list"
                                ],
                                "expected_outcomes": [
                                    "All 10 transactions displayed",
                                    "Each transaction shows: date, type, amount, status, balance_after",
                                    "Transactions ordered by date (newest first)",
                                    "Audit trail visible (timestamp, user if applicable)",
                                    "Can filter or search transactions"
                                ],
                                "business_rules_validated": ["BR-TXN-004"]
                            },
                            {
                                "name": "test_transaction_closed_account_error",
                                "scenario": "error_case",
                                "description": "User cannot transact on closed account",
                                "user_flow": "Account with status='CLOSED' → Try transaction → See error",
                                "steps": [
                                    "1. Create account with status='CLOSED' (via API)",
                                    "2. Navigate to /accounts/{account_id}",
                                    "3. Attempt to click 'New Transaction' (button may be disabled)",
                                    "4. If form opens, submit transaction"
                                ],
                                "expected_outcomes": [
                                    "'New Transaction' button disabled with tooltip 'Account closed'",
                                    "If form submits, error: 'Cannot transact on closed account'",
                                    "Error code ACC-004 shown",
                                    "Account balance unchanged"
                                ],
                                "business_rules_validated": ["BR-ACC-004"]
                            }
                        ]
                    }
                ],
                "coverage_target": 0.80
            },
            "Authentication": {
                "e2e_tests": [
                    {
                        "file_path": "tests/e2e/test_auth_workflows.spec.ts",
                        "test_cases": [
                            {
                                "name": "test_login_success_flow",
                                "scenario": "happy_path",
                                "description": "User can login with valid credentials",
                                "user_flow": "Navigate to /login → Enter credentials → Submit → Redirected to dashboard",
                                "steps": [
                                    "1. Create user via API: username='testuser', password='SecurePass123!'",
                                    "2. Navigate to http://localhost:3001/login",
                                    "3. Fill input[name='username'] with 'testuser'",
                                    "4. Fill input[name='password'] with 'SecurePass123!'",
                                    "5. Click button[type='submit']",
                                    "6. Wait for navigation"
                                ],
                                "expected_outcomes": [
                                    "Login succeeds",
                                    "Redirected to /dashboard or /customers",
                                    "User sees welcome message or username in header",
                                    "Session token stored (check localStorage or cookies)",
                                    f"Session expires after {USER_DECISIONS['session_timeout_minutes']} minutes"
                                ],
                                "business_rules_validated": ["BR-AUTH-001", "BR-AUTH-003"]
                            },
                            {
                                "name": "test_login_invalid_credentials",
                                "scenario": "error_case",
                                "description": "User sees error for invalid credentials",
                                "user_flow": "Enter wrong password → Submit → See error",
                                "steps": [
                                    "1. Navigate to /login",
                                    "2. Fill username='testuser'",
                                    "3. Fill password='WrongPassword'",
                                    "4. Click submit",
                                    "5. Wait for error"
                                ],
                                "expected_outcomes": [
                                    "Login fails",
                                    "Error message: 'Invalid credentials' or 'Username or password incorrect'",
                                    "User remains on login page",
                                    "Can retry login",
                                    "No session created"
                                ],
                                "business_rules_validated": ["BR-AUTH-001"]
                            },
                            {
                                "name": "test_protected_route_redirects_to_login",
                                "scenario": "business_rule",
                                "description": "Unauthenticated user redirected to login when accessing protected route",
                                "user_flow": "No session → Try to access /customers → Redirected to /login",
                                "steps": [
                                    "1. Clear all cookies and localStorage (ensure no session)",
                                    "2. Navigate to /customers (protected route)",
                                    "3. Observe redirect"
                                ],
                                "expected_outcomes": [
                                    "Automatically redirected to /login",
                                    "After login, redirected back to /customers (return_url)",
                                    "Cannot access protected routes without authentication"
                                ],
                                "business_rules_validated": ["BR-AUTH-002"]
                            },
                            {
                                "name": "test_session_expiration_after_timeout",
                                "scenario": "business_rule",
                                "description": f"Session expires after {USER_DECISIONS['session_timeout_minutes']} minutes of inactivity",
                                "user_flow": f"Login → Wait {USER_DECISIONS['session_timeout_minutes']} min → Try to access page → Redirected to login",
                                "steps": [
                                    "1. Login successfully",
                                    "2. Wait or manually expire session (modify session expiry in DB or fast-forward time)",
                                    "3. Try to access /customers or make API call",
                                    "4. Observe behavior"
                                ],
                                "expected_outcomes": [
                                    "Session expires after timeout",
                                    "User redirected to /login",
                                    "Error message: 'Session expired. Please login again.'",
                                    "Must re-authenticate to continue"
                                ],
                                "business_rules_validated": ["BR-AUTH-003"]
                            },
                            {
                                "name": "test_logout_flow",
                                "scenario": "happy_path",
                                "description": "User can logout successfully",
                                "user_flow": "Login → Navigate to dashboard → Click logout → Redirected to login",
                                "steps": [
                                    "1. Login successfully",
                                    "2. Navigate to dashboard",
                                    "3. Click 'Logout' button (in header/menu)",
                                    "4. Wait for redirect"
                                ],
                                "expected_outcomes": [
                                    "Session destroyed (token removed from storage)",
                                    "Redirected to /login",
                                    "Cannot access protected routes anymore",
                                    "Welcome message or username no longer shown"
                                ],
                                "business_rules_validated": []
                            },
                            {
                                "name": "test_password_not_visible_in_forms",
                                "scenario": "business_rule",
                                "description": f"Password inputs are masked (BR-AUTH-004: no plaintext passwords)",
                                "user_flow": "View login form → Check password field type",
                                "steps": [
                                    "1. Navigate to /login",
                                    "2. Inspect password input field",
                                    "3. Verify type='password'"
                                ],
                                "expected_outcomes": [
                                    "Password field has type='password' (masked)",
                                    "Password not visible when typing",
                                    "Optional: toggle visibility button available",
                                    "Aligns with BR-AUTH-004 (password security)"
                                ],
                                "business_rules_validated": ["BR-AUTH-004"]
                            }
                        ]
                    }
                ],
                "coverage_target": 0.80
            }
        }
        return strategies.get(module, {
            "e2e_tests": [],
            "coverage_target": 0.80
        })

    return {}

def enrich_task_with_tests(task: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich a single implementation task with test specifications."""

    if task["type"] != "implementation":
        return task  # Only enrich implementation tasks

    module = task["module"]
    layer = task["implementation_layer"]
    business_rules = task.get("business_rules", [])

    # Generate test strategy based on layer
    if layer == "domain":
        test_strategy = get_domain_test_strategy(task, module, business_rules)
    elif layer == "use_case":
        test_strategy = get_use_case_test_strategy(task, module, business_rules)
    elif layer in ["infrastructure_db", "infrastructure_api", "infrastructure_frontend"]:
        test_strategy = get_infrastructure_test_strategy(task, module, layer)
    else:
        test_strategy = {}

    # Add test_strategy to task
    if test_strategy:
        task["test_strategy"] = test_strategy

        # Add validation commands based on layer
        validation_commands = []

        if layer == "domain":
            validation_commands.append(
                f"pytest tests/unit/domain/ -v --cov=backend/app/domain --cov-report=term-missing --cov-fail-under={int(test_strategy.get('coverage_target', 0.95) * 100)}"
            )
        elif layer == "use_case":
            validation_commands.append(
                f"pytest tests/unit/application/ -v --cov=backend/app/application --cov-report=term-missing --cov-fail-under={int(test_strategy.get('coverage_target', 0.90) * 100)}"
            )
        elif layer == "infrastructure_db":
            validation_commands.append(
                f"pytest tests/integration/infrastructure/repositories/ -v --cov=backend/app/infrastructure --cov-report=term-missing"
            )
        elif layer == "infrastructure_api":
            validation_commands.append(
                f"pytest tests/integration/infrastructure/api/ -v --cov=backend/app/infrastructure/api --cov-report=term-missing"
            )
        elif layer == "infrastructure_frontend":
            validation_commands.append(
                "npx playwright test tests/e2e/ --reporter=html"
            )

        task["validation_commands"] = validation_commands

        # Enhance acceptance criteria with test-specific criteria
        if "acceptance_criteria" not in task:
            task["acceptance_criteria"] = []

        if layer in ["domain", "use_case"]:
            task["acceptance_criteria"].extend([
                "All unit tests pass 100%",
                f"Code coverage >= {int(test_strategy.get('coverage_target', 0.90) * 100)}%",
                "All business rules validated via tests",
                "Test specifications implemented as written"
            ])
        elif layer in ["infrastructure_db", "infrastructure_api"]:
            task["acceptance_criteria"].extend([
                "All integration tests pass 100%",
                "API endpoints match OpenAPI spec exactly",
                "Error codes from error-codes.json used correctly",
                "Business rules enforced in API layer"
            ])
        elif layer == "infrastructure_frontend":
            task["acceptance_criteria"].extend([
                "E2E tests pass >= 95%",
                "All user flows tested end-to-end",
                "Error handling visible in UI",
                "Business rules validated in UI"
            ])

    return task

def main():
    """Main function to enrich tasks.json with test specifications."""

    print("=" * 80)
    print("QA TEST GENERATOR AGENT - Test Specification Enrichment")
    print("=" * 80)
    print()

    # Load tasks.json
    print("Loading tasks.json...")
    with open('docs/state/tasks.json', 'r') as f:
        tasks_data = json.load(f)

    total_tasks = len(tasks_data['tasks'])
    implementation_tasks = [t for t in tasks_data['tasks'] if t['type'] == 'implementation']

    print(f"Total tasks: {total_tasks}")
    print(f"Implementation tasks to enrich: {len(implementation_tasks)}")
    print()

    # Enrich each implementation task
    enriched_count = 0
    for i, task in enumerate(tasks_data['tasks']):
        if task['type'] == 'implementation':
            print(f"Enriching task {enriched_count + 1}/{len(implementation_tasks)}: {task['id']} ({task['module']} - {task['implementation_layer']})")
            tasks_data['tasks'][i] = enrich_task_with_tests(task)
            enriched_count += 1

    print()
    print(f"✅ Enriched {enriched_count} implementation tasks with test specifications")
    print()

    # Add enrichment metadata
    tasks_data['test_enrichment_metadata'] = {
        "enriched_at": datetime.now().isoformat(),
        "enriched_by": "qa-test-generator",
        "total_implementation_tasks": len(implementation_tasks),
        "enriched_tasks": enriched_count,
        "user_decisions_applied": USER_DECISIONS,
        "test_coverage_targets": {
            "domain": 0.95,
            "use_case": 0.90,
            "infrastructure": 0.85,
            "e2e": 0.80
        }
    }

    # Write enriched tasks.json
    print("Writing enriched tasks.json...")
    with open('docs/state/tasks.json', 'w') as f:
        json.dump(tasks_data, f, indent=2)

    print("✅ tasks.json updated successfully")
    print()

    # Verification
    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print()

    # Verify all implementation tasks have test_strategy
    tasks_without_tests = []
    for task in tasks_data['tasks']:
        if task['type'] == 'implementation' and 'test_strategy' not in task:
            tasks_without_tests.append(task['id'])

    if tasks_without_tests:
        print(f"❌ WARNING: {len(tasks_without_tests)} implementation tasks missing test_strategy:")
        for task_id in tasks_without_tests:
            print(f"   - {task_id}")
        print()
    else:
        print(f"✅ All {len(implementation_tasks)} implementation tasks have test_strategy")
        print()

    # Summary statistics
    print("Test Specification Summary:")
    print(f"  - Domain layer tasks: {len([t for t in implementation_tasks if t['implementation_layer'] == 'domain'])}")
    print(f"  - Use case layer tasks: {len([t for t in implementation_tasks if t['implementation_layer'] == 'use_case'])}")
    print(f"  - Infrastructure DB tasks: {len([t for t in implementation_tasks if t['implementation_layer'] == 'infrastructure_db'])}")
    print(f"  - Infrastructure API tasks: {len([t for t in implementation_tasks if t['implementation_layer'] == 'infrastructure_api'])}")
    print(f"  - Infrastructure Frontend tasks: {len([t for t in implementation_tasks if t['implementation_layer'] == 'infrastructure_frontend'])}")
    print()

    print("User Decisions Applied:")
    for key, value in USER_DECISIONS.items():
        print(f"  - {key}: {value}")
    print()

    print("=" * 80)
    print("✅ TEST ENRICHMENT COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Review enriched tasks.json")
    print("  2. Verify test specifications are comprehensive")
    print("  3. Proceed to PHASE 1 (Contract Generation)")
    print()

if __name__ == "__main__":
    main()
