import logging

import google.auth.transport.requests
from google.oauth2.id_token import verify_oauth2_token
from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from authentication.models import AuthorizedUser
from hub.settings import GOOGLE_SECRET_KEY
from uvaq.models import PersonalInformation

logger = logging.getLogger(__name__)


class BaseOAuth2Authentication(BaseAuthentication):
    """
    Base class for handling OAuth2-based authentication.

    This class provides functionality for extracting and verifying bearer tokens,
    particularly for Google OAuth2, and retrieving user email information from the ID token.

    Methods:
        authenticate_bearer_token(token): Verifies the provided bearer token and extracts the institutional email.
        authenticate_header(request): Extracts and validates the authorization header from the request.

    Raises:
        AuthenticationFailed: Raised if the token is invalid or the authorization header is improperly formatted.
    """

    def authenticate_bearer_token(self, token):
        """
        Verifies the OAuth2 bearer token and extracts the user's email address.

        Args:
            token (str): The OAuth2 token provided by the client.

        Returns:
            str: The institutional email associated with the token.

        Raises:
            AuthenticationFailed: If the token is invalid or does not contain a valid email.
        """
        try:
            id_info = verify_oauth2_token(
                token,
                google.auth.transport.requests.Request(),
                audience=GOOGLE_SECRET_KEY,
            )

            # Check issuer
            if id_info.get("iss") not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise AuthenticationFailed("Invalid token issuer.")

            # Extract the institutional email
            institutional_email = id_info.get("email")
            if not institutional_email:
                raise AuthenticationFailed("The token does not contain a valid email.")
            return institutional_email

        except ValueError as e:
            logger.warning("Authentication failed: Invalid token.")
            raise AuthenticationFailed("Invalid token.")

    def authenticate_header(self, request):
        """
        Extracts and validates the authorization header from the request.

        Args:
            request (Request): The HTTP request containing the Authorization header.

        Returns:
            tuple: A tuple containing the authentication type and the token.

        Raises:
            AuthenticationFailed: If the authorization header is missing or improperly formatted.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise AuthenticationFailed("Authorization header is missing")

        try:
            auth_type, token = auth_header.split(" ", 1)
        except ValueError:
            raise AuthenticationFailed("Invalid Authorization header format")

        return auth_type.lower(), token


class IdPAuthentication(BaseOAuth2Authentication):
    """
    Authentication class for handling Identity Provider (IdP) based authentication.

    This class uses the OAuth2 token to extract the institutional email from the ID token.

    Methods:
        authenticate(request): Authenticates the request by extracting the bearer token and validating the email.

    Raises:
        AuthenticationFailed: If the token is invalid or the email is missing.
    """

    def authenticate(self, request):
        """
        Authenticates the request using a bearer token.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            tuple: A tuple containing None and the institutional email if authentication is successful.

        Raises:
            AuthenticationFailed: If authentication fails due to missing or invalid token.
        """
        auth_type, token = self.authenticate_header(request)
        if auth_type == "bearer":
            institutional_email = self.authenticate_bearer_token(token)
            if not institutional_email:
                raise AuthenticationFailed("The token does not contain a valid email.")

            try:
                personal_info = PersonalInformation.objects.get(
                    contact_info__institutional_email=institutional_email
                )
            except PersonalInformation.DoesNotExist:
                raise AuthenticationFailed("User not found in the university database.")

            user = UserProxy(personal_info)
            return (user, token)
        raise AuthenticationFailed(
            detail="Invalid authentication type. Bearer token required."
        )


class HybridAuthentication(BaseOAuth2Authentication):
    """
    Handles hybrid authentication using either bearer tokens (OAuth2) or Django's token authentication.

    This class first attempts to authenticate using an OAuth2 bearer token. If that fails, it falls back to Django's
    TokenAuthentication.

    Methods:
        authenticate(request): Authenticates the request using either OAuth2 bearer tokens or Django's token authentication.

    Raises:
        AuthenticationFailed: If both authentication methods fail.
    """

    def authenticate(self, request):
        """
        Authenticates the request using either a bearer token or Django token.

        Args:
            request (Request): The incoming HTTP request.

        Returns:
            tuple: A tuple containing the authenticated user and None, or None and the email if bearer token is used.

        Raises:
            AuthenticationFailed: If the authentication fails due to an invalid or unsupported token.
        """
        auth_type, token = self.authenticate_header(request)
        if auth_type.lower() == "bearer":
            try:
                institutional_email = self.authenticate_bearer_token(token)
                try:
                    authorized_user = AuthorizedUser.objects.get(
                        user__email=institutional_email
                    )
                    if not authorized_user.is_active:
                        raise AuthenticationFailed("User is not active.")

                    request.user = authorized_user.user
                    return (authorized_user.user, None)
                except AuthorizedUser.DoesNotExist:
                    raise AuthenticationFailed(
                        "User is not authorized to use this service."
                    )

            except ValueError as e:
                raise AuthenticationFailed(f"Invalid token: {str(e)}")

        elif auth_type.lower() == "token":
            user_auth = TokenAuthentication().authenticate(request)
            if user_auth:
                request.user = user_auth[0]
                return user_auth
            else:
                raise AuthenticationFailed("Invalid token or authentication failed.")

        else:
            raise AuthenticationFailed("Unsupported authorization type")


class UserProxy:
    def __init__(self, personal_info):
        self.personal_info = personal_info
        self.is_authenticated = True

    def __getattr__(self, attr):
        return getattr(self.personal_info, attr)
