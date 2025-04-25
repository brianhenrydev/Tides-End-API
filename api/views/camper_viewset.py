
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

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from api.serializers import CamperProfileSerializer


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
        try:
            camper = Camper.objects.get(user=request.auth.user)
        except Camper.DoesNotExist:
            return Response(
                {"message": "Camper profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.auth.user != camper.user:
            return Response(
                {"message": "You do not have permission to update this profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            camper, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

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
