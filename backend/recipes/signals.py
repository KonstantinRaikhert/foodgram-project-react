import os

from django.db import models
from django.dispatch import receiver
from recipes.models import Recipe


@receiver(models.signals.post_delete, sender=Recipe)
def delete_file(sender, instance, *args, **kwargs):
    """Deletes image files on `post_delete`"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
