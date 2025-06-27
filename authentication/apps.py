from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """
    Configuration class for the Authentication app.

    This class sets up the necessary configurations for the 'authentication' app, including
    the default auto field and the app's name.

    Attributes:
        default_auto_field (str): Specifies the type of field to use for auto-incrementing IDs.
        name (str): The name of the app as defined in Django settings.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
