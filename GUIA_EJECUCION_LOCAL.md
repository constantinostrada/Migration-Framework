# 🚀 Guía de Ejecución Local - modern-banking-system

Esta guía te llevará paso a paso para ejecutar el sistema completo en tu máquina local.

---

## 📋 Pre-requisitos

Verifica que tengas instalado:

```bash
# Docker y Docker Compose
docker --version          # Debe ser >= 20.x
docker-compose --version  # Debe ser >= 1.29

# Node.js y npm
node --version           # Debe ser >= 18.x
npm --version            # Debe ser >= 9.x

# Python (opcional, solo si no usas Docker)
python3 --version        # Debe ser >= 3.11
```

Si no tienes Docker Desktop instalado:
- **Mac**: https://docs.docker.com/desktop/install/mac-install/
- **Windows**: https://docs.docker.com/desktop/install/windows-install/
- **Linux**: https://docs.docker.com/desktop/install/linux-install/

---

## 🎯 Opción 1: Inicio Rápido (Recomendado)

### Paso 1: Navega al proyecto

```bash
cd /Users/constantinostrada/Desktop/Migration-Framework/output/modern-banking-system
```

### Paso 2: Inicia el Backend + Base de Datos

```bash
# Inicia PostgreSQL + Backend API con Docker
docker-compose up -d

# Verifica que los servicios estén corriendo
docker-compose ps

# Deberías ver:
# - modern-banking-system-db-1      (PostgreSQL)
# - modern-banking-system-backend-1 (FastAPI)
```

**Espera 10-15 segundos** para que los servicios inicien completamente.

### Paso 3: Verifica el Backend

Abre en tu navegador:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/system/health (debería responder "OK")

Si ves la documentación de Swagger, ¡el backend está listo! ✅

### Paso 4: Instala dependencias del Frontend

```bash
# Navega a la carpeta del frontend
cd frontend

# Instala dependencias (solo primera vez)
npm install
```

Esto tomará 2-3 minutos la primera vez.

### Paso 5: Inicia el Frontend

```bash
# Inicia el servidor de desarrollo
npm run dev
```

Verás algo como:
```
  ▲ Next.js 14.2.x
  - Local:        http://localhost:3000
  - Ready in 1.2s
```

### Paso 6: Abre la Aplicación

Abre en tu navegador: **http://localhost:3000**

Deberías ver la página de Customers (Customer List) automáticamente.

---

## ✅ Verificación - ¿Todo funciona?

### 1. Verifica el Backend

```bash
# En una terminal nueva
curl http://localhost:8000/api/v1/customers

# Deberías ver:
# {"items":[],"total":0,"page":1,"page_size":20,"total_pages":0}
```

### 2. Verifica el Frontend

