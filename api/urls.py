# api/urls.py
# pylint: disable=invalid-name
    
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views.report_viewset import ReportViewSet

from .views import (
    AuthViewSet,
    CamperProfileViewSet,
    CampsiteViewSet,
    ReportViewSet
)

router = DefaultRouter(trailing_slash=False)
router.register(r"auth/profile", CamperProfileViewSet, basename="profile")
router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"campsites", CampsiteViewSet, basename="campsite")
router.register(r"reports", ReportViewSet, basename="report")

urlpatterns = [
    path("", include(router.urls)),
]

