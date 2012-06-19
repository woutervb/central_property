from django.db import models, IntegrityError
from django.contrib import admin
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from treebeard.mp_tree import MP_Node
from treebeard.admin import TreeAdmin

# Create your models here.
class Parent(MP_Node):
    name = models.CharField(max_length=255)
    
    node_order_by = ['name']
    def __unicode__(self):
        return '%s' % self.name
    
    def save(self, *args, **kwargs):
        # Override the default save, so that we can ensure that root objects are unique
        all_roots = self.get_root_nodes()
        if (self in all_roots) and (len(all_roots) > 1):
            raise IntegrityError
        
        super(Parent, self).save(*args, **kwargs)
    
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
    
    def __unicode__(self):
        return self.key + ' -> ' + self.value
  
class KeyValueAdmin(admin.ModelAdmin):
    fields = (('key', 'value'),)

class KeyValueInline(admin.StackedInline):
    model = KeyValue.parent_id.through
    extra = 3

class ParentAdmin(TreeAdmin):
    inlines = [KeyValueInline]
    
def get_keys_from_parent(obj):
    """
    This function will return an array with key-value combinations that belong
    to the parent (indicated by last item) walking the tree backwards, adding
    any key's at that location.
    """
    return_kv = {}
    
    # By iterating from the lowest level to a higher level we will overwrite any
    # settings with the same key at a higher level
    at_root = False
    while not at_root:
        at_root = obj.is_root()
        kv_objs = KeyValue.objects.filter(parent_id = obj)
        obj = obj.get_parent()
        
        for kv in kv_objs:
            if kv.key not in return_kv:
                return_kv[kv.key] = kv.value
            
    return return_kv
        
