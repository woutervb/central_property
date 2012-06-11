from django.http import HttpResponse
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
    return HttpResponse("You called met with argument '%s'" % object_ref)
