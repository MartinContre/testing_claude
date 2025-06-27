from rest_framework.exceptions import PermissionDenied

from authentication.hybrid_authentication import HybridAuthentication

from .models import AuthorizedUser


def authorized_user_required(view_func):
    """
    Decorator to ensure that a user is authorized to access a specific view.

    This decorator uses a custom authentication mechanism (`HybridAuthentication`) to check
    if a user is authenticated and authorized to perform an action. If the user is not authorized,
    a `PermissionDenied` exception is raised.

    Args:
        view_func (function): The view function to protect with this decorator.

    Returns:
        function: The wrapped view function that includes the authorization check.

    Raises:
        PermissionDenied: If the user is not authenticated, not authorized, or not active.

    Workflow:
        1. Authenticates the user using `HybridAuthentication`.
        2. Checks if the user exists in the `AuthorizedUser` model.
        3. Validates that the user is active and has the necessary permissions.
    """

    def _wrapped_view(request, *args, **kwargs):
        # Authenticate the user using the custom HybridAuthentication method
        user_auth = HybridAuthentication().authenticate(request)
        if user_auth is None:
            raise PermissionDenied("Authentication failed.")

        try:
            user, _ = user_auth
            user_email = user.email if user else None

            if user_email:
                # Check if the user exists and is authorized
                authorized_user = AuthorizedUser.objects.filter(
                    user__email=user_email
                ).first()

                if not authorized_user:
                    raise PermissionDenied("User is not authorized.")
                if not authorized_user.is_active:
                    raise PermissionDenied("User is not active.")
                if not authorized_user.is_authorized:
                    raise PermissionDenied(
                        "User does not have permission to perform this action."
                    )
            else:
                raise PermissionDenied("Invalid token or authentication failed.")
        except Exception as e:
            raise PermissionDenied(str(e))

        return view_func(request, *args, **kwargs)

    return _wrapped_view
