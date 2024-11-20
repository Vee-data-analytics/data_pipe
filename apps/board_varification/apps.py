from django.apps import AppConfig

class BoardVarificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.board_varification"

    def ready(self):
        import board_varification.signals

