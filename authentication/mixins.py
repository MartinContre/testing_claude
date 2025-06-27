from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.exceptions import AuthenticationFailed

from authentication.decorators import authorized_user_required


class AuthorizedUserRequiredMixin(View):
    """
    Mixin that ensures the view requires the user to be authorized.

    This mixin wraps the dispatch method with the custom `authorized_user_required` decorator,
    which checks if the user is authorized. If the user is not authorized or authentication fails,
    a JSON response with an error message is returned.

    Methods:
        dispatch: Overrides the dispatch method to enforce authorization checks.

    Workflow:
        1. `authorized_user_required` checks if the user has valid authorization.
        2. If an `AuthenticationFailed` exception is raised, a JSON response with error details
           is returned to the client.
    """

    @method_decorator(authorized_user_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except AuthenticationFailed:
            return JsonResponse({"error": "Invalid Token"}, status=401)
