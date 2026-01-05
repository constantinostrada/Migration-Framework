# Migration Check Hooks Command

You are verifying that the framework hooks are properly configured and functional.

## Step 1: Check settings.local.json exists

Read `.claude/settings.local.json` and verify it contains hook configurations.

If file doesn't exist:
```
❌ HOOKS NO CONFIGURADOS
━━━━━━━━━━━━━━━━━━━━━━━

El archivo .claude/settings.local.json no existe.
Los hooks del framework NO están activos.

Para activar los hooks, crea el archivo con la configuración correcta.
¿Deseas que lo cree ahora? (sí/no)
```

## Step 2: Validate Hook Structure

Check that all required hooks are present:

```python
required_hooks = {
    "UserPrompt": ["session_recovery.py"],
    "PreToolUse": ["pre_write_validation.py"],
    "PostToolUse": ["auto_checkpoint.py", "generate_dashboard.py"],
    "Stop": ["phase_gate.py"]
}
```

## Step 3: Test Each Hook Script

For each hook script, verify:
1. The Python file exists
2. The file is syntactically valid (python3 -m py_compile)
3. Required imports are available

Run these checks:
```bash
# Check session_recovery.py
python3 -m py_compile .claude/hooks/v2/session_recovery.py

# Check pre_write_validation.py
python3 -m py_compile .claude/hooks/v2/pre_write_validation.py

# Check auto_checkpoint.py
python3 -m py_compile .claude/hooks/v2/auto_checkpoint.py

# Check phase_gate.py
python3 -m py_compile .claude/hooks/v2/phase_gate.py

# Check generate_dashboard.py
python3 -m py_compile .claude/hooks/v2/generate_dashboard.py
```

## Step 4: Check Core Dependencies

Verify core modules are importable:
```bash
python3 -c "from pathlib import Path; import sys; sys.path.insert(0, '.claude/hooks'); from core.state_manager import StateManager; from core.congruence import CongruenceValidator; from core.deliverables import DeliverableChecker; from core.logger import FrameworkLogger; print('OK')"
```

## Step 5: Report Results

Present results in this format:

```
🔍 VERIFICACIÓN DE HOOKS DEL FRAMEWORK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Configuración
- settings.local.json: [✅ Existe | ❌ No existe]

## Hooks Configurados

| Hook | Script | Estado |
|------|--------|--------|
| UserPrompt | session_recovery.py | [✅/❌] |
| PreToolUse | pre_write_validation.py | [✅/❌] |
| PostToolUse | auto_checkpoint.py | [✅/❌] |
| PostToolUse | generate_dashboard.py | [✅/❌] |
| Stop | phase_gate.py | [✅/❌] |

## Core Modules

| Módulo | Estado |
|--------|--------|
| state_manager | [✅/❌] |
| congruence | [✅/❌] |
| deliverables | [✅/❌] |
| logger | [✅/❌] |

## Resultado Final

[✅ HOOKS LISTOS - El framework está correctamente configurado]
o
[⚠️ HOOKS PARCIALES - Algunos componentes tienen problemas]
o
[❌ HOOKS NO FUNCIONALES - Revisar errores arriba]

## Nota Importante

⚠️ Los hooks de Claude Code requieren que el usuario los haya
habilitado en su configuración. Esta verificación confirma que
los scripts existen y son válidos, pero NO garantiza que Claude
los ejecute automáticamente.

Para confirmar ejecución real, observa si aparecen mensajes
como "⚠️ MIGRACIÓN EN PROGRESO DETECTADA" al inicio de sesión.
```

## Step 6: Offer Fixes

If any issues found, offer to fix them:
- Missing settings.local.json → Create it
- Missing hook scripts → Report which ones
- Syntax errors → Show the error message
- Missing core modules → Check installation
