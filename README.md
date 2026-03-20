# LLM Natural Language SQL Analytics

## Overview


A system that allows users to query structured databases using natural language. The system converts natural language questions into SQL queries, executes, and returns results. Includes semantic search over database schema documentation using pgvector.

<img width="987" height="749" alt="Screenshot 2026-03-19 at 5 46 10 PM" src="https://github.com/user-attachments/assets/369bb41a-2665-452b-ad1d-712f39da7cb7" />

## Technology Stack

- **Framework:** Django >=4.2, <5.0
- **Database Driver:** psycopg2-binary >=2.9.9
- **Vector Storage:** pgvector >=0.1.8
- **LLM Framework:** langchain >=0.1.0, langchain-core >=0.1.0
- **Embeddings:** sentence-transformers >=2.2.2
- **Environment:** python-dotenv >=1.0.0
- **PDF Parsing:** PyPDF2 >=3.0.0
