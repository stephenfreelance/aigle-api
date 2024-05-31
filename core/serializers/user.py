from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class UserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = UserModel
        fields = [
            "uuid",
            "created_at",
            "updated_at",
            "email",
            "user_role",
            "deleted"
        ]
