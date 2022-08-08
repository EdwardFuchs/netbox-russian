from django.apps import AppConfig


class DCIMConfig(AppConfig):
    name = "dcim"
    verbose_name = "Устройства"

    def ready(self):

        import dcim.signals
