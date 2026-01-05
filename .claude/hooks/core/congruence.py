#!/usr/bin/env python3
"""
Congruence Validator - Validates consistency between frontend, backend, and database.
Extracts fields from actual code and compares them.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class FieldInfo:
    """Information about a field in any layer."""
    name: str
    type: str
    required: bool = True
    layer: str = ""  # frontend, backend, database


@dataclass
class CongruenceMismatch:
    """A mismatch between layers."""
    field_name: str
    issue_type: str  # missing, type_mismatch, required_mismatch
    frontend_value: Optional[str] = None
    backend_value: Optional[str] = None
    database_value: Optional[str] = None
    severity: str = "error"  # error, warning


class CongruenceValidator:
    """Validates congruence between frontend, backend, and database layers."""

    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.validation_results_file = self.base_path / "docs" / "design" / "congruence" / "validation-results.json"
        self.issues_file = self.base_path / "docs" / "design" / "congruence" / "issues.md"

    # ==================== Frontend Field Extraction ====================

    def extract_form_fields_from_tsx(self, file_path: str) -> Dict[str, FieldInfo]:
        """
        Extract form fields from a TypeScript/TSX file.

        Supports multiple form libraries:
        - Plain React (useState, controlled inputs)
        - React Hook Form (register, useForm, Controller)
        - Formik (Field, useFormik, Formik component)
        - Zod schemas (z.object, z.string, etc.)
        """
        full_path = self.base_path / file_path
        if not full_path.exists():
            return {}

        with open(full_path, 'r') as f:
            content = f.read()

        fields = {}

        # ==================== Plain React Patterns ====================

        # Pattern 1: useState with formData object (multiple variations)
        # const [formData, setFormData] = useState({ field1: '', field2: '' })
        # useState<FormData>({ field1: '', field2: '' })
        for pattern in [
            r'useState[<\(][^{]*\{([^}]+)\}',
            r'useState\s*<[^>]+>\s*\(\s*\{([^}]+)\}',
        ]:
            form_data_match = re.search(pattern, content)
            if form_data_match:
                form_fields_str = form_data_match.group(1)
                field_matches = re.findall(r'(\w+)\s*:', form_fields_str)
                for field in field_matches:
                    if field not in fields:
                        fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 2: Input elements with name attribute (multiple input types)
        # <input name="fieldName" />, <Input name="..." />, <TextField name="..." />
        input_patterns = [
            r'<[Ii]nput[^>]*name=["\']([^"\']+)["\']',
            r'<TextField[^>]*name=["\']([^"\']+)["\']',
            r'<Select[^>]*name=["\']([^"\']+)["\']',
            r'<textarea[^>]*name=["\']([^"\']+)["\']',
        ]
        for pattern in input_patterns:
            for field in re.findall(pattern, content):
                if field not in fields:
                    fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 3: FormData/data object access - formData.fieldName, data.fieldName
        for pattern in [r'formData\.(\w+)', r'\bdata\.(\w+)', r'values\.(\w+)']:
            for field in re.findall(pattern, content):
                if field not in fields and field not in ['map', 'filter', 'reduce', 'forEach', 'length']:
                    fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 4: API call payload (fetch, axios, custom api)
        # await api.post('/endpoint', { field1: value1, field2: value2 })
        # fetch('/api', { body: JSON.stringify({ field1, field2 }) })
        payload_patterns = [
            r'\.(?:post|put|patch)\s*\([^,]+,\s*\{([^}]+)\}',
            r'JSON\.stringify\s*\(\s*\{([^}]+)\}',
            r'body:\s*\{([^}]+)\}',
        ]
        for pattern in payload_patterns:
            api_payload = re.search(pattern, content)
            if api_payload:
                payload_str = api_payload.group(1)
                # Handle both { field: value } and { field } shorthand
                payload_fields = re.findall(r'(\w+)(?:\s*:|,|\s*$)', payload_str)
                for field in payload_fields:
                    if field not in fields and field not in ['method', 'headers', 'credentials']:
                        fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # ==================== React Hook Form Patterns ====================

        # Pattern 5: register("fieldName") or register('fieldName')
        register_fields = re.findall(r'register\s*\(\s*["\']([^"\']+)["\']', content)
        for field in register_fields:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 6: {...register("fieldName")} spread
        spread_register = re.findall(r'\{\s*\.\.\.\s*register\s*\(\s*["\']([^"\']+)["\']', content)
        for field in spread_register:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 7: Controller with name prop
        # <Controller name="fieldName" control={control} />
        controller_fields = re.findall(r'<Controller[^>]*name=["\']([^"\']+)["\']', content)
        for field in controller_fields:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 8: watch("fieldName"), getValues("fieldName"), setValue("fieldName")
        rhf_access = re.findall(r'(?:watch|getValues|setValue|trigger|setError|clearErrors)\s*\(\s*["\']([^"\']+)["\']', content)
        for field in rhf_access:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 9: useForm defaultValues
        # useForm({ defaultValues: { field1: '', field2: '' } })
        default_values_match = re.search(r'defaultValues\s*:\s*\{([^}]+)\}', content)
        if default_values_match:
            dv_str = default_values_match.group(1)
            dv_fields = re.findall(r'(\w+)\s*:', dv_str)
            for field in dv_fields:
                if field not in fields:
                    fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # ==================== Formik Patterns ====================

        # Pattern 10: <Field name="fieldName" />
        formik_fields = re.findall(r'<Field[^>]*name=["\']([^"\']+)["\']', content)
        for field in formik_fields:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 11: <FastField name="fieldName" />
        fast_fields = re.findall(r'<FastField[^>]*name=["\']([^"\']+)["\']', content)
        for field in fast_fields:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 12: useFormik initialValues
        # useFormik({ initialValues: { field1: '', field2: '' } })
        initial_values_match = re.search(r'initialValues\s*:\s*\{([^}]+)\}', content)
        if initial_values_match:
            iv_str = initial_values_match.group(1)
            iv_fields = re.findall(r'(\w+)\s*:', iv_str)
            for field in iv_fields:
                if field not in fields:
                    fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 13: Formik component initialValues prop
        # <Formik initialValues={{ field1: '', field2: '' }}>
        formik_component = re.search(r'<Formik[^>]*initialValues=\{\{([^}]+)\}\}', content)
        if formik_component:
            fc_str = formik_component.group(1)
            fc_fields = re.findall(r'(\w+)\s*:', fc_str)
            for field in fc_fields:
                if field not in fields:
                    fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 14: formik.values.fieldName, formik.errors.fieldName
        formik_access = re.findall(r'formik\.(?:values|errors|touched)\.(\w+)', content)
        for field in formik_access:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # ==================== Zod Schema Patterns ====================

        # Pattern 15: z.object({ fieldName: z.string() })
        zod_object = re.search(r'z\.object\s*\(\s*\{([^}]+)\}', content)
        if zod_object:
            zod_str = zod_object.group(1)
            zod_fields = re.findall(r'(\w+)\s*:\s*z\.', zod_str)
            for field in zod_fields:
                if field not in fields:
                    fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # Pattern 16: Multi-line zod schema
        # const schema = z.object({
        #   fieldName: z.string(),
        # })
        zod_multiline = re.findall(r'(\w+)\s*:\s*z\.(?:string|number|boolean|date|array|object|enum)', content)
        for field in zod_multiline:
            if field not in fields:
                fields[field] = FieldInfo(name=field, type="string", layer="frontend")

        # ==================== Detect Required Fields ====================

        # HTML required attribute
        required_html = set(re.findall(r'<[^>]*name=["\'](\w+)["\'][^>]*required', content))
        for field_name in required_html:
            if field_name in fields:
                fields[field_name].required = True

        # React Hook Form required validation
        # register("fieldName", { required: true })
        rhf_required = re.findall(r'register\s*\(\s*["\']([^"\']+)["\'][^)]*required\s*:\s*true', content)
        for field_name in rhf_required:
            if field_name in fields:
                fields[field_name].required = True

        # Zod required (non-optional fields)
        # Note: In Zod, fields are required by default unless .optional() is added
        zod_optional = set(re.findall(r'(\w+)\s*:\s*z\.[^,]+\.optional\(\)', content))
        for field_name in fields:
            if field_name not in zod_optional:
                # Check if it's a zod field and not marked optional
                if re.search(rf'{field_name}\s*:\s*z\.', content):
                    fields[field_name].required = True

        return fields

    def extract_typescript_interface(self, file_path: str, interface_name: str) -> Dict[str, FieldInfo]:
        """Extract fields from a TypeScript interface."""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return {}

        with open(full_path, 'r') as f:
            content = f.read()

        fields = {}

        # Find the interface
        interface_pattern = rf'(?:interface|type)\s+{interface_name}\s*(?:=\s*)?\{{\s*([^}}]+)\}}'
        match = re.search(interface_pattern, content, re.DOTALL)

        if match:
            interface_body = match.group(1)
            # Parse fields: fieldName?: Type;
            field_pattern = r'(\w+)(\?)?:\s*([^;\n]+)'
            for m in re.finditer(field_pattern, interface_body):
                name = m.group(1)
                optional = m.group(2) == '?'
                field_type = m.group(3).strip()
                fields[name] = FieldInfo(
                    name=name,
                    type=field_type,
                    required=not optional,
                    layer="frontend"
                )

        return fields

    # ==================== Backend Field Extraction ====================

    def extract_pydantic_fields(self, file_path: str, schema_name: Optional[str] = None) -> Dict[str, FieldInfo]:
        """Extract fields from Pydantic schemas."""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return {}

        with open(full_path, 'r') as f:
            content = f.read()

        fields = {}

        # Find class definition
        if schema_name:
            class_pattern = rf'class\s+{schema_name}\s*\([^)]*\)\s*:\s*((?:\n\s+[^\n]+)+)'
        else:
            class_pattern = r'class\s+(\w+)\s*\([^)]*BaseModel[^)]*\)\s*:\s*((?:\n\s+[^\n]+)+)'

        for match in re.finditer(class_pattern, content):
            if schema_name:
                class_body = match.group(1)
            else:
                class_body = match.group(2)

            # Parse fields: field_name: Type = Field(...) or field_name: Type
            field_pattern = r'(\w+)\s*:\s*(Optional\[)?([^=\n]+)(?:\s*=\s*([^\n]+))?'

            for field_match in re.finditer(field_pattern, class_body):
                name = field_match.group(1)
                is_optional = field_match.group(2) is not None
                field_type = field_match.group(3).strip()
                default = field_match.group(4)

                # Skip if it's a method or validator
                if name.startswith('_') or name in ['model_config', 'Config']:
                    continue

                # Determine if required
                required = not is_optional and (default is None or '...' in str(default))

                fields[name] = FieldInfo(
                    name=name,
                    type=field_type,
                    required=required,
                    layer="backend"
                )

        return fields

    # ==================== Database Field Extraction ====================

    def extract_sqlalchemy_fields(self, file_path: str, model_name: Optional[str] = None) -> Dict[str, FieldInfo]:
        """Extract fields from SQLAlchemy models."""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return {}

        with open(full_path, 'r') as f:
            content = f.read()

        fields = {}

        # Find model class
        if model_name:
            class_pattern = rf'class\s+{model_name}\s*\([^)]*\)\s*:((?:\n\s+[^\n]+)+)'
        else:
            class_pattern = r'class\s+(\w+)\s*\([^)]*(?:Base|Model)[^)]*\)\s*:((?:\n\s+[^\n]+)+)'

        for match in re.finditer(class_pattern, content):
            class_body = match.group(1) if model_name else match.group(2)

            # Parse Column definitions
            column_pattern = r'(\w+)\s*=\s*(?:mapped_column|Column)\s*\(([^)]+)\)'

            for col_match in re.finditer(column_pattern, class_body):
                name = col_match.group(1)
                col_def = col_match.group(2)

                # Extract type
                type_match = re.search(r'(String|Integer|Boolean|Float|DateTime|Date|UUID|Numeric|Text|DECIMAL)', col_def)
                col_type = type_match.group(1) if type_match else "Unknown"

                # Check if nullable
                nullable = 'nullable=True' in col_def or 'nullable = True' in col_def

                fields[name] = FieldInfo(
                    name=name,
                    type=col_type,
                    required=not nullable,
                    layer="database"
                )

        return fields

    def extract_sql_columns(self, file_path: str, table_name: Optional[str] = None) -> Dict[str, FieldInfo]:
        """Extract columns from SQL CREATE TABLE statements."""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return {}

        with open(full_path, 'r') as f:
            content = f.read()

        fields = {}

        # Find CREATE TABLE
        if table_name:
            table_pattern = rf'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{table_name}\s*\(([^;]+)\)'
        else:
            table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([^;]+)\)'

        for match in re.finditer(table_pattern, content, re.IGNORECASE | re.DOTALL):
            if table_name:
                table_body = match.group(1)
            else:
                table_body = match.group(2)

            # Parse column definitions
            lines = table_body.split('\n')
            for line in lines:
                line = line.strip().rstrip(',')
                if not line or line.upper().startswith(('PRIMARY', 'FOREIGN', 'CONSTRAINT', 'UNIQUE', 'INDEX', 'CHECK')):
                    continue

                # Parse: column_name TYPE [NOT NULL] [DEFAULT ...]
                col_match = re.match(r'(\w+)\s+(\w+)(?:\([^)]+\))?\s*(.*)', line)
                if col_match:
                    name = col_match.group(1)
                    col_type = col_match.group(2)
                    constraints = col_match.group(3).upper()

                    required = 'NOT NULL' in constraints

                    fields[name] = FieldInfo(
                        name=name,
                        type=col_type,
                        required=required,
                        layer="database"
                    )

        return fields

    # ==================== Comparison Logic ====================

    def compare_fields(self, frontend: Dict[str, FieldInfo], backend: Dict[str, FieldInfo],
                       database: Optional[Dict[str, FieldInfo]] = None) -> List[CongruenceMismatch]:
        """Compare fields between layers and find mismatches."""
        mismatches = []

        # Get all unique field names
        all_fields: Set[str] = set(frontend.keys()) | set(backend.keys())
        if database:
            all_fields |= set(database.keys())

        # Field name mappings (common transformations)
        name_mappings = {
            'dob': 'date_of_birth',
            'dateOfBirth': 'date_of_birth',
            'date_of_birth': 'date_of_birth',
            'firstName': 'first_name',
            'lastName': 'last_name',
            'createdAt': 'created_at',
            'updatedAt': 'updated_at',
        }

        def normalize_name(name: str) -> str:
            """Normalize field name for comparison."""
            return name_mappings.get(name, name)

        # Check frontend vs backend
        for field_name in frontend.keys():
            normalized = normalize_name(field_name)

            # Find matching backend field
            backend_field = backend.get(field_name) or backend.get(normalized)

            if not backend_field:
                # Check if it's mapped differently
                possible_names = [k for k, v in name_mappings.items() if v == normalized]
                for pn in possible_names:
                    if pn in backend:
                        backend_field = backend[pn]
                        break

            if not backend_field:
                mismatches.append(CongruenceMismatch(
                    field_name=field_name,
                    issue_type="missing_in_backend",
                    frontend_value=frontend[field_name].type,
                    severity="error" if frontend[field_name].required else "warning"
                ))
            elif field_name != normalized and field_name not in backend:
                # Name mismatch
                mismatches.append(CongruenceMismatch(
                    field_name=field_name,
                    issue_type="name_mismatch",
                    frontend_value=field_name,
                    backend_value=normalized,
                    severity="error"
                ))

        # Check backend fields missing in frontend
        for field_name in backend.keys():
            normalized = normalize_name(field_name)
            if field_name not in frontend and normalized not in frontend:
                # Only report if it's a user-input field (not auto-generated)
                if field_name not in ['id', 'created_at', 'updated_at', 'deleted_at',
                                      'customer_number', 'account_number', 'credit_score']:
                    if backend[field_name].required:
                        mismatches.append(CongruenceMismatch(
                            field_name=field_name,
                            issue_type="missing_in_frontend",
                            backend_value=backend[field_name].type,
                            severity="error"
                        ))

        return mismatches

    def validate_entity(self, entity_name: str,
                        frontend_file: str, frontend_type: str = "form",
                        backend_schema_file: str = None, schema_name: str = None,
                        database_file: str = None, table_name: str = None) -> Tuple[bool, List[CongruenceMismatch]]:
        """
        Validate congruence for a single entity across all layers.

        Args:
            entity_name: Name of the entity (e.g., "Customer")
            frontend_file: Path to the frontend form/component file
            frontend_type: "form" for TSX form, "interface" for TypeScript interface
            backend_schema_file: Path to the Pydantic schema file
            schema_name: Name of the Pydantic schema class
            database_file: Path to SQL schema or SQLAlchemy model
            table_name: Name of the database table

        Returns:
            Tuple of (is_valid, list of mismatches)
        """
        # Extract frontend fields
        if frontend_type == "form":
            frontend_fields = self.extract_form_fields_from_tsx(frontend_file)
        else:
            frontend_fields = self.extract_typescript_interface(frontend_file, entity_name)

        # Extract backend fields
        backend_fields = {}
        if backend_schema_file:
            backend_fields = self.extract_pydantic_fields(backend_schema_file, schema_name)

        # Extract database fields
        database_fields = None
        if database_file:
            if database_file.endswith('.sql'):
                database_fields = self.extract_sql_columns(database_file, table_name)
            else:
                database_fields = self.extract_sqlalchemy_fields(database_file, entity_name)

        # Compare
        mismatches = self.compare_fields(frontend_fields, backend_fields, database_fields)

        # Filter out errors only
        errors = [m for m in mismatches if m.severity == "error"]

        return len(errors) == 0, mismatches

    def run_full_validation(self) -> Dict:
        """Run validation on all entities based on design documents."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "entities": {},
            "summary": {
                "total_entities": 0,
                "valid_entities": 0,
                "total_mismatches": 0,
                "errors": 0,
                "warnings": 0
            }
        }

        # Find all frontend forms in teller directory
        frontend_dir = self.base_path / "src" / "frontend" / "app"
        if not frontend_dir.exists():
            return results

        # Entity configuration - maps entity to its files
        entity_config = self._detect_entities()

        for entity_name, config in entity_config.items():
            is_valid, mismatches = self.validate_entity(
                entity_name=entity_name,
                frontend_file=config.get("frontend_file", ""),
                backend_schema_file=config.get("backend_schema_file", ""),
                schema_name=config.get("schema_name"),
                database_file=config.get("database_file"),
                table_name=config.get("table_name")
            )

            results["entities"][entity_name] = {
                "valid": is_valid,
                "mismatches": [asdict(m) for m in mismatches],
                "error_count": len([m for m in mismatches if m.severity == "error"]),
                "warning_count": len([m for m in mismatches if m.severity == "warning"])
            }

            results["summary"]["total_entities"] += 1
            if is_valid:
                results["summary"]["valid_entities"] += 1
            results["summary"]["total_mismatches"] += len(mismatches)
            results["summary"]["errors"] += results["entities"][entity_name]["error_count"]
            results["summary"]["warnings"] += results["entities"][entity_name]["warning_count"]

        # Save results
        self._save_results(results)

        return results

    def _detect_entities(self) -> Dict[str, Dict]:
        """Auto-detect entities and their file locations.

        First tries to read from docs/analysis/entities/entities.json (dynamic).
        Falls back to common entity names if file doesn't exist.
        """
        entities = {}

        # Try to load entities from analysis phase output (dynamic detection)
        entities_json_path = self.base_path / "docs" / "analysis" / "entities" / "entities.json"
        entity_names = []

        if entities_json_path.exists():
            try:
                with open(entities_json_path, 'r') as f:
                    entities_data = json.load(f)

                # Handle different JSON structures
                if isinstance(entities_data, dict):
                    if "entities" in entities_data:
                        # Format: {"entities": [{"name": "Customer"}, ...]}
                        for e in entities_data.get("entities", []):
                            if isinstance(e, dict) and "name" in e:
                                entity_names.append(e["name"])
                            elif isinstance(e, str):
                                entity_names.append(e)
                    else:
                        # Format: {"Customer": {...}, "Account": {...}}
                        entity_names = list(entities_data.keys())
                elif isinstance(entities_data, list):
                    # Format: ["Customer", "Account"] or [{"name": "Customer"}, ...]
                    for e in entities_data:
                        if isinstance(e, dict) and "name" in e:
                            entity_names.append(e["name"])
                        elif isinstance(e, str):
                            entity_names.append(e)
            except (json.JSONDecodeError, IOError):
                pass  # Fall back to defaults

        # Fall back to common entities if none found
        if not entity_names:
            entity_names = ["Customer", "Account", "Transaction", "User"]

        for entity in entity_names:
            entity_lower = entity.lower()

            # Find frontend form
            frontend_paths = [
                f"src/frontend/app/teller/{entity_lower}s/new/page.tsx",
                f"src/frontend/app/{entity_lower}s/new/page.tsx",
                f"src/frontend/components/{entity}Form.tsx",
            ]

            frontend_file = None
            for fp in frontend_paths:
                if (self.base_path / fp).exists():
                    frontend_file = fp
                    break

            # Find backend schema
            backend_paths = [
                f"src/backend/app/schemas/{entity_lower}.py",
                f"src/backend/app/schemas.py",
            ]

            backend_file = None
            for bp in backend_paths:
                if (self.base_path / bp).exists():
                    backend_file = bp
                    break

            # Find database schema/model
            database_paths = [
                f"src/backend/app/models/{entity_lower}.py",
                "docs/design/database/schema.sql",
            ]

            database_file = None
            for dp in database_paths:
                if (self.base_path / dp).exists():
                    database_file = dp
                    break

            if frontend_file or backend_file:
                entities[entity] = {
                    "frontend_file": frontend_file,
                    "backend_schema_file": backend_file,
                    "schema_name": f"{entity}Create",
                    "database_file": database_file,
                    "table_name": f"{entity_lower}s"
                }

        return entities

    def _save_results(self, results: Dict):
        """Save validation results to files."""
        # Ensure directory exists
        self.validation_results_file.parent.mkdir(parents=True, exist_ok=True)

        # Save JSON results
        with open(self.validation_results_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Generate issues markdown
        self._generate_issues_file(results)

    def _generate_issues_file(self, results: Dict):
        """Generate the issues.md file."""
        content = f"""# Congruence Issues

**Last Validated**: {results['timestamp']}
**Total Entities**: {results['summary']['total_entities']}
**Valid Entities**: {results['summary']['valid_entities']}
**Total Mismatches**: {results['summary']['total_mismatches']}

---

"""

        for entity_name, entity_results in results.get("entities", {}).items():
            content += f"## {entity_name}\n\n"

            if entity_results["valid"]:
                content += "- [x] All fields aligned\n\n"
            else:
                for mismatch in entity_results.get("mismatches", []):
                    checkbox = "[ ]" if mismatch["severity"] == "error" else "[x]"
                    issue_type = mismatch["issue_type"].replace("_", " ").title()

                    if mismatch["issue_type"] == "name_mismatch":
                        content += f"- {checkbox} **{issue_type}**: `{mismatch['frontend_value']}` (frontend) → `{mismatch['backend_value']}` (backend)\n"
                    elif mismatch["issue_type"] == "missing_in_backend":
                        content += f"- {checkbox} **{issue_type}**: `{mismatch['field_name']}` not found in backend schema\n"
                    elif mismatch["issue_type"] == "missing_in_frontend":
                        content += f"- {checkbox} **{issue_type}**: `{mismatch['field_name']}` (required in backend) missing from frontend form\n"
                    else:
                        content += f"- {checkbox} **{issue_type}**: `{mismatch['field_name']}`\n"

                content += "\n"

        content += """---

## Resolution Instructions

1. For **Name Mismatch** errors:
   - Update the frontend to use the correct field name that matches the backend schema

2. For **Missing in Backend** errors:
   - Either add the field to the backend schema, or remove it from the frontend

3. For **Missing in Frontend** errors:
   - Add the required field to the frontend form

After fixing issues, mark them as resolved by changing `- [ ]` to `- [x]`
Then run `/migration validate` again to verify.
"""

        with open(self.issues_file, 'w') as f:
            f.write(content)

    def get_blocking_issues(self) -> List[str]:
        """Get list of blocking issues that prevent phase advancement."""
        if not self.issues_file.exists():
            return ["Validation not run - run /migration validate first"]

        with open(self.issues_file, 'r') as f:
            content = f.read()

        # Find unchecked boxes (unresolved issues)
        issues = re.findall(r'- \[ \] \*\*([^*]+)\*\*: ([^\n]+)', content)

        return [f"{issue_type}: {description}" for issue_type, description in issues]
