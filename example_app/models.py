import uuid
from django.db import models


# Create your models here.
class SimpleModel(models.Model):
    char_field = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    datetime = models.DateTimeField(auto_now_add=True)
    boolean = models.BooleanField(default=False)


class SimpleUuidPkModel(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class ModelWithForeignKeyField(models.Model):
    foreign_key_field = models.ForeignKey(SimpleUuidPkModel, on_delete=models.CASCADE)


class ModelWithManyToManyField(models.Model):
    many_to_many_field = models.ManyToManyField(SimpleUuidPkModel)
