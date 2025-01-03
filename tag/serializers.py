from rest_framework import serializers

from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name","id"]
        read_only_fields = ["id", "created_at", "modified_at", "user"]

class TagIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id"] 
        read_only_fields = ["id"] 