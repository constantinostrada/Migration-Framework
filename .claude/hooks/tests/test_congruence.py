#!/usr/bin/env python3
"""
Unit tests for CongruenceValidator.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.congruence import CongruenceValidator, FieldInfo


class TestCongruenceValidator(unittest.TestCase):
    """Tests for CongruenceValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.validator = CongruenceValidator(self.test_dir)

        # Create test directories
        (Path(self.test_dir) / "src" / "frontend" / "app").mkdir(parents=True)
        (Path(self.test_dir) / "src" / "backend" / "app" / "schemas").mkdir(parents=True)
        (Path(self.test_dir) / "docs" / "design" / "database").mkdir(parents=True)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_extract_form_fields_from_tsx(self):
        """Test extracting fields from TSX form."""
        tsx_content = """
'use client'
import { useState } from 'react'

export default function CustomerForm() {
    const [formData, setFormData] = useState({
        title: 'Mr',
        name: '',
        email: '',
        date_of_birth: '',
        address: ''
    })

    return (
        <form>
            <input name="name" required />
            <input name="email" type="email" />
            <input name="date_of_birth" type="date" />
        </form>
    )
}
"""
        tsx_path = Path(self.test_dir) / "src" / "frontend" / "app" / "form.tsx"
        tsx_path.write_text(tsx_content)

        fields = self.validator.extract_form_fields_from_tsx("src/frontend/app/form.tsx")

        self.assertIn("title", fields)
        self.assertIn("name", fields)
        self.assertIn("email", fields)
        self.assertIn("date_of_birth", fields)

    def test_extract_pydantic_fields(self):
        """Test extracting fields from Pydantic schema."""
        pydantic_content = """
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class CustomerCreate(BaseModel):
    title: str
    name: str = Field(..., min_length=1)
    email: str
    date_of_birth: date
    phone: Optional[str] = None
    address: str
"""
        schema_path = Path(self.test_dir) / "src" / "backend" / "app" / "schemas" / "customer.py"
        schema_path.write_text(pydantic_content)

        fields = self.validator.extract_pydantic_fields("src/backend/app/schemas/customer.py", "CustomerCreate")

        self.assertIn("title", fields)
        self.assertIn("name", fields)
        self.assertIn("date_of_birth", fields)
        self.assertIn("phone", fields)

        # Check required status
        self.assertTrue(fields["name"].required)
        self.assertFalse(fields["phone"].required)

    def test_compare_fields_matching(self):
        """Test field comparison with matching fields."""
        frontend = {
            "name": FieldInfo(name="name", type="string", required=True, layer="frontend"),
            "email": FieldInfo(name="email", type="string", required=True, layer="frontend"),
            "date_of_birth": FieldInfo(name="date_of_birth", type="string", required=True, layer="frontend")
        }

        backend = {
            "name": FieldInfo(name="name", type="str", required=True, layer="backend"),
            "email": FieldInfo(name="email", type="EmailStr", required=True, layer="backend"),
            "date_of_birth": FieldInfo(name="date_of_birth", type="date", required=True, layer="backend")
        }

        mismatches = self.validator.compare_fields(frontend, backend)

        # Should have no errors (only possible warnings)
        errors = [m for m in mismatches if m.severity == "error"]
        self.assertEqual(len(errors), 0)

    def test_compare_fields_name_mismatch(self):
        """Test field comparison with name mismatch."""
        frontend = {
            "dob": FieldInfo(name="dob", type="string", required=True, layer="frontend"),
            "name": FieldInfo(name="name", type="string", required=True, layer="frontend")
        }

        backend = {
            "date_of_birth": FieldInfo(name="date_of_birth", type="date", required=True, layer="backend"),
            "name": FieldInfo(name="name", type="str", required=True, layer="backend")
        }

        mismatches = self.validator.compare_fields(frontend, backend)

        # Should detect the dob -> date_of_birth mismatch
        self.assertTrue(any(m.field_name == "dob" for m in mismatches))

    def test_compare_fields_missing_in_backend(self):
        """Test field comparison with field missing in backend."""
        frontend = {
            "name": FieldInfo(name="name", type="string", required=True, layer="frontend"),
            "extra_field": FieldInfo(name="extra_field", type="string", required=True, layer="frontend")
        }

        backend = {
            "name": FieldInfo(name="name", type="str", required=True, layer="backend")
        }

        mismatches = self.validator.compare_fields(frontend, backend)

        # Should detect missing field
        missing = [m for m in mismatches if m.issue_type == "missing_in_backend"]
        self.assertTrue(len(missing) > 0)

    def test_compare_fields_missing_in_frontend(self):
        """Test field comparison with required field missing in frontend."""
        frontend = {
            "name": FieldInfo(name="name", type="string", required=True, layer="frontend")
        }

        backend = {
            "name": FieldInfo(name="name", type="str", required=True, layer="backend"),
            "required_field": FieldInfo(name="required_field", type="str", required=True, layer="backend")
        }

        mismatches = self.validator.compare_fields(frontend, backend)

        # Should detect missing required field in frontend
        missing = [m for m in mismatches if m.issue_type == "missing_in_frontend"]
        self.assertTrue(len(missing) > 0)

    def test_extract_sql_columns(self):
        """Test extracting columns from SQL schema."""
        sql_content = """
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_number VARCHAR(10) NOT NULL UNIQUE,
    title VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    date_of_birth DATE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(200) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
        sql_path = Path(self.test_dir) / "docs" / "design" / "database" / "schema.sql"
        sql_path.write_text(sql_content)

        fields = self.validator.extract_sql_columns("docs/design/database/schema.sql", "customers")

        self.assertIn("name", fields)
        self.assertIn("email", fields)
        self.assertIn("date_of_birth", fields)

        # Check required status
        self.assertTrue(fields["name"].required)
        self.assertFalse(fields["phone"].required)

    def test_validate_entity(self):
        """Test full entity validation."""
        # Create frontend form
        tsx_content = """
