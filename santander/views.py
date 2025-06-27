import logging

from rest_framework import status, viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler

from authentication.hybrid_authentication import IdPAuthentication
from uvaq.models import PersonalInformation

from .serializers import SantanderPersonSerializer

logger = logging.getLogger(__name__)


# class SantanderCredentialViewSet(viewsets.ViewSet):
#     authentication_classes = [IdPAuthentication]
#     permission_classes = [IsAuthenticated]

#     def handle_exception(self, exc):
#         response = exception_handler(exc, self.get_exception_handler_context())
#         if isinstance(exc, AuthenticationFailed):
#             return Response(
#                 {
#                     "detail": str(exc.detail),
#                     "status_code": 401,
#                 },
#                 status=status.HTTP_401_UNAUTHORIZED,
#             )
#         elif isinstance(exc, PersonalInformation.DoesNotExist):
#             return Response(
#                 {
#                     "detail": "User not found in the university database",
#                     "status_code": 404,
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )
#         elif response is not None:
#             # Handle generic server errors
#             if 500 <= response.status_code < 600:
#                 return Response(
#                     {
#                         "detail": "University server has an error",
#                         "status_code": response.status_code,
#                     },
#                     status=response.status_code,
#                 )
#         return response

#     def list(self, request):
#         user = request.user

#         if not user.has_content():
#             return Response(
#                 {
#                     "detail": "User has been found, but the user has not content",
#                     "status_code": 204,
#                 },
#                 status=status.HTTP_204_NO_CONTENT,
#             )

#         serializer = SantanderPersonSerializer(user)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class SantanderCredentialViewSet(viewsets.ViewSet):
    authentication_classes = [IdPAuthentication]
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        response = exception_handler(exc, self.get_exception_handler_context())
        if isinstance(exc, AuthenticationFailed):
            return Response(
                {
                    "detail": str(exc.detail),
                    "status_code": 401,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        elif isinstance(exc, PersonalInformation.DoesNotExist):
            return Response(
                {
                    "detail": "User not found in the university database",
                    "status_code": 404,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        elif response is not None:
            # Handle generic server errors
            if 500 <= response.status_code < 600:
                return Response(
                    {
                        "detail": "University server has an error",
                        "status_code": response.status_code,
                    },
                    status=response.status_code,
                )
            # Si response existe pero no entra en ninguna condición, la retornamos
            return response

        # Si response es None, devolvemos un error genérico
        return Response(
            {
                "detail": "Unhandled exception",
                "status_code": 500,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    def list(self, request):
        user = request.user

        if not user.has_content():
            return Response(
                {
                    "detail": "User has been found, but the user has not content",
                    "status_code": 204,
                },
                status=status.HTTP_204_NO_CONTENT,
            )

        serializer = SantanderPersonSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
