from api.serializers.campsite_serializers import CampsiteSerializer
from rest_framework import serializers
from api.models import Camper, PaymentMethod, Reservation
from django.contrib.auth.models import User


class ReservationSerializer(serializers.ModelSerializer):
    """Serializer for Reservation model."""
    campsite = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            "id",
            "campsite",
            "check_in_date",
            "check_out_date",
            "total_price",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        depth = 7


    def get_campsite(self, obj):
        """Get campsite for reservation"""
        
        return CampsiteSerializer(obj.campsite, many=False, context=self.context ).data



class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model."""
    masked_card_number = serializers.SerializerMethodField()
    expiration_date = serializers.SerializerMethodField()

    def get_expiration_date(self, obj):
        """Return the expiration date in MM/YY format."""
        try:
            # Assuming expiration_date is a date object
            return obj.expiration_date.strftime("%m/%y")
        except (AttributeError, TypeError):
            # Handle cases where the expiration date is not accessible or not a date
            return ""

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
            "id",
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
        fields = ["id", "username", "email", "first_name", "last_name" ]


class CamperProfileSerializer(serializers.ModelSerializer):
    """Serializer for Camper profile data."""
    user = UserSerializer(read_only=True)
    payment_methods = serializers.SerializerMethodField()
    reservation_history = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    def get_reservation_history(self, obj):
        """Get the reservation history for the camper."""
        reservations = obj.reservations.filter(
            camper=obj,
        ).order_by("-check_in_date")
        return ReservationSerializer(reservations, many=True, context=self.context).data

    def get_payment_methods(self, obj):
        """Get the payment methods for the camper."""
        user_methods = PaymentMethod.objects.filter(camper=obj)
        return PaymentMethodSerializer(user_methods, many=True).data
        # Assuming you have a PaymentMethodSerializer defined elsewhere
    def get_is_admin(self,obj):
        return obj.user.is_staff

    class Meta:
        model = Camper
        fields = [
            "id",
            "user",
            "is_admin",
            "payment_methods",
            "reservation_history",
            "age",
            "phone_number",
        ]
        read_only_fields = ["id", "user"]
        depth=5
