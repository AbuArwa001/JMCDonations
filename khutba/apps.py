from django.apps import AppConfig

class KhutbaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'khutba'

    def ready(self):
        import khutba.signals
