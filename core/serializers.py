from rest_framework import serializers


class QueryRequestSerializer(serializers.Serializer):
    connection_id = serializers.UUIDField()
    natural_language = serializers.CharField()
    generated_sql = serializers.CharField(required=False, allow_blank=True)


class SchemaSearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    connection_id = serializers.UUIDField(required=False)