# api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
# pylint: disable=invalid-name

router = DefaultRouter(trailing_slash=False)

urlpatterns = [
    path("", include(router.urls)),
]