const [formData, setFormData] = useState({
    name: '',
    email: '',
    date_of_birth: ''
})
"""
        tsx_path = Path(self.test_dir) / "src" / "frontend" / "app" / "form.tsx"
        tsx_path.write_text(tsx_content)

        # Create backend schema
        pydantic_content = """
class CustomerCreate(BaseModel):
    name: str
    email: str
    date_of_birth: date
"""
        schema_path = Path(self.test_dir) / "src" / "backend" / "app" / "schemas" / "customer.py"
        schema_path.write_text(pydantic_content)

        is_valid, mismatches = self.validator.validate_entity(
            entity_name="Customer",
            frontend_file="src/frontend/app/form.tsx",
            backend_schema_file="src/backend/app/schemas/customer.py",
            schema_name="CustomerCreate"
        )

        # Should be valid since fields match
        self.assertTrue(is_valid)

    def test_get_blocking_issues(self):
        """Test getting blocking issues from issues file."""
        issues_content = """
# Congruence Issues

## Customer

- [ ] **Name Mismatch**: `dob` (frontend) -> `date_of_birth` (backend)
- [x] **Missing in Backend**: `extra_field` resolved
"""
        issues_path = Path(self.test_dir) / "docs" / "design" / "congruence"
        issues_path.mkdir(parents=True)
        (issues_path / "issues.md").write_text(issues_content)

        issues = self.validator.get_blocking_issues()

        # Should have one unresolved issue
        self.assertEqual(len(issues), 1)
        self.assertIn("Name Mismatch", issues[0])


class TestFieldNameNormalization(unittest.TestCase):
    """Tests for field name normalization."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.validator = CongruenceValidator(self.test_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_common_name_mappings(self):
        """Test that common name variations are detected."""
        frontend = {
            "dob": FieldInfo(name="dob", type="string", required=True, layer="frontend")
        }

        backend = {
            "date_of_birth": FieldInfo(name="date_of_birth", type="date", required=True, layer="backend")
        }

        mismatches = self.validator.compare_fields(frontend, backend)

        # Should detect the mapping and flag as name mismatch
        name_mismatches = [m for m in mismatches if m.issue_type == "name_mismatch"]
        self.assertTrue(len(name_mismatches) > 0 or
                       any(m.field_name == "dob" for m in mismatches))


if __name__ == "__main__":
    unittest.main()
