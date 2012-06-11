from django.db import models
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from treebeard.mp_tree import MP_Node

# Create your models here.
class Parent(MP_Node):
    name = models.CharField(max_length=255)
    
    node_order_by = ['name']
    def __unicode__(self):
        return 'Name: %s' % self.name
    
    # These lines below are basic modification fields for an audit trail
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

