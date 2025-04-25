from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Campsite, Reservation
from rest_framework import status
from datetime import date, timedelta
from calendar import monthrange

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

    @action(detail=True, methods=["get"], url_path="availability")
    def availability(self,request, pk=None):
        # Get the campsite object
        campsite = get_object_or_404(Campsite, id=pk)

        # Get query parameters for month and year
        today = date.today()
        month = int(request.query_params.get("month", today.month))
        year = int(request.query_params.get("year", today.year))

        # Calculate start and end dates for the requested month
        start_date = date(year, month, 1)
        _, days_in_month = monthrange(year, month)
        end_date = start_date + timedelta(days=days_in_month)

        # Get all reservations for the campsite in the date range
        reservations = Reservation.objects.filter(
            campsite=campsite,
            check_in_date__lt=end_date,
            check_out_date__gte=start_date,
        )

        # Create a set of all reserved dates
        reserved_dates = set()
        for reservation in reservations:
            current_date = reservation.check_in_date
            while current_date <= reservation.check_out_date:
                reserved_dates.add(current_date)
                current_date += timedelta(days=1)

        # Create a list of all dates in the range with their availability
        all_dates = []

        current_date = start_date
        while current_date < end_date:
            all_dates.append(
                {
                    "date": current_date,
                    "day": current_date.strftime("%A"),
                    "month": current_date.strftime("%B"),
                    "year": current_date.year,
                    "day_number": current_date.day,
                    "month_number": current_date.month,
                    "year_number": current_date.year,
                    "available": current_date >= today
                    and current_date not in reserved_dates,
                }
            )
            current_date += timedelta(days=1)

        # Return the available dates as a JSON response
        return Response(all_dates, status=status.HTTP_200_OK)

