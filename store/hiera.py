from django.http import HttpResponse, Http404, HttpResponseServerError
from views import get_response_from_items

def hiera(request, object_ref):
    items = object_ref.split('.')
    items.reverse()
    
    return get_response_from_items(request, items)
    