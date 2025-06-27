from django.contrib import admin

from .models import AuthorizedUser


@admin.register(AuthorizedUser)
class AuthorizedUserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the AuthorizedUser model.

    This class customizes the display of the AuthorizedUser instances in the Django admin interface.
    It defines which fields will be displayed in the list view of AuthorizedUser records.

    Attributes:
        list_display (tuple): Fields that will be shown in the AuthorizedUser list in the admin panel.
            - user: Displays the associated User object.
            - is_authorized: Shows whether the user is authorized.
            - can_manage_users: Shows whether the user has permissions to manage other users.
            - is_active: Displays if the user is currently active.
            - date_joined: Displays the date the user was created.
    """

    list_display = (
        "user",
        "is_authorized",
        "can_manage_users",
        "is_active",
        "date_joined",
    )
