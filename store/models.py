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

def get_keys_from_parent(items):
    """
    This function will return an array with key-value combinations that belong
    to the parent (indicated by last item) walking the tree backwards, adding
    any key's at that location.
    """
    return_kv = {}
    
    for item in reversed(items):
        parent = Parent.objects.get(name = item)
        kv_objs = KeyValue.objects.filter(parent_id = parent)
        
        for kv in kv_objs:
            return_kv[kv.key] = kv.value
            
    return return_kv
    
def get_keys_from_kv(items):
    """
    This function wil return a simple key-value pair of the requested item
    """
    
    return_kv = {}
    
    parent = Parent.objects.get(name = items[-2])
    kv_objs = KeyValue.objects.filter(parent_id = parent, key = items[-1])

    for kv in kv_objs:
        return_kv[kv.key] = kv.value 
    
    return return_kv
    
def parent_tree_valid(items):
    return True