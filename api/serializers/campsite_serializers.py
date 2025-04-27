from rest_framework import serializers
from api.models import Campsite
from api.models import CampsiteImage

from api.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""

    username = serializers.SerializerMethodField()

    def get_username(self, obj):
        """Return the username of the camper who made the review."""
        return obj.camper.user.username if obj.camper and obj.camper.user else None

    class Meta:
        model = Review
        fields = [
            "id",
            "username",
            "rating",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        depth = 1


class CampsiteImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = CampsiteImage
        fields = ["id", "image_url"]
        depth = 1



class CampsiteSerializer(serializers.ModelSerializer):

    images = CampsiteImageSerializer(many=True, read_only=True)

    reviews = serializers.SerializerMethodField()
    """Serializer for Campsite model."""

    def get_reviews(self, obj):
        """Return the reviews for the campsite."""
        reviews = obj.reviews.all()
        return ReviewSerializer(reviews, many=True).data

    class Meta:
        model = Campsite
        fields = [
            "id",
            "site_number",
            "description",
            "coordinates",
            "reviews",
            "price_per_night",
            "max_occupancy",
            "available",
            "created_at",
            "updated_at",
            "images",
        ]
        depth = 1

