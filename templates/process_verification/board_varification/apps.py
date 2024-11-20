from django.apps import AppConfig

class BoardVarificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "board_varification"

    def ready(self):
        import board_varification.signals

