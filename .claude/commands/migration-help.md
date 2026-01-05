# Migration Help Command

You are showing help information about the migration framework. Display the following:

```
🔧 UNIVERSAL MIGRATION FRAMEWORK - AYUDA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 COMANDOS DISPONIBLES:

  /migration start       Iniciar una nueva migración
                         Solicita documentos y comienza el análisis.

  /migration status      Ver estado actual
                         Muestra progreso, fase actual y próximos pasos.

  /migration restart     Archivar o reiniciar
                         Opciones para guardar, eliminar o resetear.

  /migration validate    Validar congruencia
                         Ejecuta validación real entre front/back/DB.

  /migration checkpoint  Crear checkpoint manual
                         Guarda snapshot completo del estado.

  /migration checkpoints Gestionar historial de checkpoints
                         Listar, restaurar o limpiar checkpoints.

  /migration docs [tech] Consultar documentación actualizada
                         Usa Context7 para obtener docs de FastAPI,
                         Next.js, Pydantic, SQLAlchemy, etc.

  /migration check-hooks Verificar hooks del framework
                         Confirma que los hooks están configurados.

  /migration help        Mostrar esta ayuda


📊 FASES DE MIGRACIÓN:

  1. ANÁLISIS
     └─ Sub-agentes extraen información de documentos
     └─ Se identifican entidades, reglas, requerimientos

  2. FEEDBACK
     └─ Validación con el usuario
     └─ Checklist interactivo
     └─ Diagramas de flujo

  3. DISEÑO
     └─ Arquitectura backend (API contracts)
     └─ Diseño frontend (componentes, páginas)
     └─ Esquema de base de datos
     └─ Validación de congruencia

  4. CONSTRUCCIÓN
     └─ Implementación del backend (FastAPI)
     └─ Implementación del frontend (Next.js)
     └─ Migraciones de base de datos
     └─ Auto-commits con git

  5. TESTING
     └─ Tests unitarios backend
     └─ Tests de integración
     └─ Tests E2E con Playwright


📁 ESTRUCTURA DE ARCHIVOS:

  docs/
  ├── input/          Documentos proporcionados por el usuario
  ├── analysis/       Resultados del análisis
  ├── design/         Documentos de diseño
  ├── qa/             Reportes de testing
  └── state/          Estado y checkpoints

  src/
  ├── backend/        Aplicación FastAPI
  ├── frontend/       Aplicación Next.js
  └── database/       Migraciones SQL


💡 TIPS:

  • Los sub-agentes NUNCA escriben código, solo analizan
  • El orquestador (Claude) es el único que implementa
  • Todo el contexto importante se guarda en archivos
  • Usa /migration checkpoint antes de cerrar sesión
  • Si pierdes contexto, Claude lee RECOVERY.md automáticamente


🔗 MCPs CONFIGURADOS:

  • Context7     - Documentación técnica actualizada
  • Playwright   - Testing E2E automatizado
  • PostgreSQL   - Interacción con base de datos
  • GitHub       - Control de versiones


❓ ¿NECESITAS AYUDA?

  Describe tu problema o pregunta y te ayudaré.
  También puedes:
  • Pedir ver el estado actual: /migration status
  • Preguntar sobre una fase específica
  • Solicitar que explique algún concepto
```
