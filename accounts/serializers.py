from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from accounts.models import User
from story.models import Story

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "alias", "password")

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))
        return value

    def validate_alias(self, value):
        if User.objects.filter(alias=value).exists():
            raise ValidationError("This alias already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            alias=validated_data["alias"],
        )
        user.is_active = False
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    story_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "alias", "date_joined", "story_count")

    def get_story_count(self, obj):
        return Story.objects.filter(user=obj).count()

class UserRoleSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("role","id")

    def get_role(self, obj):
        return obj.type

class ChangePasswordAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("password", "confirm_password")

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
