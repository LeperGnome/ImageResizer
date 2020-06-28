from django.conf import settings
from django.db import models
from core.utils import generate_image_name


class ObjectManager(models.Manager):
    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None


class Image(models.Model):
    name = models.CharField(max_length=511, default=generate_image_name())
    img_file = models.ImageField(upload_to=settings.UPLOADS_URL)
    objects = ObjectManager()
