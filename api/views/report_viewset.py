from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.views import Response
from rest_framework.viewsets import ViewSet
from rest_framework import serializers
from api.models.reservation import Reservation
from django.db.models import Count
from django.db.models.functions import ExtractMonth
from collections import defaultdict
import datetime

from api.serializers.camper_serializers import ReservationSerializer

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
                { "endpoint": "admin/report/sales", "name": "Sales Report", "implemented": True },
            { "endpoint": "admin/analytics/reservations", "name": "Reservation Analytics", "implemented": False },
            { "endpoint": "admin/manage/campsites", "name": "Manage Sites", "implemented": True },
        ],
            "reservations": reservations.data
        },
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="sales")
    def sales_report(self, request ):
        """handles sales report data"""
        all_completed_reservations = Reservation.objects.filter(status="completed")
        data = ReservationSerializer(all_completed_reservations, many=True)
        total_sales = round(sum(res["total_price"] for res in data.data),2)
        return Response({
            "total_sales": total_sales,
        },status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="reservations")
    def reservation_report(self, request):
        """handles reservation report data"""
        # Get reservations grouped by month
        reservations_by_month = Reservation.objects.annotate(
            month=ExtractMonth('check_in_date')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        # Create a dictionary with all months initialized to 0
        month_data = defaultdict(int)
        for item in reservations_by_month:
            month_data[item['month']] = item['count']
        
        # Month name mapping
        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'June',
            7: 'July', 8: 'Aug', 9: 'Sept', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }
        
        # Format the result
        result = []
        for month_num in range(1, 13):
            result.append({
                'month': month_names[month_num],
                'reservations': month_data[month_num]
            })
        
        return Response(result, status=status.HTTP_200_OK)
