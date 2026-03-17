import uuid
from django.db import models


class DatabaseConnection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=5432)
    database = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'database_connections'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_connection_string(self):
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class SchemaDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=255)
    content = models.TextField()
    embeddings = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'schema_documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name


class QueryHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(DatabaseConnection, on_delete=models.CASCADE, related_name='queries')
    natural_language = models.TextField()
    generated_sql = models.TextField()
    executed_sql = models.TextField(blank=True, null=True)
    result = models.JSONField(blank=True, null=True)
    error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'query_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.natural_language[:50]}... - {self.created_at}"