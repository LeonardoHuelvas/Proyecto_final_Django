# apps.py
from django.apps import AppConfig

class CoursesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'courses'

    def ready(self):
        from django.db.models.signals import post_save
        from django.contrib.auth.models import User
        from .signals import create_profile
        post_save.connect(create_profile, sender=User)
