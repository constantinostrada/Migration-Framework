# 🚀 Migration Framework v4.3

**Framework de Migración Automatizada de Sistemas Legacy a Arquitecturas Modernas**

[![Version](https://img.shields.io/badge/version-4.3-blue.svg)](https://github.com/constantinostrada/migration-framework)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org)

> **Transforma sistemas legacy en aplicaciones modernas con Clean Architecture usando IA especializada**

## 📋 Tabla de Contenidos

- [🎯 Características Principales](#-características-principales)
- [🏗️ Arquitectura](#️-arquitectura)
- [🛠️ Tecnologías](#️-tecnologías)
- [📋 Requisitos](#-requisitos)
- [🚀 Instalación](#-instalación)
- [💡 Uso](#-uso)
- [📁 Estructura del Proyecto](#-estructura-del-proyecto)
- [🤖 Agentes Especializados](#-agentes-especializados)
- [📊 Métricas de Calidad](#-métricas-de-calidad)
- [🔧 Desarrollo](#-desarrollo)
- [🤝 Contribución](#-contribución)
- [📝 Licencia](#-licencia)
- [📞 Contacto](#-contacto)

## 🎯 Características Principales

### ✨ Automatización Inteligente
- **Auto-asignación de agentes**: Los agentes especializados se asignan automáticamente tareas basadas en su expertise
- **Workflow autónomo**: 95% autonomía, solo 4 puntos de decisión crítica con usuario
- **TDD integrado**: Tests especificados antes del código
- **Validación continua**: QA integrada en cada fase

### 🏛️ Arquitectura Moderna
- **Clean Architecture**: Separación clara entre Domain, Application e Infrastructure
- **API-First**: Contratos OpenAPI generados automáticamente
- **Clean Code**: Código de producción listo para deployment
- **Documentación completa**: API docs, arquitectura, testing, deployment

### 🎯 Calidad Garantizada
- **E2E Testing**: Validación completa con Playwright
- **Smoke Tests**: Validación rápida de APIs críticas
- **Tech Stack Validation**: Compatibilidad verificada antes de implementar
- **UI Approval**: Mockups HTML para aprobación antes del desarrollo

### 📈 Eficiencia
- **40 tareas pre-generadas**: Workflow determinístico y trazable
- **Tiempo de ejecución**: 27-37 horas para sistemas completos
- **ROI demostrado**: Ahorro del 80-90% en tiempo de QA
- **Zero context loss**: Migración completa sin pérdida de reglas de negocio

## 🏗️ Arquitectura

### Clean Architecture Layers

```
┌─────────────────────────────────────┐
│           PRESENTATION              │
│         (Next.js + shadcn/ui)       │
├─────────────────────────────────────┤
│           APPLICATION               │
│       (Use Cases & DTOs)            │
├─────────────────────────────────────┤
│             DOMAIN                  │
│   (Entities, Value Objects, Rules)  │
├─────────────────────────────────────┤
│         INFRASTRUCTURE              │
│   (ORM, API, External Services)     │
└─────────────────────────────────────┘
```

### Workflow de Migración

```mermaid
graph TD
    A[SDD Analysis] --> B[Requirements Extraction]
    B --> C[Tech Stack Validation]
    C --> D[Task Generation]
    D --> E[Contract Generation]
    E --> F[Domain Implementation]
    F --> G[Application Layer]
    G --> H[Infrastructure Layer]
    H --> I[UI Design & Approval]
    I --> J[Frontend Implementation]
    J --> K[Smoke Tests]
    K --> L[E2E Testing]
    L --> M[Final Delivery]
```

## 🛠️ Tecnologías

### Backend
- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy 2.0** - ORM asíncrono avanzado
- **PostgreSQL** - Base de datos robusta
- **Pydantic** - Validación de datos
- **Alembic** - Migraciones de base de datos

### Frontend
- **Next.js 14** - Framework React full-stack
- **TypeScript** - JavaScript tipado
- **Tailwind CSS** - Framework CSS utility-first
- **shadcn/ui** - Componentes UI de alta calidad
- **React Hook Form** - Gestión de formularios

### Testing & QA
- **Pytest** - Framework de testing Python
- **Playwright** - Testing E2E automatizado
- **Coverage.py** - Reportes de cobertura
- **Locust** - Testing de carga

### DevOps & Tools
- **Docker** - Containerización
- **PostgreSQL** - Base de datos
- **Redis** - Cache y sesiones
- **Nginx** - Load balancer
- **GitHub Actions** - CI/CD

## 📋 Requisitos

### Requisitos Mínimos
- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 15+
- **Docker**: 20+ (opcional)
- **RAM**: 8GB mínimo
- **Disco**: 10GB espacio libre

### Recomendado para Desarrollo
- **Python**: 3.11.5+
- **Node.js**: 20+
- **PostgreSQL**: 15+
- **Docker Desktop**: Latest
- **VS Code** con extensiones recomendadas
- **RAM**: 16GB+
- **CPU**: 4+ cores

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/yourusername/migration-framework.git
cd migration-framework
```

### 2. Configurar el Entorno

```bash
# Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

```bash
# Usando Docker (recomendado)
docker run -d \
  --name postgres-migration \
  -e POSTGRES_DB=migration_db \
  -e POSTGRES_USER=migration_user \
  -e POSTGRES_PASSWORD=migration_pass \
  -p 5432:5432 \
  postgres:15

# O instalar PostgreSQL localmente
```

### 4. Variables de Entorno

Crear archivo `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://migration_user:migration_pass@localhost:5432/migration_db

# Application
SECRET_KEY=your-secret-key-here
DEBUG=True

# External APIs (opcional)
OPENAI_API_KEY=your-openai-key
```

## 💡 Uso

### Inicio Rápido

1. **Preparar SDD**: Coloca tu documento SDD en `docs/input/`

2. **Iniciar Migración**:
   ```bash
   # El framework se ejecuta completamente autónomo
   /migration start
   ```

3. **Monitorear Progreso**:
   - Estado en tiempo real: `docs/state/orchestrator-state.json`
   - Progreso por agente: `docs/state/tracking/`
   - Logs detallados en terminal

### Puntos de Decisión (Solo 4)

1. **PHASE 0**: Reglas de negocio poco claras
2. **PHASE 0.5**: Incompatibilidad de tech stack
3. **PHASE 3**: Aprobación de mockups UI
4. **PHASE 4**: Decisión estratégica E2E

### Resultado Final

```
output/{project-name}/
├── backend/          # FastAPI + SQLAlchemy
├── frontend/         # Next.js + shadcn/ui
├── tests/           # Cobertura 90%+
├── docs/            # Documentación completa
└── docker/          # Archivos de deployment
```

## 📁 Estructura del Proyecto

```
migration-framework/
├── docs/                          # Documentación y configuración
│   ├── input/                     # Archivos base del framework
│   │   ├── ai_agent_tasks.json    # 30 tareas base
│   │   └── ai_agent_tasks_extended.json # 10 tareas adicionales
│   ├── schemas/                   # Esquemas TypeScript
│   ├── state/                     # Estado de migración (generado)
│   ├── analysis/                  # Análisis SDD (generado)
│   └── examples/                  # Ejemplos y casos de uso
├── output/                        # Código generado (por proyecto)
├── .claude/                       # Instrucciones de agentes
│   ├── agents/                    # 11 agentes especializados
│   └── docs/                      # Documentación detallada
├── CLAUDE.md                      # Instrucciones principales
├── CLAUDE_V4.3_CHANGES.md         # Log de cambios
├── docker-compose.yml             # Servicios para desarrollo
└── README.md                      # Este archivo
```

## 🤖 Agentes Especializados

### Core Agents (11 especializados)

| Agente | Responsabilidad | Capa |
|--------|----------------|------|
| **sdd-analyzer** | Análisis SDD → módulos y reglas | Análisis |
| **protocol-architect** | APIs OpenAPI + contratos | Contratos |
| **test-generator** | Tests unitarios + integración | QA |
| **database-architect** | Schema SQL + migraciones | Infraestructura |
| **domain-agent** | Lógica de dominio pura | Domain |
| **use-case-agent** | Casos de uso + DTOs | Application |
| **infrastructure-agent** | ORM + APIs + UI | Infrastructure |
| **context7-agent** | Investigación técnica | Investigación |
| **tech-stack-validator** | Validación compatibilidad | Validación |
| **ui-approval-agent** | Mockups HTML | Diseño |
| **e2e-qa-agent** | Testing E2E Playwright | QA |

### Auto-Asignación Inteligente

Los agentes leen automáticamente todas las tareas y se asignan basándose en:
- **Keywords**: "entity", "DTO", "ORM", "React", etc.
- **Layer**: domain, application, infrastructure
- **Dependencies**: Respeta orden de ejecución

## 📊 Métricas de Calidad

### Cobertura de Testing
- **Unit Tests**: 100% de funciones críticas
- **Integration Tests**: 100% de APIs
- **E2E Tests**: 95%+ pass rate mínimo
- **Coverage Total**: 90%+ líneas de código

### Rendimiento
- **API Response Time**: < 200ms (95th percentile)
- **Database Queries**: Optimizadas con índices
- **Frontend Bundle**: < 500KB gzipped
- **Lighthouse Score**: 90+ en todas las métricas

### Seguridad
- **OWASP Top 10**: Cubierto completamente
- **Input Validation**: Sanitización en cliente y servidor
- **Authentication**: JWT + refresh tokens
- **Authorization**: Role-based access control
- **Encryption**: Datos sensibles encriptados

## 🔧 Desarrollo

### Configuración de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
npm install

# Ejecutar tests
pytest
npm test

# Linting
black . --check
isort . --check-only
flake8
```

### Scripts Disponibles

```bash
# Desarrollo
npm run dev          # Frontend dev server
npm run build        # Build producción
npm run preview      # Preview build

# Testing
npm run test         # Unit tests
npm run test:e2e     # E2E tests
npm run test:perf    # Performance tests

# Backend
uvicorn app.main:app --reload  # FastAPI dev server
alembic upgrade head           # DB migrations
```

### Docker Development

```bash
# Ambiente completo
docker-compose up -d

# Servicios individuales
docker-compose up postgres redis
docker-compose up backend frontend
```

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor lee las [guías de contribución](CONTRIBUTING.md).

### Tipos de Contribución

1. **🐛 Reportar Bugs**: Usa los [issues de GitHub](https://github.com/yourusername/migration-framework/issues)
2. **💡 Nuevas Features**: Discute en [discussions](https://github.com/yourusername/migration-framework/discussions)
3. **🔧 Pull Requests**: Sigue el flujo estándar de Git
4. **📖 Documentación**: Mejoras en docs siempre son bienvenidas

### Proceso de Desarrollo

1. Fork el proyecto
2. Crea una branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Estándares de Código

- **Python**: PEP 8, type hints, docstrings
- **TypeScript**: ESLint, Prettier
- **Tests**: Cobertura mínima 90%
- **Commits**: Conventional commits

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📞 Contacto

**Migration Framework Team**

- **Email**: team@migration-framework.dev
- **Twitter**: [@migrationfw](https://twitter.com/migrationfw)
- **LinkedIn**: [Migration Framework](https://linkedin.com/company/migration-framework)
- **Website**: [https://migration-framework.dev](https://migration-framework.dev)

### Soporte

- 📖 **Documentación**: [docs.migration-framework.dev](https://docs.migration-framework.dev)
- 💬 **Discord**: [Únete a nuestra comunidad](https://discord.gg/migration-framework)
- 🐛 **Issues**: [Reporta problemas](https://github.com/constantinostrada/migration-framework/issues)
- 💡 **Discussions**: [Preguntas y ideas](https://github.com/constantinostrada/migration-framework/discussions)

---

## 🙏 Agradecimientos

- **Claude AI** por el poder de razonamiento avanzado
- **Anthropic** por la plataforma de IA
- **Comunidad Open Source** por las herramientas que hacen esto posible

---

**⭐ Si este proyecto te ayuda, considera darle una estrella en GitHub!**

---

*Migration Framework v4.3 - Transformando el legado en el futuro, un sistema a la vez.*
