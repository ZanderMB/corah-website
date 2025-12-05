from django.apps import AppConfig


class CorahConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CORAH'

    def ready(self):
        from . import signals 