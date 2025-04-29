from django.db import models
from .campsite import Campsite


class Amenity(models.Model):
    """
    Represents an amenity that can be associated with a campsite.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CampsiteAmenity(models.Model):
    """
    Many-to-many relationship between Campsite and Amenity.
    """

    campsite = models.ForeignKey(
        Campsite, on_delete=models.CASCADE, related_name="amenities"
    )
    amenity = models.ForeignKey(
        Amenity, on_delete=models.CASCADE, related_name="campsites"
    )

    class Meta:

        db_table = "campsite_amenity"
        verbose_name = "Campsite Amenity"
        verbose_name_plural = "Campsite Amenities"
        ordering = ["campsite", "amenity"]
        unique_together = ("campsite", "amenity")

    def __str__(self):
        return f"{self.campsite} - {self.amenity}"

