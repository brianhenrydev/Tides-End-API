"""Camper and Payment Method models for the application.
This module defines the Camper and PaymentMethod models, which are used to
store information about campers and their payment methods.
The Camper model includes fields for the user's age and phone number,
while the PaymentMethod model includes fields for the cardholder's name,
expiration date, and a flag indicating whether the payment method is the default.
The models are linked through a one-to-one relationship with the User model
and a foreign key relationship with the Camper model.
"""

from django.db import models
from django.contrib.auth.models import User


class Camper(models.Model):
    """Model representing a camper's profile."""
    # The camper is linked to a user account
    # using a one-to-one relationship with the User model.
    # This allows us to extend the User model with additional fields
    # specific to campers, such as age and phone number.
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="camper_profile"
    )
    age = models.PositiveIntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)


class PaymentMethod(models.Model):
    """Model representing a payment method for a camper."""

    camper = models.ForeignKey(
        Camper, on_delete=models.CASCADE, related_name="payment_methods"
    )
    issuer = models.CharField(
        max_length=50,
        choices=[
            ("Visa", "Visa"),
            ("MasterCard", "MasterCard"),
            ("Amex", "American Express"),
        ],
    )
    card_number = models.PositiveIntegerField()
    cardholder_name = models.CharField(max_length=100)
    expiration_date = models.DateField()
    cvv = models.PositiveIntegerField()
    billing_name = models.CharField(max_length=255, blank=True, null=True)
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

