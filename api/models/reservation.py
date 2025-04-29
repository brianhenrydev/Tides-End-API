from django.db import models

# Import necessary models
from api.models import Camper
from api.models import Campsite


class Reservation(models.Model):
    """
    Model representing a reservation made by a camper at a campground.
    """

    class Meta:
        verbose_name = "Reservation"
        verbose_name_plural = "Reservations"
        ordering = ["check_in_date"]  # Order by check-in date

    # Define the fields for the Reservation model
    # Foreign key to the Camper model
    camper = models.ForeignKey(
        Camper, on_delete=models.CASCADE, related_name="reservations"
    )
    # Foreign key to the Campsite model
    campsite = models.ForeignKey(
        Campsite, on_delete=models.CASCADE, related_name="reservations"
    )
    # Check-in date
    check_in_date = models.DateField()
    # Check-out date
    check_out_date = models.DateField()
    # Number of guests
    number_of_guests = models.PositiveIntegerField()
    # Created at timestamp
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # Updated at timestamp
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        """gets total price of reservation"""
        stay_duration = (self.check_out_date - self.check_in_date).days
        price_per_night = self.campsite.price_per_night
        return round(stay_duration * price_per_night,2)

    def __str__(self):
        return f"Reservation  {self.check_in_date} to {self.check_out_date}"
