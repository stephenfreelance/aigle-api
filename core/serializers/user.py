from djoser.serializers import UserSerializer as UserSerializerBase
from django.contrib.auth import get_user_model

from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(UserSerializerBase):
    class Meta(UserSerializerBase.Meta):
        model = UserModel
        fields = ["uuid", "created_at", "updated_at", "email", "user_role", "deleted"]

    email = serializers.CharField()


class UserInputSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ["email", "user_role", "deleted", "password"]

    password = serializers.CharField()

    def update(self, instance, validated_data):
        password_clear = validated_data.pop("password", None)

        if password_clear:
            instance.set_password(password_clear)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        return instance
