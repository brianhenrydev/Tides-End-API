from django.db import models

from .campsite import Campsite
from .camper import Camper


class Review(models.Model):
    camper = models.ForeignKey(Camper, on_delete=models.CASCADE, related_name="reviews")
    campsite = models.ForeignKey(
        Campsite, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )  # Rating from 1 to 5

    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.camper.user.username} for {self.campground.site_number} - {self.rating} Stars"
