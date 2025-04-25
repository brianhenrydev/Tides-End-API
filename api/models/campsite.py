from django.db.models import Model
from django.core.validators import FileExtensionValidator
from django.contrib.gis.db import models


class CampsiteImage(Model):
    campsite = models.ForeignKey(
        "Campsite", related_name="images", on_delete=models.CASCADE
    )
    image_url = models.ImageField(
        upload_to="campsite_images",
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Campsite(Model):
    site_number = models.CharField(max_length=255)
    description = models.TextField()
    coordinates = models.CharField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_occupancy = models.IntegerField()
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.site_number

