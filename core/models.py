from django.db import models


class ObjectManager(models.Manager):
    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return None


class Image(models.Model):
    path = models.ImageField()
    objects = ObjectManager()
