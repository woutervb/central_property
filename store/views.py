from django.http import HttpResponse, Http404
from models import Parent, KeyValue
from treebeard.mp_tree import MP_NodeQuerySet
import logging

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("Hello, world. You're at the store.")

def store(request, object_ref):
    """
    This function will check the request that came in.
    If the object_ref matches only one of the 'parent' elements, then we will throw the data of
    all key-value pairs at that level. If a specific key is requested we will only return
    the key-value pair of that item.
    """
    logger.debug("Store views.store with arguments '%s'" % object_ref)
    
    # We know that the uri is / divided. The last one is either an
    # Group identifier or an Key
    items = object_ref.split('/')
    
    #check if the last item is a key or an object
    try:
        obj = Parent.objects.get(name = items[-1])
    except Parent.DoesNotExist:
        # If parent does not have the name of the item a key might exist
        try:
            obj = KeyValue.objects.filter(key__exact = items[-1])
        except KeyValue.DoesNotExist:
            # Neither a Group or Key does exist with the name
            raise Http404
    
    str = u''
    for objs in obj:
        str = str + obj.key + ' => ' + obj.value + ','
            
    return HttpResponse("You called met with argument '%s'" % str)
