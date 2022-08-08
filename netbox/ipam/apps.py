from django.apps import AppConfig


class IPAMConfig(AppConfig):
    name = "ipam"
    verbose_name = "Сеть"

    def ready(self):
        import ipam.signals
