from django.contrib import admin
from django.urls import path, include

from core.views import (
    GenerateSQLView,
    ExecuteQueryView,
    QueryView,
)
from core.web_views import query


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/generate-sql/', GenerateSQLView.as_view(), name='generate-sql'),
    path('api/execute/', ExecuteQueryView.as_view(), name='execute-query'),
    path('api/query/', QueryView.as_view(), name='api-query'),    
    path('', query, name='query'),
]