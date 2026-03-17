import json
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .models import DatabaseConnection, SchemaDocument, QueryHistory
from .serializers import (
    DatabaseConnectionSerializer,
    SchemaDocumentSerializer,
    QueryHistorySerializer,
    QueryRequestSerializer,
    SchemaSearchSerializer
)
from .services import DatabaseService, SQLGenerationService, EmbeddingService


class DatabaseConnectionViewSet(viewsets.ModelViewSet):
    queryset = DatabaseConnection.objects.all()
    serializer_class = DatabaseConnectionSerializer

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        connection = self.get_object()
        connection_data = {
            'host': connection.host,
            'port': connection.port,
            'database': connection.database,
            'username': connection.username,
            'password': connection.password
        }
        result = DatabaseService.test_connection(connection_data)
        return Response(result)

    @action(detail=True, methods=['get'])
    def schema(self, request, pk=None):
        connection = self.get_object()
        connection_data = {
            'host': connection.host,
            'port': connection.port,
            'database': connection.database,
            'username': connection.username,
            'password': connection.password
        }
        result = DatabaseService.get_schema(connection_data)
        return Response(result)


class SchemaDocumentViewSet(viewsets.ModelViewSet):
    queryset = SchemaDocument.objects.all()
    serializer_class = SchemaDocumentSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_text(instance.content)
            embeddings = EmbeddingService.embed_documents(chunks)
            instance.embeddings = json.dumps({'chunks': chunks, 'embeddings': embeddings})
            instance.save()
        except Exception:
            pass


class QueryHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = QueryHistory.objects.all()
    serializer_class = QueryHistorySerializer


class GenerateSQLView(APIView):
    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        if serializer.is_valid():
            connection_id = serializer.validated_data['connection_id']
            natural_language = serializer.validated_data['natural_language']
            
            try:
                connection = DatabaseConnection.objects.get(id=connection_id)
            except DatabaseConnection.DoesNotExist:
                return Response(
                    {'error': 'Database connection not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            connection_data = {
                'host': connection.host,
                'port': connection.port,
                'database': connection.database,
                'username': connection.username,
                'password': connection.password
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
        
        try:
            connection = DatabaseConnection.objects.get(id=connection_id)
        except DatabaseConnection.DoesNotExist:
            return Response(
                {'error': 'Database connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        connection_data = {
            'host': connection.host,
            'port': connection.port,
            'database': connection.database,
            'username': connection.username,
            'password': connection.password
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
        
        try:
            connection = DatabaseConnection.objects.get(id=connection_id)
        except DatabaseConnection.DoesNotExist:
            return Response(
                {'error': 'Database connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        connection_data = {
            'host': connection.host,
            'port': connection.port,
            'database': connection.database,
            'username': connection.username,
            'password': connection.password
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


class SchemaSearchView(APIView):
    def post(self, request):
        serializer = SchemaSearchSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            connection_id = serializer.validated_data.get('connection_id')
            
            query_embedding = EmbeddingService.embed_text(query)
            
            if connection_id:
                docs = SchemaDocument.objects.filter(connection_id=connection_id)
            else:
                docs = SchemaDocument.objects.all()
            
            results = []
            for doc in docs:
                if doc.embeddings:
                    doc_data = json.loads(doc.embeddings)
                    if 'embeddings' in doc_data:
                        doc_embeddings = doc_data['embeddings']
                        chunks = doc_data.get('chunks', [])
                        
                        similarities = []
                        for i, emb in enumerate(doc_embeddings):
                            similarity = sum([a * b for a, b in zip(query_embedding, emb)])
                            similarities.append((i, similarity))
                        
                        similarities.sort(key=lambda x: x[1], reverse=True)
                        
                        for idx, sim in similarities[:3]:
                            if sim > 0.3:
                                results.append({
                                    'document': doc.name,
                                    'content': chunks[idx] if idx < len(chunks) else '',
                                    'similarity': sim
                                })
            
            return Response({'results': results})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadDocumentView(APIView):
    def post(self, request):
        connection_id = request.data.get('connection_id')
        file = request.FILES.get('file')
        
        if not connection_id or not file:
            return Response(
                {'error': 'connection_id and file are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            connection = DatabaseConnection.objects.get(id=connection_id)
        except DatabaseConnection.DoesNotExist:
            return Response(
                {'error': 'Database connection not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if file.name.endswith('.pdf'):
            pdf_reader = PdfReader(file)
            content = ''
            for page in pdf_reader.pages:
                content += page.extract_text()
        else:
            content = file.read().decode('utf-8', errors='ignore')
        
        doc = SchemaDocument.objects.create(
            connection=connection,
            name=file.name,
            content=content
        )
        
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_text(content)
            embeddings = EmbeddingService.embed_documents(chunks)
            doc.embeddings = json.dumps({'chunks': chunks, 'embeddings': embeddings})
            doc.save()
        except Exception:
            pass
        
        return Response({
            'id': str(doc.id),
            'name': doc.name,
            'message': 'Document uploaded successfully'
        }, status=status.HTTP_201_CREATED)