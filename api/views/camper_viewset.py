"""Python
Camper Profile ViewSet
This module contains the CamperProfileViewSet class, which handles
CRUD operations for camper profiles.
It includes methods for listing, updating, and deleting camper profiles.
It uses Django REST Framework for serialization and authentication.
It also includes permission checks to ensure that only authenticated users
can access certain endpoints.
Author: [Brian Henry]
Date: [2025-04-24]
"""

from inspect import stack
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models.functions import Lower
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action


from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.models.camper import PaymentMethod
from api.serializers import CamperProfileSerializer
from api.models import Camper, Reservation


def convert_expiration_date(mm_yy):
    try:
        # Parse the MM/YY format
        date_obj = datetime.strptime(mm_yy, "%m/%y")
        # Create a new date object with the first day of the month
        iso_date = date_obj.replace(day=1)
        # Return the ISO format
        return iso_date.isoformat().split("T")[0]  # This will return 'YYYY-MM-DD'
    except ValueError:
        raise ValueError("Date must be in MM/YY format.")


class CamperProfileViewSet(ViewSet):
    """ViewSet for managing camper profiles."""

    serializer_class = CamperProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]


    def list(self, request):
        """Handle GET requests for camper profile."""
        if request.user.is_anonymous:
            return Response(
                {
                    "message": "Welcome, guest user! Please log in to access your profile."
                },
                status=status.HTTP_200_OK,
            )
        camper = Camper.objects.filter(user=request.auth.user).first()
        if camper:
            serialized_camper = self.serializer_class(
                camper, many=False, context={"request": request}
            )
            return Response(
                serialized_camper.data,
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "No camper profile found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def update(self, request, pk=None):
        """Handle PUT requests to update an existing camper profile."""
        
        user = request.auth.user
    
        # Attempt to retrieve the camper profile
        try:
            camper = Camper.objects.get(user=user)
        except Camper.DoesNotExist:
            return Response(
                {"message": "Camper profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
    
        # Extract data from the request
        new_first_name = request.data.get("first_name")
        new_username = request.data.get("username")
        new_last_name = request.data.get("last_name")
        new_email = request.data.get("email")
        new_age = request.data.get("age")
        new_phone_number = request.data.get("phone_number")
    
        # Update camper profile fields only if new values are provided
        if new_age is not None:
            camper.age = new_age
        if new_phone_number is not None:
            camper.phone_number = new_phone_number
        camper.save()
    
        # Update user profile fields only if new values are provided
        if new_username is not None:
            user.username = new_username
        if new_first_name is not None:
            user.first_name = new_first_name
        if new_last_name is not None:
            user.last_name = new_last_name
        if new_email is not None:
            user.email = new_email
        user.save()
    
        return Response({"message": "Camper profile updated successfully."}, status=status.HTTP_200_OK)

    def destroy(self, request):
        """Handle DELETE requests to delete a camper profile."""
        try:
            camper = Camper.objects.get(user=request.auth.user)
        except Camper.DoesNotExist:
            return Response(
                {"message": "Camper profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.auth.user != camper.user:
            return Response(
                {"message": "You do not have permission to delete this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        camper.delete()
        return Response(
            {"message": "Camper Profile deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, methods=["post"], url_path="addpaymentmethod")
    def add_payment_method(self, request):
        """
        Add a payment method for the camper.
        Expected request.data:
        {
            "issuer": "Visa",  # Choices: "Visa", "MasterCard", "Amex"
            "card_number": "4111111111111111",
            "cardholder_name": "John Doe",
            "expiration_date": "2024-12",  # ISO format: YYYY-MM
            "cvv": "123",
            "billing_address": "123 Main St, Anytown, USA",
            "is_default": True
        }
        """
        # Get the Camper instance associated with the logged-in user.
        try:
            camper = Camper.objects.get(user=request.auth.user)
        except Camper.DoesNotExist:
            return Response(
                {"detail": "Camper not found for the current user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Extract fields from request.data.
        issuer = request.data.get("issuer", "").strip()
        card_number = request.data.get("card_number", "").strip()
        cardholder_name = request.data.get("cardholder_name", "").strip()
        expiration_date = request.data.get("expiration_date", "").strip()
        cvv = request.data.get("cvv", "").strip()
        billing_address = request.data.get("billing_address", "").strip()
        is_default = request.data.get("is_default", False)

        # You could perform additional validation here (e.g., card number format, expiration date, etc.).
        if not issuer or issuer.lower() not in ["visa", "mastercard", "amex", "discover"]:
            return Response(
                {"detail": "A valid issuer is required (Visa, MasterCard, Amex)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (
            not card_number
            or not cardholder_name
            or not expiration_date
            or not cvv
            or not billing_address
        ):
            return Response(
                {"detail": "Missing payment method fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        expiration_date = convert_expiration_date(expiration_date)

        # If the new payment method is marked as default, update other payment methods.
        if is_default:
            PaymentMethod.objects.filter(camper=camper, is_default=True).update(
                is_default=False
            )

        # Create a new PaymentMethod object.
        payment_method = PaymentMethod.objects.create(
            camper=camper,
            issuer=issuer,
            card_number=card_number,
            cardholder_name=cardholder_name,
            expiration_date=expiration_date,
            cvv=cvv,
            billing_address=billing_address,
            is_default=is_default,
        )

        # Return a successful response. You might also want to include the PaymentMethod data.
        return Response(
            {
                "detail": "Payment method added successfully.",
                "payment_method_id": payment_method.id,
                "issuer": payment_method.issuer,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="removepaymentmethod")
    def remove_payment_method(self, request):
        """
        Remove a payment method for the camper.

        Expected request.data:
        {
            "payment_method_id": 123
        }
        """
        try:
            camper = Camper.objects.get(user=request.auth.user)
        except Camper.DoesNotExist:
            return Response(
                {"detail": "Camper not found for the current user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment_method_id = request.data.get("payment_method_id")
        if not payment_method_id:
            return Response(
                {"detail": "Payment method id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment_method = PaymentMethod.objects.get(
                id=payment_method_id, camper=camper
            )
        except PaymentMethod.DoesNotExist:
            return Response(
                {
                    "detail": "Payment method not found or not associated with this camper."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        payment_method.delete()

        return Response(
            {"detail": "Payment method removed successfully."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="cancel-reservation")
    def cancel_reservation(self, request):
        """
        Cancel a reservation for the authenticated user.

        Requires:
        - reservation_id: ID of the reservation to cancel

        Returns:
        - 204 No Content on success
        - 400 Bad Request if reservation_id is invalid or missing
        - 404 Not Found if reservation doesn't exist
        - 403 Forbidden if user doesn't own the reservation
        """
        try:
            # Validate input
            reservation_id = request.data.get("reservation_id")
            if not reservation_id:
                return Response(
                    {"error": "Reservation ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

                # Get the current user's camper profile
            try:
                camper = Camper.objects.get(user=request.user)
            except Camper.DoesNotExist:
                return Response(
                    {"error": "Camper profile not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Find the reservation
            try:
                reservation = Reservation.objects.get(pk=reservation_id)
            except Reservation.DoesNotExist:
                return Response(
                    {"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Verify ownership
            if reservation.camper.id != camper.id:
                return Response(
                    {"error": "You do not have permission to cancel this reservation"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            reservation.delete()
            return Response(
                {"message": "Reservation cancelled successfully"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Log the exception
            logger.error(f"Error cancelling reservation: {str(e)}")
            return Response(
                {"error": "An error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
