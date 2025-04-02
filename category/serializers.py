from rest_framework import serializers

from category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("name", "parent_name", "parent", "id", "description")
        read_only_fields = ["id", "created_at", "modified_at", "user"]

    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None

class CategoryIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id")
        read_only_fields = ["id"] 
