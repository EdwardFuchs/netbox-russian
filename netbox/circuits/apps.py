from django.apps import AppConfig


class CircuitsConfig(AppConfig):
    name = "circuits"
    verbose_name = "Каналы"

    def ready(self):
        import circuits.signals
