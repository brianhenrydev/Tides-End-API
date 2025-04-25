from rest_framework import serializers
from api.models import Camper, PaymentMethod, Reservation
from django.contrib.auth.models import User


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservation model."""

    class Meta:
        model = Reservation
        fields = [
            "id",
            "campsite",
            "check_in_date",
            "check_out_date",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model."""

    masked_card_number = serializers.SerializerMethodField()

    def get_masked_card_number(self, obj):
        """Return the masked card number."""
        try:
            return "**** **** **** " + str(obj.card_number)[-4:]
        except TypeError:
            # Handle cases where the card number is not accessible
            return "**** **** **** ****"

    class Meta:
        model = PaymentMethod
        fields = [
            "issuer",
            "masked_card_number",
            "cardholder_name",
            "expiration_date",
            "cvv",
            "billing_address",
            "is_default",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the Django User model."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CamperProfileSerializer(serializers.ModelSerializer):
    """Serializer for Camper profile data."""

    user = UserSerializer(read_only=True)
    payment_methods = serializers.SerializerMethodField()
    reservation_history = serializers.SerializerMethodField()

    def get_reservation_history(self, obj):
        """Get the reservation history for the camper."""
        reservations = obj.reservations.filter(
            camper=obj, status__in=["completed", "pending"]
        ).order_by("-check_in_date")
        return ReservationSerializer(reservations, many=True).data

    def get_payment_methods(self, obj):
        """Get the payment methods for the camper."""
        user_methods = PaymentMethod.objects.filter(camper=obj)
        return PaymentMethodSerializer(user_methods, many=True).data
        # Assuming you have a PaymentMethodSerializer defined elsewhere

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

