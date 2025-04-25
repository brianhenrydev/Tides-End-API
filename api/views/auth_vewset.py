from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login as auth_login
from rest_framework import status
import json


class AuthViewSet(ViewSet):
    """ViewSet for handling authentication (login and register)."""

    permission_classes = [AllowAny]  # Allow unauthenticated access

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """Handle user login."""
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "@" in username:
            try:
                user = User.objects.get(email=username)
                username = user.username
            except User.DoesNotExist:
                return Response(
                    {"error": "Invalid credentials."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            authenticated_user = authenticate(username=username, password=password)
        else:
            authenticated_user = authenticate(username=username, password=password)
        if authenticated_user is not None:
            token, _ = Token.objects.get_or_create(user=authenticated_user)
            auth_login(request, authenticated_user)
            return Response(
                {"valid": True, "token": token.key, "id": authenticated_user.id},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """Handle user registration."""
        # Load the JSON string of the request body into a dict
        req_body = json.loads(request.body.decode("utf-8"))

        # Create a new user by invoking the `create_user` helper method
        # on Django's built-in User model
        if User.objects.filter(username=req_body["username"]).exists():
            return HttpResponse(
                {"error": "Username already exists"},
                content_type="application/json",
                status=status.HTTP_400_BAD_REQUEST,
            )
        new_user = User.objects.create_user(
            username=req_body["username"],
            email=req_body["email"],
            password=req_body["password"],
            first_name=req_body["first_name"],
            last_name=req_body["last_name"],
        )
        new_user.save()

        camper = Camper.objects.create(
            user=new_user,
            age=data.get("age"),
            phone_number=data.get("phone_number"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            country=data.get("country"),
        )  # Assuming Camper has a OneToOneField with User

        # Commit the user to the database by saving it
        camper.save()

        # Use the REST Framework's token generator on the new user account
        token = Token.objects.create(user=new_user)
        token.save()

        # Return the token to the client
        data = {"token": token.key, "id": new_user.id}
        return Response(
            data, status=status.HTTP_201_CREATED
        )

