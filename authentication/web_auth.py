import logging

from django.conf import settings
from django.contrib.sessions.models import Session
from rest_framework import authentication

logger = logging.getLogger(__name__)


class WebUploadAuthentication(authentication.BaseAuthentication):
    """Autenticación especial para flujos web de subida de CSV"""

    def authenticate(self, request):
        # Ignorar autenticación DRF para rutas específicas
        if "/v1/api/tievolucion/" in request.path and "upload" in request.path:
            logger.debug(f"Bypassing DRF auth for web upload: {request.path}")
            return self.handle_web_flow(request)

        # Continuar con autenticación normal para otras rutas
        return None

    def handle_web_flow(self, request):
        """Maneja autenticación por sesión para flujos web"""
        session_key = request.session.session_key
        upload_type = request.path.split("/")[
            4
        ]  # Extrae 'staff', 'professor' o 'student'

        if request.session.get(f"{upload_type}_authenticated"):
            logger.info(f"Session auth valid for {upload_type} upload")
            return (AnonymousUser(), None)  # Usuario anónimo controlado por sesión

        logger.warning(f"Web auth required for {upload_type} upload")
        raise authentication.AuthenticationFailed("Requiere autenticación web")

    def authenticate_header(self, request):
        """Header personalizado para flujos web"""
        return "WebSessionAuth"
