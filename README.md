# AltsReimaginedAPI

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A modern **FastAPI-based document harvesting and processing API** built with Clean Architecture principles. The application provides automated file management capabilities with support for multiple database backends (PostgreSQL and SQL Server).

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [API Endpoints](#-api-endpoints)
- [Database Migrations](#-database-migrations)
- [Logging](#-logging)
- [Domain Entities](#-domain-entities)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **FastAPI Framework** - High-performance, modern Python web framework
- **Clean Architecture** - Well-organized codebase with separation of concerns
- **Multi-Database Support** - Switch between PostgreSQL and SQL Server via configuration
- **Database Migrations** - Alembic-based schema versioning
- **Flexible Logging** - Console, Database, and Azure Application Insights support
- **Dependency Injection** - Repository pattern with dependency injection
- **Auto-Generated API Docs** - Swagger UI and ReDoc documentation
- **Health Checks** - Built-in health monitoring endpoints
- **Pydantic Settings** - Type-safe configuration management

---

## 🏗 Architecture

This project follows **Clean Architecture** principles with a layered approach:

```
┌─────────────────────────────────────────────────────────────┐
│                       API Layer                              │
│              (Controllers, Routes, FastAPI)                  │
├─────────────────────────────────────────────────────────────┤
│                     Domain Layer                             │
│           (Entities, Services, Interfaces)                   │
├─────────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                        │
│        (Database, Repositories, Logging, Migrations)         │
├─────────────────────────────────────────────────────────────┤
│                      Core Layer                              │
│           (Settings, Configuration, Lifespan)                │
└─────────────────────────────────────────────────────────────┘
```

### Request Flow

```
FastAPI Request
       ↓
Controller (file_manager_controller)
       ↓
Service (file_manager_service)
       ↓
Repository interface → Repository implementation (file_manager_repository)
       ↓
Database (SQL Server / Postgres)
       ↓
Logging (logger_manager → db_logger / app_insights_logger)
```

---

## 📁 Project Structure

```
Frame-python/
├── .env                          # Environment variables (not in repo)
├── .gitignore                    # Git ignore rules
├── alembic.ini                   # Alembic configuration
├── README.md                     # Project documentation
├── src/
│   ├── main.py                   # FastAPI application entry point
│   │
│   ├── api/                      # API Layer
│   │   ├── __init__.py
│   │   ├── controllers/          # API Controllers
│   │   │   └── file_manager_controller.py
│   │   └── routes/               # Route definitions
│   │       └── file_manager_routes.py
│   │
│   ├── core/                     # Core Configuration
│   │   ├── config.ini            # Application configuration
│   │   ├── settings.py           # Pydantic settings management
│   │   └── lifespan.py           # Application lifecycle hooks
│   │
│   ├── domain/                   # Domain Layer
│   │   ├── entities/             # SQLAlchemy models
│   │   │   ├── base_entity.py    # Base entity with common fields
│   │   │   ├── file_manager.py   # File entity model
│   │   │   ├── account_master.py # Account entity
│   │   │   ├── firm_master.py    # Firm entity
│   │   │   ├── extract_file.py   # Extract file entity
│   │   │   ├── file_configuration.py
│   │   │   ├── publishing_control.py
│   │   │   └── logger.py         # Logs entity
│   │   ├── interfaces/           # Repository interfaces
│   │   │   └── file_manager_repository_interface.py
│   │   └── services/             # Business logic services
│   │       └── file_manager_service.py
│   │
│   ├── infrastructure/           # Infrastructure Layer
│   │   ├── database/
│   │   │   ├── base.py           # SQLAlchemy Base
│   │   │   ├── connection_manager.py  # DB connection handling
│   │   │   ├── alembic/          # Database migrations
│   │   │   │   ├── env.py
│   │   │   │   ├── script.py.mako
│   │   │   │   └── versions/     # Migration files
│   │   │   ├── postgres_repositories/
│   │   │   │   └── file_manager_repository.py
│   │   │   └── sqlserver_repositories/
│   │   │       └── (SQL Server implementations)
│   │   └── logging/
│   │       ├── logger_manager.py      # Logging setup
│   │       ├── db_logger.py           # Database logging handler
│   │       └── app_insights_logger.py # Azure App Insights handler
│   │
│   ├── exceptions/               # Custom exceptions
│   ├── middleware/               # Custom middleware
│   └── utils/                    # Utility functions
│
└── venv/                         # Virtual environment
```

---

## 📋 Prerequisites

- **Python 3.10+**
- **PostgreSQL** or **SQL Server** database
- **pip** or **Poetry** package manager

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/Frame-python.git
cd Frame-python
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If `requirements.txt` doesn't exist, install core dependencies:
> ```bash
> pip install fastapi uvicorn sqlalchemy pydantic-settings python-dotenv alembic psycopg2-binary
> ```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

Create a `.env` file in the project root with the following variables:

```env
# PostgreSQL Connection
POSTGRES_URL=postgresql://username:password@localhost:5432/database_name

# SQL Server Connection (if using SQL Server)
SQL_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

# Azure Application Insights (optional)
APP_INSIGHTS_KEY=your-application-insights-key
```

### Application Configuration (`src/core/config.ini`)

```ini
[app]
name = AltsReimaginedAPI
debug = True

[database]
# Options: postgres, sqlserver
active_db = postgres

# Environment variable used to load the actual connection string
connection_string_env = DATABASE_URL

[logger]
active_logger = db   # Options: 'db' or 'app_insights'
log_level = INFO
```

### Configuration Options

| Setting | Description | Options |
|---------|-------------|---------|
| `active_db` | Active database backend | `postgres`, `postgresql`, `sql`, `sqlserver`, `mssql` |
| `active_logger` | Logging backend | `db`, `app_insights` |
| `log_level` | Logging verbosity | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

---

## ▶️ Running the Application

### Development Mode

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Python Directly

```bash
python -m uvicorn src.main:app --reload
```

The application will start at: `http://localhost:8000`

---

## 📖 API Documentation

Once the application is running, you can access the interactive API documentation:

| Documentation | URL |
|--------------|-----|
| **Swagger UI** | [http://localhost:8000/swagger](http://localhost:8000/swagger) |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

---

## 🔌 API Endpoints

### Root Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Application info (name, version, status) |
| `GET` | `/health` | Health check endpoint |

### File Manager Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/files/GetFileManagerListApi` | Get list of file documents |

### Example Responses

#### Root Endpoint (`GET /`)

```json
{
  "name": "AltsReimaginedAPI",
  "version": "1.0.0",
  "status": "running"
}
```

#### Health Check (`GET /health`)

```json
{
  "status": "healthy"
}
```

---

## 🗃️ Database Migrations

This project uses **Alembic** for database migrations.

### Initialize Migration Environment

```bash
alembic init src/infrastructure/database/alembic
```

### Create a New Migration

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>
```

### Rollback Migration

```bash
# Downgrade by one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### View Migration History

```bash
alembic history --verbose
```

---

## 📝 Logging

The application supports multiple logging backends configured via `config.ini`:

### Console Logging (Always Enabled)

All logs are output to the console with timestamps and log levels.

```
2025-12-10 19:00:00 | INFO | src.core.lifespan | Application starting up...
2025-12-10 19:00:00 | INFO | src.core.lifespan | Database initialized successfully
```

### Database Logging

When `active_logger = db` in `config.ini`, logs are stored in the `logs` table:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `message` | TEXT | Log message |
| `message_template` | TEXT | Message template |
| `level` | TEXT | Log level (INFO, ERROR, etc.) |
| `timestamp` | TIMESTAMP | Log timestamp |
| `exception` | TEXT | Exception details |
| `log_event` | JSONB | Additional properties |

### Azure Application Insights

When `active_logger = app_insights`, logs are sent to Azure Application Insights for centralized monitoring.

---

## 📦 Domain Entities

### BaseEntity

All entities inherit from `BaseEntity` which provides common fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `created` | DateTime | Record creation timestamp |
| `created_by` | String(255) | User who created the record |
| `updated` | DateTime | Last update timestamp |
| `updated_by` | String(255) | User who last updated |
| `is_active` | Boolean | Soft delete flag |

### FileManager

Main entity for document/file management with extensive metadata fields including:

- Document identification (`doc_uid`, `doc_sid`, `filename`)
- Account linking (`account_uid`, `entity_uid`, `firm`)
- Processing status (`status`, `stage`, `document_process_stage`)
- Harvest metadata (`harvest_system`, `harvest_method`, `harvest_source`)
- Index/Extract metadata (`index_system`, `extract_system`)
- Audit fields (`create_by`, `create_date`, `update_date`)

### AccountMaster

Entity for managing account information including firm relationships, account status, and investor details.

### FirmMaster

Entity for firm/organization management with hierarchical relationships.

### Logs

Entity for storing application logs when database logging is enabled.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow **PEP 8** style guidelines
- Write docstrings for all public functions
- Add type hints to function signatures
- Create unit tests for new features
- Update documentation as needed

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For support and questions, please:

- Open an issue on GitHub
- Contact the development team

---

<p align="center">
  Built with ❤️ using <a href="https://fastapi.tiangolo.com/">FastAPI</a>
</p>
