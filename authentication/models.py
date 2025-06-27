from django.contrib.auth.models import User
from django.db import models


class AuthorizedUser(models.Model):
    """
    Extends Django's built-in User model with additional authorization fields.

    This model represents a user that has been authorized to access specific
    features of the system, such as user management.

    Attributes:
        user (User): A one-to-one relationship with the Django User model.
        is_authorized (bool): Indicates if the user has been authorized to use the system.
        can_manage_users (bool): Specifies if the user has the privilege to manage other users.
        is_active (bool): Determines if the user's account is active.
        date_joined (DateTimeField): The date and time when the user was authorized.

    Methods:
        __str__(): Returns the email of the associated user.
    Notes:
        - The `is_authorized` flag should be set to `True` when the user has been granted access to the system.
        - The `can_manage_users` flag allows for the designation of administrative privileges.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_authorized = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email
