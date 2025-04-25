# api/urls.py
# pylint: disable=invalid-name
    
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AuthViewSet,
    CamperProfileViewSet,
    CampsiteViewSet
)

router = DefaultRouter(trailing_slash=False)
router.register(r"auth/profile", CamperProfileViewSet, basename="profile")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"campsites", CampsiteViewSet, basename="campsites")

urlpatterns = [
    path("", include(router.urls)),
]

