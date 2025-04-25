from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from api.models import Campsite

from api.serializers import CampsiteSerializer


class CampsiteViewSet(ViewSet):

    def list(self, request):
        """
        List all campsites
        """
        campsites = Campsite.objects.all()
        serializer = CampsiteSerializer(
            campsites, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Retrieve a campsite by ID
        """
        try:
            campsite = Campsite.objects.get(pk=pk)
            serializer = CampsiteSerializer(campsite, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Campsite.DoesNotExist:
            return Response(
                {"message": "Campsite not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        """
        Create a new campsite
        """
        serializer = CampsiteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

