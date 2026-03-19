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
