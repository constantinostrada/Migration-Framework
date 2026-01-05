# 🤝 Guía de Contribución - Migration Framework

¡Gracias por tu interés en contribuir al **Migration Framework**! Este documento describe cómo puedes contribuir de manera efectiva a este proyecto.

## 📋 Tabla de Contenidos

- [🚀 Inicio Rápido](#-inicio-rápido)
- [🐛 Reportar Bugs](#-reportar-bugs)
- [💡 Solicitar Features](#-solicitar-features)
- [🔧 Contribuir Código](#-contribuir-código)
- [📖 Contribuir Documentación](#-contribuir-documentación)
- [🧪 Guías de Testing](#-guías-de-testing)
- [📝 Estándares de Código](#-estándares-de-código)
- [🔄 Proceso de Pull Request](#-proceso-de-pull-request)
- [🎯 Áreas de Contribución](#-áreas-de-contribución)

## 🚀 Inicio Rápido

### Configuración Inicial

1. **Fork y Clone**:
   ```bash
   git clone https://github.com/constantinostrada/migration-framework.git
   cd migration-framework
   ```

2. **Configurar Entorno**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   npm install
   ```

3. **Verificar Setup**:
   ```bash
   python -c "import migration_framework; print('✅ Python setup OK')"
   npm run build  # Verificar build
   ```

## 🐛 Reportar Bugs

### Plantilla de Bug Report

Usa esta plantilla para reportar bugs:

```markdown
**Descripción del Bug**
Breve descripción del problema

**Pasos para Reproducir**
1. Ir a '...'
2. Ejecutar '....'
3. Ver error en '...'

**Comportamiento Esperado**
Qué debería suceder

**Comportamiento Actual**
Qué está sucediendo

**Capturas de Pantalla**
Si aplica, agrega screenshots

**Entorno**
- OS: [e.g. macOS 12.1, Windows 11]
- Python: [e.g. 3.11.5]
- Node.js: [e.g. 18.17.0]
- Framework Version: [e.g. v4.3]

**Archivos Relevantes**
- `docs/state/orchestrator-state.json`
- Logs de error
- Configuración usada
```

## 💡 Solicitar Features

### Tipos de Features

1. **Nuevos Agentes**: Agentes especializados para tareas específicas
2. **Nuevos Tech Stacks**: Soporte para frameworks adicionales
3. **Mejoras de QA**: Nuevas validaciones o tests
4. **Optimizaciones**: Mejoras de rendimiento
5. **Integraciones**: Conexiones con otras herramientas

### Plantilla de Feature Request

```markdown
**Título del Feature**

**Descripción**
Descripción detallada del feature solicitado

**Problema que Resuelve**
Cuál es el problema actual que se resuelve

**Solución Propuesta**
Cómo debería funcionar el feature

**Alternativas Consideradas**
Otras soluciones que se consideraron

**Impacto**
Cómo afecta al usuario y al sistema

**Implementación**
Ideas sobre cómo implementarlo (opcional)
```

## 🔧 Contribuir Código

### Configuración de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt
npm install

# Configurar pre-commit hooks
pre-commit install

# Ejecutar tests iniciales
pytest --cov
npm test
```

### Flujo de Trabajo

1. **Seleccionar Issue**: Elige un issue abierto o crea uno nuevo
2. **Crear Branch**: `git checkout -b feature/nombre-del-feature`
3. **Desarrollar**: Implementa tu feature con tests
4. **Testear**: Asegúrate que todos los tests pasan
5. **Documentar**: Actualiza documentación si es necesario
6. **Commit**: Usa conventional commits
7. **Push**: Sube tu branch
8. **Pull Request**: Crea PR con descripción detallada

### Conventional Commits

```bash
# Tipos permitidos
feat: nueva funcionalidad
fix: corrección de bug
docs: cambios en documentación
style: cambios de formato (espacios, etc.)
refactor: refactorización de código
test: agregar o corregir tests
chore: cambios en build, herramientas, etc.

# Ejemplos
git commit -m "feat: agregar soporte para React 18"
git commit -m "fix: corregir validación de email en domain layer"
git commit -m "docs: actualizar guía de instalación"
```

## 📖 Contribuir Documentación

### Tipos de Documentación

1. **READMEs**: Para componentes específicos
2. **Guías**: Tutoriales y how-tos
3. **API Docs**: Documentación de APIs generadas
4. **Arquitectura**: Diagramas y decisiones técnicas

### Estándares de Documentación

- Usa **Markdown** para todo
- Incluye **ejemplos de código** ejecutables
- Mantén **actualizado** con los cambios del código
- Usa **emojis** para mejorar legibilidad
- Incluye **capturas de pantalla** cuando aplique

## 🧪 Guías de Testing

### Tipos de Tests Requeridos

#### Unit Tests (Python)
```python
# tests/unit/test_domain_customer.py
import pytest
from app.domain.entities.customer import Customer

def test_customer_creation_valid():
    """Test customer creation with valid data"""
    customer = Customer.create(valid_customer_data)
    assert customer.is_valid()
    assert customer.credit_score > 0
```

#### Integration Tests
```python
# tests/integration/test_customer_api.py
async def test_create_customer_api(client):
    """Test complete customer creation flow"""
    response = await client.post("/api/v1/customers", json=customer_data)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "PENDING"
```

#### E2E Tests (Playwright)
```typescript
// tests/e2e/customer-management.spec.ts
test("complete customer lifecycle", async ({ page }) => {
  await page.goto("/customers/new");
  await page.fill("[name=name]", "John Doe");
  await page.fill("[name=email]", "john@example.com");
  await page.click("[type=submit]");
  await expect(page.locator(".success-message")).toBeVisible();
});
```

### Cobertura Requerida

- **Unit Tests**: 90%+ cobertura
- **Integration Tests**: 100% de APIs
- **E2E Tests**: 95%+ pass rate

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app --cov-report=html

# Tests específicos
pytest tests/unit/test_customer.py -v

# Tests de frontend
npm run test
npm run test:e2e
```

## 📝 Estándares de Código

### Python

```python
# ✅ Correcto
from typing import Optional, List
from pydantic import BaseModel, Field

class Customer(BaseModel):
    """Customer domain entity."""

    id: Optional[int] = Field(default=None, description="Customer ID")
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")

    def calculate_credit_score(self) -> float:
        """Calculate customer credit score based on financial data."""
        # Implementation here
        pass
```

### TypeScript/React

```typescript
// ✅ Correcto
interface CustomerFormProps {
  onSubmit: (customer: CustomerData) => Promise<void>;
  isLoading: boolean;
}

export const CustomerForm: React.FC<CustomerFormProps> = ({
  onSubmit,
  isLoading
}) => {
  const handleSubmit = async (data: CustomerData) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Error creating customer:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form implementation */}
    </form>
  );
};
```

### Linting

```bash
# Python
black . --check      # Formato
isort . --check-only # Imports
flake8              # Linting
mypy                # Type checking

# TypeScript
npm run lint        # ESLint
npm run type-check  # TypeScript
```

## 🔄 Proceso de Pull Request

### Checklist de PR

- [ ] **Tests pasan**: `pytest && npm test`
- [ ] **Linting OK**: `black . && npm run lint`
- [ ] **Cobertura**: `pytest --cov` > 90%
- [ ] **Documentación**: Actualizada si aplica
- [ ] **Commits**: Conventional commits
- [ ] **Branch**: `feature/` o `fix/` o `docs/`
- [ ] **Conflicts**: Resueltos con main

### Plantilla de PR

```markdown
## 📝 Descripción

Breve descripción de los cambios realizados

## 🎯 Tipo de Cambio

- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 💥 Breaking change
- [ ] 📖 Documentation
- [ ] 🔧 Refactoring
- [ ] 🧪 Tests

## 🔍 Cambios Realizados

### Backend
- Cambios en domain layer
- Nuevos endpoints API
- Actualización de schemas

### Frontend
- Nuevos componentes
- Actualización de UI
- Mejoras de UX

### Tests
- Nuevos tests unitarios
- Tests de integración
- Tests E2E

## 🧪 Testing

- [ ] Unit tests pasan
- [ ] Integration tests pasan
- [ ] E2E tests pasan (95%+)
- [ ] Cobertura > 90%

## 📋 Checklist

- [ ] Código sigue estándares del proyecto
- [ ] Documentación actualizada
- [ ] Variables de entorno documentadas
- [ ] Migraciones de BD incluidas si aplica
- [ ] Breaking changes documentados

## 🔗 Issues Relacionados

Resuelve: #123
Relacionado: #456

## 📸 Screenshots (si aplica)

*Agregar screenshots de cambios visuales*
```

## 🎯 Áreas de Contribución

### Alto Impacto
- **Nuevos Agentes**: Especializados en tecnologías específicas
- **Mejoras de QA**: Nuevas validaciones o estrategias de testing
- **Performance**: Optimizaciones de velocidad y recursos
- **Security**: Mejoras de seguridad y compliance

### Medio Impacto
- **Nuevos Tech Stacks**: Soporte para frameworks adicionales
- **UI/UX**: Mejoras en la interfaz de usuario
- **Documentación**: Guías, tutoriales, ejemplos
- **DevOps**: Mejoras en CI/CD, deployment

### Bajo Impacto
- **Bug Fixes**: Corrección de issues reportados
- **Code Quality**: Refactoring y mejoras de código
- **Tests**: Cobertura adicional, nuevos escenarios
- **Dependencies**: Actualización de librerías

### Comenzando

1. **Principiantes**: Comienza con issues etiquetados como `good-first-issue`
2. **Intermedios**: Issues con `help-wanted`
3. **Avanzados**: Issues con `enhancement` o crea tus propias features

## 📞 Soporte

¿Necesitas ayuda con tu contribución?

- **Discord**: [Únete a nuestra comunidad](https://discord.gg/migration-framework)
- **Discussions**: [Preguntas en GitHub](https://github.com/constantinostrada/migration-framework/discussions)
- **Issues**: Para bugs específicos

## 🙏 Reconocimiento

¡Todas las contribuciones son valoradas! Los contribuidores serán:

- Mencionados en el CHANGELOG
- Agregados al archivo CONTRIBUTORS.md
- Reconocidos en releases
- Invitados a eventos de la comunidad

---

¡Gracias por contribuir al Migration Framework! 🚀
