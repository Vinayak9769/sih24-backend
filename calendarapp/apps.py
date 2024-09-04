from django.apps import AppConfig


class CalenderAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendarapp'

    def ready(self):
        import calendarapp.signals
