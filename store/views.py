from django.http import HttpResponse, Http404, HttpResponseServerError
from models import Parent, KeyValue, get_keys_from_parent, get_keys_from_kv, parent_tree_valid
import logging
import simplejson as json

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
    parent_obj = None
    result_set = None
    try:
        parent_obj = Parent.objects.get(name = items[-1])
    except Parent.DoesNotExist:
        # If parent does not have the name of the item a key might exist
        try:
            result_set = KeyValue.objects.filter(key__exact = items[-1])
        except KeyValue.DoesNotExist:
            # Neither a Group or Key does exist with the name
            raise Http404
    
    if not parent_tree_valid(items):
        raise Http404
    
    if parent_obj:
        kv = get_keys_from_parent(items)
    elif result_set:
        kv = get_keys_from_kv(items)
    else:
        return HttpResponseServerError('Unexpected situation. Neither parents or key-value pairs match last operand')

    return make_response(request, kv)    
    
def make_response(request, data):
    """
    This function is supposed to create some output based on the requested data.
    So based on the accept-encoding we output: xml, json, yaml etc.
    """
    
    # some dirty hack we only ouput json at the moment
    output = json.dumps(data, sort_keys=True, indent=4 * ' ')
    return HttpResponse(output)