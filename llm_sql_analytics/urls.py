from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from core.views import (
    DatabaseConnectionViewSet,
    SchemaDocumentViewSet,
    QueryHistoryViewSet,
    GenerateSQLView,
    ExecuteQueryView,
    QueryView,
    SchemaSearchView,
    UploadDocumentView
)
from core.web_views import (
    dashboard,
    connections,
    test_connection,
    delete_connection,
    query,
    documents,
    history
)

router = DefaultRouter()
router.register(r'connections', DatabaseConnectionViewSet, basename='connection')
router.register(r'documents', SchemaDocumentViewSet, basename='document')
router.register(r'history', QueryHistoryViewSet, basename='history')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/generate-sql/', GenerateSQLView.as_view(), name='generate-sql'),
    path('api/execute/', ExecuteQueryView.as_view(), name='execute-query'),
    path('api/query/', QueryView.as_view(), name='api-query'),
    path('api/schema-search/', SchemaSearchView.as_view(), name='schema-search'),
    path('api/upload/', UploadDocumentView.as_view(), name='upload-document'),
    
    path('', dashboard, name='dashboard'),
    path('connections/', connections, name='connections'),
    path('connections/<uuid:pk>/test/', test_connection, name='test_connection'),
    path('connections/<uuid:pk>/delete/', delete_connection, name='delete_connection'),
    path('query/', query, name='query'),
    path('documents/', documents, name='documents'),
    path('history/', history, name='history'),
]