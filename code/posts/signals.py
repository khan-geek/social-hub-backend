import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import Post

@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

@receiver(pre_save, sender=Post)
def auto_delete_old_post_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_image = Post.objects.get(pk=instance.pk).image
    except Post.DoesNotExist:
        return
    new_image = instance.image
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)
