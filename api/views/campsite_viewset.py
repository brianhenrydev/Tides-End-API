from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Campsite, Reservation, Camper
from rest_framework import status
from datetime import date, timedelta
from calendar import monthrange

from api.models.amenities import Amenity, CampsiteAmenity
from api.models.review import Review
from api.serializers import CampsiteSerializer
from api.serializers import ReservationSerializer, ReviewSerializer
from api.serializers.campsite_serializers import AmenitySerializer


class CampsiteViewSet(ViewSet):
    def update(self, request, pk=None):
        """Update campsite details including amenities"""
        try:
            fields_to_update = [
                "site_number",
                "description",
                "price_per_night",
                "max_occupancy",
                "coordinates",
                "available",
            ]
            campsite_data = {
                key: request.data.get(key)
                for key in fields_to_update
                if key in request.data
            }

            # Get the list of amenity IDs from the request
            amenity_ids = request.data.get("amenities", [])

            # Convert to a list of integers if it's not already
            if isinstance(amenity_ids, list) and all(
                isinstance(item, int) for item in amenity_ids
            ):
                # List is already in correct format
                pass
            elif (
                isinstance(amenity_ids, list)
                and len(amenity_ids) > 0
                and isinstance(amenity_ids[0], dict)
            ):
                # Extract IDs from dict objects
                amenity_ids = [
                    amenity["id"] for amenity in amenity_ids if "id" in amenity
                ]
            else:
                # Handle any other format or empty list
                amenity_ids = []

            campsite_to_update = Campsite.objects.get(pk=pk)

            serializer = CampsiteSerializer(
                campsite_to_update, data=campsite_data, partial=True
            )

            if serializer.is_valid():
                try:
                    # Get existing amenities
                    current_amenities = CampsiteAmenity.objects.filter(
                        campsite=campsite_to_update
                    )
                    current_amenity_ids = set(ca.amenity.id for ca in current_amenities)

                    # Convert the incoming amenity IDs to a set
                    new_amenity_ids = set(amenity_ids)

                    # Find amenities to remove
                    amenities_to_remove = current_amenity_ids - new_amenity_ids
                    for amenity_id in amenities_to_remove:
                        CampsiteAmenity.objects.filter(
                            campsite=campsite_to_update, amenity_id=amenity_id
                        ).delete()

                    # Find amenities to add
                    amenities_to_add = new_amenity_ids - current_amenity_ids
                    for amenity_id in amenities_to_add:
                        # Make sure the amenity exists
                        try:
                            amenity = Amenity.objects.get(id=amenity_id)
                            CampsiteAmenity.objects.create(
                                campsite=campsite_to_update, amenity=amenity
                            )
                        except Amenity.DoesNotExist:
                            return Response(
                                {
                                    "detail": f"Amenity with ID {amenity_id} does not exist"
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

                    # Save the campsite updates
                    updated_campsite = serializer.save()

                    return Response(
                        CampsiteSerializer(
                            updated_campsite, context={"request": request}
                        ).data,
                        status=status.HTTP_200_OK,
                    )
                except Exception as ex:
                    return Response(
                        {"detail": f"Could not update amenities: {str(ex)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Campsite.DoesNotExist:
            return Response(
                {"detail": "Campsite not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as ex:
            return Response(
                {"detail": f"Error updating campsite: {str(ex)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
    def availability(self, request, pk=None):
        campsite = get_object_or_404(Campsite, id=pk)

        today = date.today()
        month = int(request.query_params.get("month", today.month))
        year = int(request.query_params.get("year", today.year))

        # Calculate start and end dates for the requested month
        start_date = date(year, month, 1)
        _, days_in_month = monthrange(year, month)
        end_date = start_date + timedelta(days=days_in_month)

        reservations = Reservation.objects.filter(
            campsite=campsite,
            check_in_date__lt=end_date,
            check_out_date__gte=start_date,
        )

        reserved_dates = set()
        for reservation in reservations:
            current_date = reservation.check_in_date
            while current_date <= reservation.check_out_date:
                reserved_dates.add(current_date)
                current_date += timedelta(days=1)

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

    @action(detail=True, methods=["post"], url_path="reserve")
    def reserve(self, request, pk=None):
        """Reservation for campsite"""
        try:
            check_in_date = request.data.get("check_in_date", "")
            check_out_date = request.data.get("check_out_date", "")
            number_of_guests = request.data.get("number_of_guests", "")

            if not check_in_date or not check_out_date or not number_of_guests:
                return Response(
                    {"message": "Missing parameters"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                number_of_guests = int(number_of_guests)
            except ValueError:
                return Response(
                    {"message": "Invalid number of guests"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                check_in_date = date.fromisoformat(check_in_date)
                check_out_date = date.fromisoformat(check_out_date)
            except ValueError:
                return Response(
                    {"message": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if check_in_date >= check_out_date:
                return Response(
                    {"message": "Check-in date must be before check-out date"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            print(f"Error getting parameters: {e}")
            return Response(
                {"message": "Error getting parameters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            campsite = get_object_or_404(Campsite, id=pk)
            camper = Camper.objects.get(user=request.auth.user)
        except Campsite.DoesNotExist:
            return Response(
                {"message": "Campsite not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Camper.DoesNotExist:
            return Response(
                {"message": "Camper not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error getting camper/campsite: {e}")
            return Response(
                {"message": "Error getting camper/campsite"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reservation = Reservation(
                campsite=campsite,
                camper=camper,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                number_of_guests=number_of_guests,
            )
            reservation.save()

            serialized_res = ReservationSerializer(
                reservation, context={"request": request}
            )

            return Response(serialized_res.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error creating reservation: {e}")
            return Response(
                {"message": f"Couldn't create Reservation: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        try:
            try:
                camper = get_object_or_404(Camper, user=request.auth.user)
            except Camper.DoesNotExist:
                return Response({"details": "There was a problem getting camper..."})
            try:
                comment = request.data.get("comment")
                rating = request.data.get("rating")
            except Exception as ex:
                return Response(
                    {"details": "There was a problem getting request data..."}
                )
            try:
                campsite = get_object_or_404(Campsite, id=pk)
            except Campsite.DoesNotExist:
                return Response({"details": "There was a problem getting campsite..."})

            new_review = Review()
            new_review.camper = camper
            new_review.campsite = campsite

            if comment is not None:
                new_review.comment = comment
            if rating is not None:
                new_review.rating = rating

            try:
                serialized_review = ReviewSerializer(new_review, data=request.data)
                valid = serialized_review.is_valid()
                if valid:
                    serialized_review.save()
                    return Response(
                        serialized_review.data, status=status.HTTP_201_CREATED
                    )
                return Response(
                    {"details": "There was a problem creating your review"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as ex:
                return Response(
                    {"details": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response({"details": "There was a problem..."})

    @action(detail=False, methods=["get", "post"], url_path="amenities")
    def amenities(self, request, pk=None):
        am = Amenity.objects.all()
        sam = AmenitySerializer(am, many=True)

        return Response(sam.data, status=status.HTTP_200_OK)
