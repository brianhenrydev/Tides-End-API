from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.views import Response
from rest_framework.viewsets import ViewSet
from rest_framework import serializers
from api.models.reservation import Reservation

class ReservationReportSerializer(serializers.ModelSerializer):
    """serializer for reservation report"""
    duration = serializers.SerializerMethodField()
    class Meta:
        model = Reservation
        fields = [
            "id",
            "campsite",
            "duration",
            "check_in_date",
            "check_out_date",
            "total_price",
            "status",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        depth = 0

    def get_duration(self,obj):
        """duration of trip"""
        if obj.check_in_date and obj.check_out_date:
            duration = obj.check_out_date - obj.check_in_date
            return f"{duration.days} days"
        return "0 days"


class ReportViewSet(ViewSet):
    permission_classes = [IsAdminUser]
    """Viewset for report data"""
    def list(self,request):
        """reports top level"""
        all_reservations = Reservation.objects.all()
        reservations = ReservationReportSerializer(all_reservations,  many=True, context={"request": request})

        return Response({
                "links": [
            { "endpoint": "admin/report/sales", "name": "Sales Report" },
            { "endpoint": "admin/analytics/reservations", "name": "Reservation Analytics" },
        ],
            "reservations": reservations.data
        },
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="sales")
    def sales_report(self, request ):
        """handles sales report data"""
        return Response("hi",status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="reservations")
    def reservation_report(self, request ):
        """handles reservation report data"""
        all_reservations = Reservation.objects.all()
        report = ReservationReportSerializer(all_reservations,  many=True, context={"request": request})

        return Response(report.data, status=status.HTTP_200_OK)
