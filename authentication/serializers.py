from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from .models import AuthorizedUser


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model.

    This serializer handles the serialization and deserialization of User instances,
    allowing the creation and updating of users while ensuring that sensitive information,
    such as the password, is handled securely.

    Attributes:
        Meta: Defines the model and fields to be serialized.

    Methods:
        validate_email(value): Ensures that the provided email is unique.
        validate_username(value): Ensures that the provided username is unique.
        create(validated_data): Creates a new user with a hashed password.
        update(instance, validated_data): Updates an existing user's details, including password changes.
    """

    class Meta:
        """
        Metadata for UserSerializer. Specifies the model and fields to be serialized.

        Fields:
            - first_name: User's first name.
            - last_name: User's last name.
            - username: Username for the user.
            - email: Email address for the user.
            - password: Write-only field to handle passwords securely.
        """

        model = User
        fields = ["first_name", "last_name", "username", "email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """
        Validates that the email is unique in the User table.

        Args:
            value (str): The email provided for the user.

        Raises:
            serializers.ValidationError: If the email is already in use.

        Returns:
            str: The validated email.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_username(self, value):
        """
        Validates that the username is unique in the User table.

        Args:
            value (str): The username provided for the user.

        Raises:
            serializers.ValidationError: If the username is already in use.

        Returns:
            str: The validated username.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already in use.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Creates a new user, setting the password securely.

        Args:
            validated_data (dict): The validated data for creating a new user.

        Returns:
            User: The newly created User instance.
        """
        user = User(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Updates an existing user instance, including password updates if provided.

        Args:
            instance (User): The existing user instance to update.
            validated_data (dict): The validated data for updating the user.

        Returns:
            User: The updated User instance.
        """
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        password = validated_data.get("password", None)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class AuthorizedUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the AuthorizedUser model, which extends the User model with additional authorization fields.

    This serializer handles both the User instance and the AuthorizedUser-specific fields such as
    `is_authorized` and `can_manage_users`.

    Attributes:
        user (UserSerializer): A nested serializer for the related User instance.

    Methods:
        create(validated_data): Creates an AuthorizedUser and the associated User.
        update(instance, validated_data): Updates the AuthorizedUser and the nested User.

    """

    user = UserSerializer()

    class Meta:
        """
        Metadata for AuthorizedUserSerializer. Specifies the model and fields to be serialized.

        Fields:
            - id: The primary key for the AuthorizedUser.
            - user: A nested serializer for the User details.
            - is_authorized: Indicates if the user is authorized to access specific features.
            - can_manage_users: Indicates if the user has the privilege to manage other users.
        """

        model = AuthorizedUser
        fields = ["id", "user", "is_authorized", "can_manage_users"]

    @transaction.atomic
    def create(self, validated_data):
        """
        Creates an AuthorizedUser and the associated User instance.

        Args:
            validated_data (dict): The validated data for creating an AuthorizedUser, including user details.

        Returns:
            AuthorizedUser: The newly created AuthorizedUser instance.
        """
        user_data = validated_data.pop("user")
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        authorized_user, created = AuthorizedUser.objects.update_or_create(
            user=user, defaults=validated_data
        )
        return authorized_user

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Updates an existing AuthorizedUser instance and its associated User.

        Args:
            instance (AuthorizedUser): The AuthorizedUser instance to update.
            validated_data (dict): The validated data for updating the AuthorizedUser.

        Returns:
            AuthorizedUser: The updated AuthorizedUser instance.

        Raises:
            serializers.ValidationError: If the nested user data is invalid.
        """
        user_data = validated_data.pop("user", None)
        if user_data:
            user_instance = instance.user
            user_serializer = UserSerializer(
                user_instance, data=user_data, partial=True
            )
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise serializers.ValidationError(user_serializer.errors)

        # Update AuthorizedUser-specific fields
        instance.is_authorized = validated_data.get(
            "is_authorized", instance.is_authorized
        )
        instance.can_manage_users = validated_data.get(
            "can_manage_users", instance.can_manage_users
        )
        instance.save()
        return instance
