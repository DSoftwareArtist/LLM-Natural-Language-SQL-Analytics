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

## 3. Functionality Specification

### Core Features

#### 3.1 Database Connection Management

- Add PostgreSQL database connections with connection details
- Test database connectivity
- Store connection configurations securely
- Support multiple database connections

#### 3.2 Schema Introspection

- Automatically fetch table names and column information
- Store schema in PostgreSQL with pgvector for semantic search
- Support uploading schema documentation (PDF)

#### 3.3 Natural Language to SQL

- Accept natural language queries
- Use LLM to convert natural language to SQL
- Support SELECT, INSERT, UPDATE, DELETE operations
- Include validation and error handling

#### 3.4 Semantic Schema Search

- Embed schema documentation using sentence-transformers
- Store embeddings in pgvector
- Search schema semantically to find relevant tables/columns

#### 3.5 Query Execution

- Execute generated SQL against target database
- Return formatted results
- Handle errors gracefully with user-friendly messages

#### 3.6 Query History

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

## 4. API Endpoints

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

## 5. Acceptance Criteria

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
