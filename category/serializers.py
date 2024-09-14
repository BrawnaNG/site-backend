from rest_framework import serializers

from category.models import Category


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("name", "parent_name", "parent")
        read_only_fields = ["id", "created_at", "modified_at", "user"]

    def get_parent_name(self, obj):
        if obj.parent:
            return obj.parent.name
        return None
