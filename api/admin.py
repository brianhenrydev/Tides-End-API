from django.contrib import admin

# Register your models here.

from api.models import (
    Camper,
    PaymentMethod,
    Campsite,
    CampsiteImage,
    Amenity,
    CampsiteAmenity,
    Reservation,
    Review
)

admin.site.register(Camper)
admin.site.register(PaymentMethod)
admin.site.register(Campsite)
admin.site.register(CampsiteImage)
admin.site.register(Amenity)
admin.site.register(CampsiteAmenity)
admin.site.register(Reservation)
admin.site.register(Review)
