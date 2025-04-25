from rest_framework import serializers
from api.models import Camper
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the Django User model."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CamperProfileSerializer(serializers.ModelSerializer):
    """Serializer for Camper profile data."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = Camper
        fields = [
            "id",
            "user",
            "payment_methods",
            "reservation_history",
            "age",
            "phone_number",
        ]
        read_only_fields = ["id", "user"]

