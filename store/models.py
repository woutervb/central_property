from django.db import models, IntegrityError
from django_extensions.db.fields import ModificationDateTimeField, CreationDateTimeField
from treebeard.mp_tree import MP_Node

# Create your models here.
class Tree(MP_Node):
    name = models.CharField(max_length=255)
    
    node_order_by = ['name']
    def __unicode__(self):
        return '%s' % self.name
    
    def save(self, *args, **kwargs):
        # Override the default save, so that we can ensure that root objects are unique
        all_roots = self.get_root_nodes()
#        if (self in all_roots) and (len(all_roots) > 1):
        cnt = 0
        for item in all_roots:
            if item.name == self.name:
                cnt = cnt + 1
        if cnt > 1:
            raise IntegrityError("Non unique root key")
        super(Tree, self).save(*args, **kwargs)
    
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
    tree_id = models.ManyToManyField(Tree)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    
    def __unicode__(self):
        return self.key + ' -> ' + self.value
    
    def save(self, *args, **kwargs):
        # Override the default save to ensure that key, value combination is uniq
        results = KeyValue.objects.filter(key = self.key)
        cnt = 0
        for res in results:
            if (res.value == self.value) and (res != self):
                cnt = cnt + 1
        if cnt > 0:        
            raise IntegrityError("Non unique key/value combination")
        
        super(KeyValue, self).save(*args, **kwargs)
        
def get_keys_from_tree(obj):
    """
    This function will return an array with key-value combinations that belong
    to the tree (indicated by last item) walking the tree backwards, adding
    any key's at that location.
    """
    return_kv = {}
    
    # By iterating from the lowest level to a higher level we will overwrite any
    # settings with the same key at a higher level
    at_root = False
    while not at_root:
        at_root = obj.is_root()
        kv_objs = KeyValue.objects.filter(tree_id = obj)
        obj = obj.get_parent()
        
        for kv in kv_objs:
            if kv.key not in return_kv:
                return_kv[kv.key] = kv.value
            
    return return_kv
        
