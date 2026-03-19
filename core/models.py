import uuid
from django.db import models
from pgvector.django import VectorField





class QueryHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
