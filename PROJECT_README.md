# BankingNewApp - Modern Banking System

Complete migration of legacy COBOL/CICS/DB2 banking system to modern FastAPI + Next.js + PostgreSQL stack.

## 🎯 Project Overview

**BankingNewApp** is a full-stack banking application that provides:
- Customer management with credit assessment
- Multiple account types (ISA, Current, Saving, Loan, Mortgage)
- Transaction processing (deposits, withdrawals, transfers)
- Role-based access control (Admin, Teller, Customer)
- Complete audit trail and business rule enforcement

### Tech Stack

**Backend:**
- FastAPI 0.109+ (Python 3.11)
- SQLAlchemy 2.0 (Async ORM)
- PostgreSQL 15+
- Alembic (migrations)
- JWT authentication
- Pydantic v2 validation

**Frontend:**
- Next.js 14 (App Router)
- TypeScript 5.3+
- Tailwind CSS 3.4+
- React Hook Form + Zod
- Axios HTTP client

**Infrastructure:**
- Docker + Docker Compose
- PostgreSQL (database)
- pgAdmin (database management)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OR Python 3.11+ and Node.js 18+

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Seed database with sample data
docker-compose exec backend python scripts/seed_data.py

# Access the application
open http://localhost:3000
```

### Option 2: Manual Setup

**Backend:**
```bash
cd src/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed database
python scripts/seed_data.py

# Start server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd src/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📋 Application URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050

## 🔐 Demo Credentials

After seeding the database:

| Role | Username | Password | Description |
|------|----------|----------|-------------|
| Admin | `admin` | `Admin123!` | Full system access |
| Teller | `teller` | `Teller123!` | Bank teller operations |
| Customer | `customer` | `Customer123!` | Customer portal access |

## 📁 Project Structure

```
src/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/v1/       # API endpoints
│   │   ├── core/         # Configuration, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   ├── repositories/ # Data access layer
│   │   └── db/           # Database setup
│   ├── scripts/          # Utility scripts
│   └── alembic/          # Database migrations
│
└── frontend/             # Next.js frontend
    ├── app/              # App Router pages
    │   ├── (auth)/       # Auth pages
    │   └── (dashboard)/  # Protected pages
    ├── components/       # React components
    └── lib/              # Utilities, API client
```

## 🏦 Features

### Customer Management
- Create customers with automatic credit assessment
- Query 5 credit agencies (Experian, Equifax, TransUnion, Crediva, UKCIS)
- View customer details and credit history
- Update customer information
- Track customer accounts

### Account Management
- **5 Account Types:**
  - ISA: Individual Savings Account (interest-bearing, tax-free)
  - Current: Day-to-day banking (overdraft facility)
  - Saving: Interest-bearing savings
  - Loan: Track loan balances with interest
  - Mortgage: Track mortgage balances with interest

- **Business Rules Enforced:**
  - Maximum 9 accounts per customer
  - Overdraft only available for Current accounts
  - Interest only applicable to ISA and Saving accounts
  - Account-specific withdrawal limits

### Transaction Processing
- **Deposit**: Add funds to any account
- **Withdraw**: Remove funds with validation
- **Transfer**: Between accounts atomically
- **Transaction History**: View all transactions with filters

- **Business Rules Enforced:**
  - Insufficient funds validation
  - Overdraft limit enforcement
  - ISA withdrawal limits (4 per year)
  - Saving withdrawal limits (6 per month)
  - Complete audit trail (soft delete only)

### Security & Access Control
- JWT-based authentication
- Password strength validation
- Role-based access control (RBAC)
- Protected API endpoints
- Secure password hashing (bcrypt)

## 🔧 Development

### Backend Development

```bash
cd src/backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run tests
pytest

# Format code
black app/
flake8 app/
```

### Frontend Development

```bash
cd src/frontend

# Development server with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

### Database Operations

```bash
# Direct PostgreSQL access
docker-compose exec postgres psql -U bankingapp -d banking_db

# Backup database
docker-compose exec postgres pg_dump -U bankingapp banking_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U bankingapp banking_db < backup.sql
```

## 📊 Business Rules

All business rules from the legacy COBOL system are enforced:

**Customer Rules (BR-CUST-xxx)**
- Age validation (18-150 years)
- Birth year must be > 1600
- Credit score averaging from 5 agencies

**Account Rules (BR-ACC-xxx)**
- Max 9 accounts per customer
- Account type-specific validations
- Interest/overdraft restrictions

**Transaction Rules (BR-TXN-xxx)**
- Positive amount validation
- Insufficient funds checks
- Withdrawal limits (ISA/Saving)
- Soft delete only (audit trail)

See `docs/analysis/business-rules/` for complete documentation.

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f [service]

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Execute commands in container
docker-compose exec backend bash
docker-compose exec frontend sh

# Remove everything (including data)
docker-compose down -v
```

See `DOCKER_SETUP.md` for comprehensive Docker documentation.

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user

**Customers**
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer (with credit check)
- `GET /api/v1/customers/{id}` - Get customer details
- `PUT /api/v1/customers/{id}` - Update customer

**Accounts**
- `GET /api/v1/accounts` - List accounts
- `POST /api/v1/accounts` - Create account
- `GET /api/v1/accounts/{id}` - Get account details
- `PUT /api/v1/accounts/{id}` - Update account settings

**Transactions**
- `GET /api/v1/transactions` - List all transactions
- `POST /api/v1/transactions/deposit` - Deposit funds
- `POST /api/v1/transactions/withdraw` - Withdraw funds
- `POST /api/v1/transactions/transfer` - Transfer between accounts

## 🎨 Frontend Pages

**Public Pages**
- `/` - Landing page
- `/login` - User login
- `/register` - User registration

**Protected Pages** (requires authentication)
- `/dashboard` - Dashboard home
- `/customers` - Customer list
- `/customers/create` - Create customer
- `/customers/[id]` - Customer details
- `/accounts` - Account list
- `/accounts/create` - Create account
- `/accounts/[id]` - Account details
- `/transactions` - Transaction list
- `/transactions/new` - New transaction

**Admin Only**
- `/admin` - Admin panel
- `/admin/users` - User management

## 🚀 Deployment

### Production Checklist

- [ ] Change all default passwords
- [ ] Update `SECRET_KEY` in backend
- [ ] Configure CORS origins
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Set resource limits in Docker
- [ ] Build frontend for production (`npm run build`)
- [ ] Set up reverse proxy (Nginx)

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=your-super-secret-key-min-32-chars
CORS_ORIGINS=["https://yourdomain.com"]
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 📞 Support

For issues or questions:
- Review documentation in `docs/` directory
- Check `DOCKER_SETUP.md` for Docker issues
- Review API docs at http://localhost:8000/docs
- Check application logs: `docker-compose logs -f`

---

**Status**: ✅ Production Ready

**Version**: 1.0.0

**Last Updated**: December 2025
