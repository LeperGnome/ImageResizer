from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models
from django.http import Http404
import time


def generate_image_name() -> str:
    return f'image_{time.time()}'


class ObjectManager(models.Manager):
    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None

    def get_or_404(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404


class Image(models.Model):
    name = models.CharField(max_length=511, default=generate_image_name())
    img_file = models.ImageField()
    objects = ObjectManager()


class ResizedImage(models.Model):
    base = models.ForeignKey(Image, models.CASCADE)
    img_file = models.ImageField()
    width = models.IntegerField()
    height = models.IntegerField()
    size = models.IntegerField()
    objects = ObjectManager()
