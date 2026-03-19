from django.conf import settings
from django.db import connection as django_connection

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pgvector.psycopg2 import register_vector


from .models import QueryHistory
from .serializers import QueryRequestSerializer, SchemaSearchSerializer
from .services import DatabaseService, SQLGenerationService, EmbeddingService


class GenerateSQLView(APIView):
    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        if serializer.is_valid():
            connection_id = serializer.validated_data['connection_id']
            natural_language = serializer.validated_data['natural_language']
            
            
            connection_data = {
                'host': settings.DATABASE_HOST,
                'port': settings.DATABASE_PORT,
                'database': settings.DATABASE_NAME,
                'username': settings.DATABASE_USER,
                'password': settings.DATABASE_PASSWORD
            }
            
            schema_result = DatabaseService.get_schema(connection_data)
            if not schema_result['success']:
                return Response(
                    {'error': schema_result['message']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            schema_str = SQLGenerationService.format_schema_for_prompt(schema_result)
            
            try:
                sql = SQLGenerationService.generate_sql(natural_language, schema_str)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            return Response({
                'sql': sql,
                'schema': schema_result
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExecuteQueryView(APIView):
    def post(self, request):
        connection_id = request.data.get('connection_id')
        sql = request.data.get('sql', '')
        
        if not connection_id or not sql:
            return Response(
                {'error': 'connection_id and sql are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        connection_data = {
            'host': settings.DATABASE_HOST,
            'port': settings.DATABASE_PORT,
            'database': settings.DATABASE_NAME,
            'username': settings.DATABASE_USER,
            'password': settings.DATABASE_PASSWORD
        }
        
        result = DatabaseService.execute_query(connection_data, sql)
        
        QueryHistory.objects.create(
            connection=connection,
            natural_language=request.data.get('natural_language', ''),
            generated_sql=request.data.get('generated_sql', ''),
            executed_sql=sql,
            result=result if result['success'] else None,
            error=result.get('message') if not result['success'] else None
        )
        
        return Response(result)


class QueryView(APIView):
    def post(self, request):
        connection_id = request.data.get('connection_id')
        natural_language = request.data.get('natural_language')
        
        if not connection_id or not natural_language:
            return Response(
                {'error': 'connection_id and natural_language are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        connection_data = {
            'host': settings.DATABASE_HOST,
            'port': settings.DATABASE_PORT,
            'database': settings.DATABASE_NAME,
            'username': settings.DATABASE_USER,
            'password': settings.DATABASE_PASSWORD
        }
        
        schema_result = DatabaseService.get_schema(connection_data)
        if not schema_result['success']:
            return Response(
                {'error': schema_result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        schema_str = SQLGenerationService.format_schema_for_prompt(schema_result)
        
        try:
            sql = SQLGenerationService.generate_sql(natural_language, schema_str)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        result = DatabaseService.execute_query(connection_data, sql)
        
        QueryHistory.objects.create(
            connection=connection,
            natural_language=natural_language,
            generated_sql=sql,
            executed_sql=sql if result['success'] else None,
            result=result if result['success'] else None,
            error=result.get('message') if not result['success'] else None
        )
        
        return Response({
            'sql': sql,
            'result': result
        })
