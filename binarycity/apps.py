from django.apps import AppConfig


class BinarycityConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'binarycity'

    def ready(self):
        """Import signal handlers when the app is ready"""
        from . import viewssendnoti
