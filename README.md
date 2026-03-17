# LLM Natural Language SQL Analytics - Specification

## 1. Project Overview

**Project Name:** LLM SQL Analytics  
**Project Type:** Django Web Application  
**Core Functionality:** A system that allows users to query structured databases using natural language. The system converts natural language questions into SQL queries, executes them against connected databases, and returns results. Includes semantic search over database schema documentation using pgvector.

**Target Users:** Business analysts, data scientists, and non-technical users who need to query databases without writing SQL.

---

## 2. Technology Stack

- **Framework:** Django >=4.2, <5.0
- **Database Driver:** psycopg2-binary >=2.9.9
- **Vector Storage:** pgvector >=0.1.8
- **LLM Framework:** langchain >=0.1.0, langchain-core >=0.1.0
- **Text Processing:** langchain-text-splitters >=0.3.0
- **LLM Provider:** langchain-openai >=0.1.0, openai >=1.0.0
- **Embeddings:** sentence-transformers >=2.2.2
- **Environment:** python-dotenv >=1.0.0
- **PDF Parsing:** PyPDF2 >=3.0.0

---

## 3. UI/UX Specification

### Layout Structure

**Header**

- Application title: "LLM SQL Analytics"
- Navigation: Dashboard, Query Interface, Schema Docs, Settings

**Main Content Area**

- Dashboard: Overview of connected databases and recent queries
- Query Interface: Natural language input + SQL preview + results table
- Schema Docs: List of uploaded documents with semantic search
- Settings: Database connection configuration

**Footer**

- Version info and copyright

### Visual Design

**Color Palette**

- Primary: `#1E3A5F` (Deep Navy)
- Secondary: `#3D5A80` (Slate Blue)
- Accent: `#48CAE4` (Cyan)
- Background: `#F8F9FA` (Light Gray)
- Surface: `#FFFFFF` (White)
- Text Primary: `#212529` (Dark Gray)
- Text Secondary: `#6C757D` (Medium Gray)
- Success: `#28A745` (Green)
- Error: `#DC3545` (Red)
- Warning: `#FFC107` (Yellow)

**Typography**

- Headings: "Inter", sans-serif, 600 weight
- Body: "Inter", sans-serif, 400 weight
- Monospace (SQL): "JetBrains Mono", monospace

**Spacing**

- Base unit: 8px
- Container max-width: 1200px
- Card padding: 24px
- Section margin: 32px

### Components

**Query Input Card**

- Textarea for natural language input
- "Generate SQL" button (primary style)
- "Execute" button (accent style)
- SQL preview panel with syntax highlighting

**Results Table**

- Sortable columns
- Pagination for large results
- Export to CSV option

**Schema Doc Card**

- Document name
- Upload date
- Preview snippet
- Semantic search input

**Database Connection Card**

- Connection name
- Database type indicator
- Status indicator (connected/disconnected)
- Edit/Delete actions

---

## 4. Functionality Specification

### Core Features

#### 4.1 Database Connection Management

- Add PostgreSQL database connections with connection details
- Test database connectivity
- Store connection configurations securely
- Support multiple database connections

#### 4.2 Schema Introspection

- Automatically fetch table names and column information
- Store schema in PostgreSQL with pgvector for semantic search
- Support uploading schema documentation (PDF)

#### 4.3 Natural Language to SQL

- Accept natural language queries
- Use LLM to convert natural language to SQL
- Support SELECT, INSERT, UPDATE, DELETE operations
- Include validation and error handling

#### 4.4 Semantic Schema Search

- Embed schema documentation using sentence-transformers
- Store embeddings in pgvector
- Search schema semantically to find relevant tables/columns

#### 4.5 Query Execution

- Execute generated SQL against target database
- Return formatted results
- Handle errors gracefully with user-friendly messages

#### 4.6 Query History

- Store all queries with timestamps
- View past queries and their results
- Re-run previous queries

### User Interactions

1. **Add Database:** User enters connection details → System tests connection → Saves if successful
2. **Ask Question:** User types natural language → System generates SQL → User reviews → Executes → Views results
3. **Search Schema:** User enters search term → System returns semantically similar schema elements
4. **Upload Docs:** User uploads PDF → System extracts text → Embeds and stores in vector DB

### Data Handling

- Query history stored in SQLite (local)
- Database connections stored encrypted
- Schema embeddings stored in PostgreSQL via pgvector

### Edge Cases

- Invalid SQL generated → Show error with suggestion to retry
- Database connection failed → Show connection error with troubleshooting tips
- Empty results → Show "No results found" message
- Large result sets → Paginate results
- Network timeout → Show timeout error with retry option

---

## 5. Database Schema

### Django Models

```
DatabaseConnection
- id: UUID (primary key)
- name: CharField (unique)
- host: CharField
- port: IntegerField
- database: CharField
- username: CharField
- password: CharField (encrypted)
- created_at: DateTimeField
- updated_at: DateTimeField
- is_active: BooleanField

SchemaDocument
- id: UUID (primary key)
- connection: ForeignKey(DatabaseConnection)
- name: CharField
- content: TextField
- embedding: VectorField (pgvector)
- uploaded_at: DateTimeField

QueryHistory
- id: UUID (primary key)
- connection: ForeignKey(DatabaseConnection)
- natural_language: TextField
- generated_sql: TextField
- executed_sql: TextField (nullable)
- result: JSONField (nullable)
- error: TextField (nullable)
- created_at: DateTimeField
```

---

## 6. API Endpoints

| Method | Endpoint                      | Description                    |
| ------ | ----------------------------- | ------------------------------ |
| GET    | /api/connections/             | List all database connections  |
| POST   | /api/connections/             | Add new database connection    |
| GET    | /api/connections/{id}/        | Get connection details         |
| PUT    | /api/connections/{id}/        | Update connection              |
| DELETE | /api/connections/{id}/        | Delete connection              |
| POST   | /api/connections/{id}/test/   | Test connection                |
| GET    | /api/connections/{id}/schema/ | Get database schema            |
| POST   | /api/query/                   | Execute natural language query |
| GET    | /api/history/                 | Get query history              |
| POST   | /api/docs/                    | Upload schema document         |
| GET    | /api/docs/                    | List schema documents          |
| POST   | /api/docs/search/             | Semantic search in documents   |

---

## 7. Acceptance Criteria

1. ✓ User can add PostgreSQL database connections
2. ✓ User can test database connectivity
3. ✓ User can enter natural language queries
4. ✓ System generates valid SQL from natural language
5. ✓ User can execute queries and view results
6. ✓ User can upload PDF schema documentation
7. ✓ System performs semantic search over schema docs
8. ✓ Query history is maintained
9. ✓ Web interface is responsive and functional
10. ✓ Error handling provides helpful feedback
