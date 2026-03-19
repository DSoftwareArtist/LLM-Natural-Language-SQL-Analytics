import os
from datetime import datetime, date
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from django.conf import settings
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sentence_transformers import SentenceTransformer


class DatabaseService:
    
    @staticmethod
    def get_connection(connection_data: Dict[str, Any]):
        return psycopg2.connect(
            host=connection_data['host'],
            port=connection_data['port'],
            database=connection_data['database'],
            user=connection_data['username'],
            password=connection_data['password'],
            cursor_factory=RealDictCursor
        )

    @staticmethod
    def get_schema(connection_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            with DatabaseService.get_connection(connection_data) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT table_name, column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' 
                        ORDER BY table_name, ordinal_position
                    """)
                    columns = cursor.fetchall()
                    
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    tables = cursor.fetchall()
                    
                    return {
                        'success': True,
                        'tables': [t['table_name'] for t in tables],
                        'columns': [dict(c) for c in columns]
                    }
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def execute_query(connection_data: Dict[str, Any], sql: str) -> Dict[str, Any]:
        def convert_row(row):
            result = {}
            for key, value in dict(row).items():
                if isinstance(value, (datetime, date)):
                    result[key] = value.isoformat()
                elif isinstance(value, bytes):
                    result[key] = value.decode('utf-8', errors='replace')
                else:
                    result[key] = value
            return result
        
        try:
            with DatabaseService.get_connection(connection_data) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    if sql.strip().upper().startswith('SELECT'):
                        results = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description] if cursor.description else []
                        return {
                            'success': True,
                            'columns': columns,
                            'rows': [convert_row(r) for r in results],
                            'row_count': len(results)
                        }
                    else:
                        conn.commit()
                        return {
                            'success': True,
                            'message': 'Query executed successfully',
                            'rows_affected': cursor.rowcount
                        }
        except Exception as e:
            return {'success': False, 'message': str(e)}


class EmbeddingService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            model_name = os.environ.get('SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2')
            cls._model = SentenceTransformer(model_name)
        return cls._model

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    @classmethod
    def embed_documents(cls, texts: List[str]) -> List[List[float]]:
        model = cls.get_model()
        embeddings = model.encode(texts, convert_to_numpy=True)
        return [e.tolist() for e in embeddings]


class SQLGenerationService:
    _llm = None
    _chain = None

    @classmethod
    def get_llm(cls):
        if cls._llm is None:
            api_key = os.environ.get('GROQ_API_KEY', '')
            if not api_key:
                raise ValueError("GROQ_API_KEY not set")
            cls._llm = ChatGroq(
                model='llama-3.3-70b-versatile',
                temperature=0,
                api_key=api_key
            )
        return cls._llm

    @classmethod
    def generate_sql(cls, natural_language: str, schema_info: str) -> str:
        llm = cls.get_llm()
        
        prompt = PromptTemplate(
            input_variables=["question", "schema"],
            template="""
                You are a SQL expert. Given a natural language question and a database schema, generate a valid PostgreSQL query.

                Schema:
                {schema}

                Question: {question}

                Generate only the SQL query and format it as string, no explanation. If the question cannot be answered with the given schema, generate a query that returns an appropriate empty result.
                """
            )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(question=natural_language, schema=schema_info)
        print('LLM Output:', result)
        sql = result.strip()
        if sql.lower().startswith('sql'):
            sql = sql[3:].strip()
        if sql.lower().startswith('```sql'):
            sql = sql[6:].strip()
        if sql.endswith('```'):
            sql = sql[:-3].strip()
        return sql

    @classmethod
    def format_schema_for_prompt(cls, schema: Dict[str, Any]) -> str:
        tables = schema.get('tables', [])
        columns = schema.get('columns', [])
        
        table_columns = {}
        for col in columns:
            table_name = col['table_name']
            if table_name not in table_columns:
                table_columns[table_name] = []
            table_columns[table_name].append(f"{col['column_name']} ({col['data_type']})")
        
        schema_str = ""
        for table in tables:
            schema_str += f"Table: {table}\n"
            schema_str += f"Columns: {', '.join(table_columns.get(table, []))}\n\n"
        
        return schema_str