from django.db import models
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField

# Create your models here.
class Parent(models.Model):
    """
    The Parent class identifies the parent, if any an object belongs to.
    If parent_id attribute is not set or Null it there is no successor
    """
    parent_id = models.ForeignKey('self')
    description = models.CharField(max_length=255)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

class KeyValue(models.Model):
    """
    This class is used to store simple key-value pairs.
    We limit the size of a value to 4k, an key can be a maximum of 255 chars.
    The assumption is made that we only with to store data encoded as a character.
    """
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=4096)
    parent_id = models.ManyToManyField(Parent)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

