# signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de que se guarda un objeto User.
    Crea un objeto Profile asociado al nuevo User.
    
    Args:
        sender (Model): El modelo que envía la señal.
        instance (User): La instancia del modelo que se acaba de guardar.
        created (bool): Un booleano que indica si se creó una nueva instancia.
        **kwargs: Parámetros adicionales.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal que se ejecuta después de que se guarda un objeto User.
    Guarda el perfil asociado al User.
    
    Args:
        sender (Model): El modelo que envía la señal.
        instance (User): La instancia del modelo que se acaba de guardar.
        **kwargs: Parámetros adicionales.
    """
    instance.profile.save()
