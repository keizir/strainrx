from django.apps import AppConfig


class BusinessConfig(AppConfig):
    name = 'web.businesses'
    verbose_name = "Businesses"

    def ready(self):
        """Override this to put in:
            Users system checks
            Users signal registration
        """
        pass
