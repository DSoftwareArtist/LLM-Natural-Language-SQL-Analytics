# LLM Natural Language SQL Analytics - Specification

## Overview


A system that allows users to query structured databases using natural language. The system converts natural language questions into SQL queries, executes them against connected databases, and returns results. Includes semantic search over database schema documentation using pgvector.

<img width="967" height="739" alt="Screenshot 2026-03-19 at 5 39 25 PM" src="https://github.com/user-attachments/assets/b94cbc77-eae0-42f6-89cf-6fd7b05f146f" />


## Technology Stack

- **Framework:** Django >=4.2, <5.0
- **Database Driver:** psycopg2-binary >=2.9.9
- **Vector Storage:** pgvector >=0.1.8
- **LLM Framework:** langchain >=0.1.0, langchain-core >=0.1.0
- **Text Processing:** langchain-text-splitters >=0.3.0
- **LLM Provider:** langchain-openai >=0.1.0, openai >=1.0.0
- **Embeddings:** sentence-transformers >=2.2.2
- **Environment:** python-dotenv >=1.0.0
- **PDF Parsing:** PyPDF2 >=3.0.0


## Setup Instructions

### 1. Prerequisites

- Python 3.9+
- PostgreSQL 15+ with pgvector extension
- Groq API key (free)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

**Option A: Using Docker**
```bash
docker run -d --name postgres-pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=llm_analytics \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

**Option B: Local PostgreSQL**
1. Install PostgreSQL
2. Create database: `CREATE DATABASE llm_analytics;`
3. Enable pgvector: `CREATE EXTENSION vector;`

### 4. Configure Environment

Edit `.env` file:
```env
DB_NAME=llm_analytics
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_django_secret_key
```

**Get Groq API Key (free):**
1. Go to https://console.groq.com/keys
2. Create a new API key
3. Copy it to your `.env` file

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Run Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

- Web UI: http://localhost:8000
- Admin: http://localhost:8000/admin


