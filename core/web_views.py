from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection as django_connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.psycopg2 import register_vector

from .models import QueryHistory
from .services import DatabaseService, SQLGenerationService, EmbeddingService


def query(request):
    query_result = None
    generated_sql = None
    
    if request.method == 'POST':
        natural_language = request.POST.get('natural_language')
        
        if  natural_language:
            try:
                connection_data = {
                    'host': settings.DATABASE_HOST,
                    'port': settings.DATABASE_PORT,
                    'database': settings.DATABASE_NAME,
                    'username': settings.DATABASE_USER,
                    'password': settings.DATABASE_PASSWORD
                }
                
                schema_result = DatabaseService.get_schema(connection_data)
                if schema_result.get('success'):
                    schema_str = SQLGenerationService.format_schema_for_prompt(schema_result)
                    generated_sql = SQLGenerationService.generate_sql(natural_language, schema_str)
                    
                    if 'execute' in request.POST:
                        query_result = DatabaseService.execute_query(connection_data, generated_sql)
                        
                        QueryHistory.objects.create(
                            natural_language=natural_language,
                            generated_sql=generated_sql,
                            executed_sql=generated_sql if query_result.get('success') else None,
                            result=query_result if query_result.get('success') else None,
                            error=query_result.get('message') if not query_result.get('success') else None
                        )
            except Exception as e:
                query_result = {'success': False, 'message': str(e)}
    
    context = {
        'query_result': query_result,
        'generated_sql': generated_sql
    }
    return render(request, 'core/query.html', context)

