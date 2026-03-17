from rest_framework import serializers
from .models import DatabaseConnection, SchemaDocument, QueryHistory


class DatabaseConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatabaseConnection
        fields = ['id', 'name', 'host', 'port', 'database', 'username', 'password', 'created_at', 'updated_at', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = super().create(validated_data)
        if password:
            instance.password = password
            instance.save()
        return instance


class SchemaDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchemaDocument
        fields = ['id', 'connection', 'name', 'content', 'uploaded_at']


class QueryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryHistory
        fields = ['id', 'connection', 'natural_language', 'generated_sql', 'executed_sql', 'result', 'error', 'created_at']


class QueryRequestSerializer(serializers.Serializer):
    connection_id = serializers.UUIDField()
    natural_language = serializers.CharField()
    generated_sql = serializers.CharField(required=False, allow_blank=True)


class SchemaSearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    connection_id = serializers.UUIDField(required=False)