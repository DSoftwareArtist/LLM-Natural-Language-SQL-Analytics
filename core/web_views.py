import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import DatabaseConnection, SchemaDocument, QueryHistory
from .services import DatabaseService, SQLGenerationService, EmbeddingService


def dashboard(request):
    connections = DatabaseConnection.objects.all()[:5]
    recent_queries = QueryHistory.objects.all()[:10]
    context = {
        'connections': connections,
        'recent_queries': recent_queries
    }
    return render(request, 'core/dashboard.html', context)


def connections(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        host = request.POST.get('host')
        port = request.POST.get('port')
        database = request.POST.get('database')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        connection = DatabaseConnection.objects.create(
            name=name,
            host=host,
            port=int(port),
            database=database,
            username=username,
            password=password
        )
        return redirect('connections')
    
    connections = DatabaseConnection.objects.all()
    return render(request, 'core/connections.html', {'connections': connections})


@csrf_exempt
def test_connection(request, pk):
    if request.method == 'POST':
        connection = get_object_or_404(DatabaseConnection, pk=pk)
        connection_data = {
            'host': connection.host,
            'port': connection.port,
            'database': connection.database,
            'username': connection.username,
            'password': connection.password
        }
        result = DatabaseService.test_connection(connection_data)
        return JsonResponse(result)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def delete_connection(request, pk):
    if request.method == 'POST':
        connection = get_object_or_404(DatabaseConnection, pk=pk)
        connection.delete()
    return redirect('connections')


def query(request):
    connections = DatabaseConnection.objects.filter(is_active=True)
    query_result = None
    generated_sql = None
    
    if request.method == 'POST':
        connection_id = request.POST.get('connection_id')
        natural_language = request.POST.get('natural_language')
        
        if connection_id and natural_language:
            try:
                connection = DatabaseConnection.objects.get(id=connection_id)
                connection_data = {
                    'host': connection.host,
                    'port': connection.port,
                    'database': connection.database,
                    'username': connection.username,
                    'password': connection.password
                }
                
                schema_result = DatabaseService.get_schema(connection_data)
                if schema_result.get('success'):
                    schema_str = SQLGenerationService.format_schema_for_prompt(schema_result)
                    generated_sql = SQLGenerationService.generate_sql(natural_language, schema_str)
                    
                    if 'execute' in request.POST:
                        query_result = DatabaseService.execute_query(connection_data, generated_sql)
                        
                        QueryHistory.objects.create(
                            connection=connection,
                            natural_language=natural_language,
                            generated_sql=generated_sql,
                            executed_sql=generated_sql if query_result.get('success') else None,
                            result=query_result if query_result.get('success') else None,
                            error=query_result.get('message') if not query_result.get('success') else None
                        )
            except Exception as e:
                query_result = {'success': False, 'message': str(e)}
    
    context = {
        'connections': connections,
        'query_result': query_result,
        'generated_sql': generated_sql
    }
    return render(request, 'core/query.html', context)


def documents(request):
    connections = DatabaseConnection.objects.filter(is_active=True)
    documents = SchemaDocument.objects.all()
    search_results = None
    
    if request.method == 'POST':
        if 'search' in request.POST:
            query = request.POST.get('search_query')
            if query:
                query_embedding = EmbeddingService.embed_text(query)
                results = []
                
                for doc in documents:
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
                
                search_results = results
        elif 'upload' in request.POST:
            from PyPDF2 import PdfReader
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            
            connection_id = request.POST.get('connection_id')
            file = request.FILES.get('file')
            
            if connection_id and file:
                connection = get_object_or_404(DatabaseConnection, id=connection_id)
                
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
    
    context = {
        'connections': connections,
        'documents': documents,
        'search_results': search_results
    }
    return render(request, 'core/documents.html', context)


def history(request):
    queries = QueryHistory.objects.all()
    return render(request, 'core/history.html', {'queries': queries})