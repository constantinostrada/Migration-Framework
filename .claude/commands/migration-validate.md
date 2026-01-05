# Migration Validate Command

You are running a congruence validation check. This command executes REAL validation using the CongruenceValidator.

## Step 1: Check Prerequisites

Verify current phase allows validation:
```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager
sm = StateManager('.')
state = sm.get_project_state()
if state:
    phase = state.get('current_phase', 'IDLE')
    print(f'PHASE:{phase}')
else:
    print('PHASE:NONE')
"
```

- If IDLE/NONE: Warn that no migration is active
- If ANALYSIS/FEEDBACK: Validate design documents only
- If DESIGN/CONSTRUCTION/TESTING: Run full validation

## Step 2: Execute Validation

### Option A: Design Document Validation (DESIGN phase)

Check design documents exist and are internally consistent:

```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.deliverables import DeliverableChecker
dc = DeliverableChecker('.')
complete, missing_req, missing_opt = dc.check_phase_deliverables('DESIGN')
print('COMPLETE:' + str(complete))
for m in missing_req:
    print('MISSING:' + m)
"
```

Then read and compare:
- `docs/design/backend/api-contracts.json`
- `docs/design/frontend/components.json`
- `docs/design/database/schema.json`

### Option B: Full Code Validation (CONSTRUCTION phase)

Execute the CongruenceValidator on actual source code:

```bash
python3 << 'PYEOF'
import sys
import json
sys.path.insert(0, '.claude/hooks')
from core.congruence import CongruenceValidator

validator = CongruenceValidator('.')
results = validator.run_full_validation()

print("=" * 60)
print("VALIDATION RESULTS")
print("=" * 60)
print(f"Entities validated: {results['summary']['total_entities']}")
print(f"Valid entities: {results['summary']['valid_entities']}")
print(f"Total mismatches: {results['summary']['total_mismatches']}")
print(f"Errors: {results['summary']['errors']}")
print(f"Warnings: {results['summary']['warnings']}")
print("=" * 60)

for entity, data in results.get('entities', {}).items():
    status = "✅" if data['valid'] else "❌"
    print(f"{status} {entity}: {data['error_count']} errors, {data['warning_count']} warnings")
    for m in data.get('mismatches', []):
        print(f"   - {m['issue_type']}: {m['field_name']}")

print("=" * 60)
print(f"Results saved to: docs/design/congruence/validation-results.json")
print(f"Issues saved to: docs/design/congruence/issues.md")
PYEOF
```

## Step 3: Read and Present Results

After running validation, read the generated files:

1. Read `docs/design/congruence/validation-results.json` for structured data
2. Read `docs/design/congruence/issues.md` for human-readable issues

Present results:

```
🔍 VALIDACIÓN DE CONGRUENCIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESUMEN
- Entidades validadas: [N]
- Entidades válidas: [X]
- Errores totales: [Y]
- Advertencias: [Z]

## Por Entidad

| Entidad | Estado | Errores | Advertencias |
|---------|--------|---------|--------------|
| Customer | ✅/❌ | 0 | 0 |
| Account | ✅/❌ | 0 | 0 |
| ... | ... | ... | ... |

## Issues Encontrados

[If errors > 0]
❌ ERRORES (bloquean avance):
- [entity]: [field] - [issue_type]
- ...

[If warnings > 0]
⚠️ ADVERTENCIAS (no bloquean):
- [entity]: [field] - [issue_type]
- ...

## Resultado Final

[If errors == 0]
✅ VALIDACIÓN EXITOSA
No hay errores de congruencia. Puede continuar.

[If errors > 0]
❌ VALIDACIÓN FALLIDA
Hay [N] errores que deben corregirse antes de continuar.

Revisa: docs/design/congruence/issues.md
```

## Step 4: Update State

If validation ran successfully, update the project state:

```bash
python3 -c "
import sys
sys.path.insert(0, '.claude/hooks')
from core.state_manager import StateManager
sm = StateManager('.')
sm.update_state({
    'last_action': 'Congruence validation executed',
    'next_action': 'Fix issues if any, or continue with current phase'
})
"
```

## Step 5: Offer Actions

Based on results:

**If all passed:**
```
✅ ¿Qué deseas hacer?
1. Continuar con la fase actual
2. Ver detalles de la validación
3. Avanzar a la siguiente fase (si está permitido)
```

**If issues found:**
```
⚠️ ¿Qué deseas hacer?
1. Ver issues detallados (leer issues.md)
2. Intentar corregir automáticamente
3. Corregir manualmente y volver a validar
```

## Auto-Fix Capability

If user requests auto-fix for name mismatches:

1. Read the mismatch details from validation-results.json
2. For each name_mismatch:
   - Show: "Frontend usa `dob`, Backend espera `date_of_birth`"
   - Propose: "¿Renombrar en frontend a `date_of_birth`?"
3. If approved, update the frontend file
4. Re-run validation

## Important Notes

- Validation creates/updates files in `docs/design/congruence/`
- Errors BLOCK phase advancement in DESIGN and CONSTRUCTION
- Warnings do NOT block but should be reviewed
- Run validation after ANY design document changes
- Run validation after writing source code