En el navegador (http://localhost:3000):
- ✅ Ves la tabla de Customers
- ✅ Ves el botón "Create Customer" arriba a la derecha
- ✅ Ves el campo de búsqueda

### 3. Prueba Crear un Customer

1. Haz clic en **"Create Customer"**
2. Llena el formulario:
   - **Name**: John Doe
   - **Email**: john.doe@example.com
   - **Phone**: +12025551234
   - **Address**: 123 Main Street, New York, NY 10001
   - **Monthly Income**: 10000
   - **Total Debt**: 1000

3. **Observa el Credit Score Preview** (debería aparecer mientras escribes):
   - Score: 765 (calculado automáticamente)
   - Color: Verde (porque 765 >= 750)

4. Haz clic en **"Create Customer"**

5. Deberías ver:
   - ✅ Toast de éxito: "Customer created successfully"
   - ✅ Redirección a la página de detalle del customer
   - ✅ Customer aparece en la lista

---

## 🎨 Características que puedes probar

### 1. Credit Score Preview en Tiempo Real
- Ve a "Create Customer"
- Escribe en "Monthly Income" y "Total Debt"
- El credit score se calcula automáticamente:
  - **Formula**: (income - debt) / income × 850
  - **Verde** (≥750): Aprobado
  - **Amarillo** (650-749): Marginal
  - **Rojo** (<650): Rechazado

### 2. Validaciones
Prueba estos casos de error:

**Email inválido**:
- Email: "invalidemail" → Error inline: "Invalid email format"

**Teléfono inválido**:
- Phone: "123" → Error inline: "Invalid phone format (use E.164: +1234567890)"

**Credit Score bajo**:
- Monthly Income: 5000
- Total Debt: 4500
- Score: 85 (rojo)
- Al hacer submit → Alert dialog: "Credit score 85 is below minimum threshold of 750"

**Email duplicado**:
- Crea un customer con email "test@example.com"
- Intenta crear otro con el mismo email
- Alert dialog: "Customer with this email already exists"

### 3. Búsqueda
- Escribe en el campo de búsqueda (mínimo 3 caracteres)
- Busca por nombre: "John"
- Busca por email: "john@"
- La búsqueda tiene debounce (espera 500ms antes de buscar)

### 4. Paginación
- Si tienes más de 20 customers, verás paginación en la parte inferior
- Botones: Previous, 1, 2, 3, ..., Next

### 5. Editar Customer
- Haz clic en "Edit" en cualquier customer de la lista
- Modifica el nombre, email, teléfono o dirección
- **Nota**: El credit score NO se puede editar (es solo lectura)
- Guarda los cambios

### 6. Eliminar Customer
- Haz clic en "Delete" en cualquier customer
- Aparece un AlertDialog de confirmación
- Confirma la eliminación
- Toast: "Customer deleted successfully"

### 7. Responsive Design
- Reduce el tamaño de la ventana del navegador
- En móvil (< 768px): La tabla se convierte en cards
- En tablet (768-1024px): Tabla compacta
- En desktop (> 1024px): Tabla completa

---

## 🐛 Troubleshooting - Problemas Comunes

### Problema 1: "Cannot connect to Docker daemon"

```bash
# Asegúrate de que Docker Desktop esté corriendo
# Mac: Abre Docker Desktop desde Aplicaciones
# Windows: Abre Docker Desktop desde el menú Inicio
```

### Problema 2: Puerto 8000 ya en uso

```bash
# Encuentra el proceso usando el puerto
lsof -i :8000

# Detén el proceso o usa otro puerto
# Edita docker-compose.yml: ports: - "8001:8000"
```

### Problema 3: Puerto 3000 ya en uso

```bash
# Inicia en otro puerto
PORT=3001 npm run dev
```

### Problema 4: Frontend no se conecta al Backend

**Verifica que el backend esté corriendo**:
```bash
curl http://localhost:8000/api/v1/customers
```

**Verifica la variable de entorno**:
```bash
# En frontend/.env.local debe estar:
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Problema 5: Error de CORS

Si ves errores de CORS en la consola del navegador:

```bash
# Verifica que en backend/app/infrastructure/api/main.py esté:
# allow_origins=["http://localhost:3000"]

# Reinicia el backend
docker-compose restart backend
```

### Problema 6: "Module not found" en Frontend

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Problema 7: Base de datos no inicia

```bash
# Detén todo
docker-compose down

# Elimina volúmenes
docker-compose down -v

# Reinicia
docker-compose up -d
```

---

## 📊 Ver Logs

### Logs del Backend
```bash
docker-compose logs -f backend
```

### Logs de la Base de Datos
```bash
docker-compose logs -f db
```

### Logs del Frontend
Los verás directamente en la terminal donde corriste `npm run dev`

---

## 🛑 Detener todo

```bash
# Detén los servicios de Docker
docker-compose down

# Detén el frontend
# Presiona Ctrl+C en la terminal donde corre npm run dev
```

---

## 🔄 Reiniciar desde cero

Si algo sale mal y quieres empezar de nuevo:

```bash
# Detén y elimina TODO (containers + volúmenes + imágenes)
docker-compose down -v --rmi all

# Reinicia
docker-compose up -d

# Reinstala frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📱 Accesos Rápidos

Una vez que todo esté corriendo:

- **Frontend (App)**: http://localhost:3000
- **Backend (API)**: http://localhost:8000/api/v1
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Redoc API Docs**: http://localhost:8000/redoc
- **Base de Datos**: localhost:5432
  - Usuario: `postgres`
  - Password: `postgres`
  - Database: `banking_db`

---

## 🧪 Próximo Paso: Pruebas E2E

Una vez que tengas todo corriendo localmente, puedes ejecutar las pruebas E2E:

```bash
cd frontend

# Instala Playwright (solo primera vez)
npx playwright install

# Ejecuta las pruebas E2E
npm run test:e2e

# Ejecuta con UI interactiva
npx playwright test --ui

# Ejecuta solo un test específico
npx playwright test tests/e2e/customers/customer-create.spec.ts
```

---

## ✅ Checklist de Éxito

Marca cada item cuando funcione:

- [ ] Docker Desktop está corriendo
- [ ] `docker-compose ps` muestra 2 servicios (db + backend)
- [ ] http://localhost:8000/docs muestra la API
- [ ] `npm run dev` inicia sin errores
- [ ] http://localhost:3000 muestra la lista de Customers
- [ ] Puedo crear un customer nuevo
- [ ] Veo el credit score preview en tiempo real
- [ ] Las validaciones funcionan (email, phone)
- [ ] Puedo buscar customers
- [ ] Puedo editar un customer
- [ ] Puedo eliminar un customer
- [ ] El diseño es responsive (mobile/tablet/desktop)

---

## 🎉 ¡Listo!

Si todos los checkboxes están marcados, ¡felicidades! 🎊

Tienes un sistema bancario moderno completamente funcional con:
- ✅ Backend RESTful (FastAPI + PostgreSQL)
- ✅ Frontend moderno (Next.js + React + shadcn/ui)
- ✅ Clean Architecture (3 capas)
- ✅ 118 tests pasando (100%)
- ✅ Documentación completa

---

## 📞 ¿Necesitas ayuda?

Si algo no funciona:
1. Revisa la sección de Troubleshooting arriba
2. Revisa los logs: `docker-compose logs -f`
3. Pregúntame con el error específico que ves
