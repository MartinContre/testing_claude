from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.hybrid_authentication import HybridAuthentication
from authentication.serializers import AuthorizedUserSerializer

from .models import AuthorizedUser


class LoginView(APIView):
    """
    API View for user login and token generation.

    This view handles user login by authenticating the user's email and password.
    If authentication is successful, it generates an authentication token for the user.

    Methods:
        post: Authenticates the user and returns a token upon successful login.

    Workflow:
        1. The user submits an email and password.
        2. The view verifies if the user exists and if the password is correct.
        3. If the user is authorized, a token is generated or retrieved.
        4. Returns the token if login is successful, or an error if it fails.

    """

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            # Check if a user with the given email exists
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                try:
                    # Check if the user is authorized
                    authorized_user = AuthorizedUser.objects.get(user=user)
                    if not authorized_user.is_authorized:
                        return Response(
                            {"error": "User is not authorized"},
                            status=status.HTTP_403_FORBIDDEN,
                        )

                    # Generate or retrieve token
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({"token": token.key}, status=status.HTTP_200_OK)

                except AuthorizedUser.DoesNotExist:
                    return Response(
                        {"error": "User not found in AuthorizedUser database"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found with this email"},
                status=status.HTTP_404_NOT_FOUND,
            )


class AuthorizedUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing authorized users.

    This ViewSet handles CRUD operations on the `AuthorizedUser` model. It ensures that only authenticated
    users can access the actions and allows filtering of active users in the queryset.

    Attributes:
        queryset (QuerySet): The queryset used for retrieving authorized users.
        serializer_class (Serializer): The serializer used for handling AuthorizedUser objects.
        authentication_classes (list): Custom authentication methods, including HybridAuthentication.
        permission_classes (list): Permissions required to access the view (IsAuthenticated).

    Methods:
        create: Creates a new AuthorizedUser.
        partial_update: Updates specific fields of an AuthorizedUser.
        destroy: Soft deletes an AuthorizedUser by marking it as inactive.
        list: Lists all active AuthorizedUsers.
        retrieve: Retrieves a single AuthorizedUser by ID.
        check_can_manage_users: Verifies if the current user has permission to manage other users.

    Example:
        {
        "user": {
            "first_name": "first_name",
            "last_name": "last_name",
            "username": "username",
            "email": "mail@uvaq.edu.mx",
            "password": "password"
        },
        "is_authorized": true,
        "can_manage_users": true
    }
    """

    queryset = AuthorizedUser.objects.all()
    serializer_class = AuthorizedUserSerializer
    authentication_classes = [HybridAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return only active authorized users.

        This method filters the queryset to return only those users that are marked as active.
        """
        return AuthorizedUser.objects.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        """
        Create a new AuthorizedUser.

        Inherits the default create behavior from ModelViewSet.
        """
        return super().create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an AuthorizedUser.

        This method allows updating certain fields of an AuthorizedUser without modifying the entire record.
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete an AuthorizedUser by marking it as inactive.

        Instead of fully deleting the record, it sets the `is_active` field to False.
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        List all active AuthorizedUsers.

        Inherits the default list behavior from ModelViewSet.
        """
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific AuthorizedUser by ID.

        Inherits the default retrieve behavior from ModelViewSet.
        """
        return super().retrieve(request, *args, **kwargs)

    def check_can_manage_users(self, request):
        """
        Verify if the current user has permission to manage other users.

        This method checks if the current user can manage other users based on the `can_manage_users` field.

        Raises:
            PermissionDenied: If the user is not allowed to manage other users or does not exist.
        """
        user_email = request.user.email
        try:
            user = AuthorizedUser.objects.get(email=user_email)
            if not user.can_manage_users:
                raise PermissionDenied("You do not have permission to manage users.")
        except AuthorizedUser.DoesNotExist:
            raise PermissionDenied("User not found.")
