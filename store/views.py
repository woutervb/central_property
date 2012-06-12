from django.http import HttpResponse, Http404, HttpResponseServerError
from models import Parent, KeyValue, get_keys_from_parent, get_keys_from_kv, parent_tree_valid
import logging
import simplejson as json
import yaml
import re
from elementtree.SimpleXMLWriter import XMLWriter
from StringIO import StringIO

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
       
    if parent_obj:
        if not parent_tree_valid(items):
            raise Http404
        kv = get_keys_from_parent(items)
    elif result_set:
        # Only check the parent part(s), as we will check that the parent really exist
        # When fetching the real key value combination
        if not parent_tree_valid(items[:-1]):
            raise Http404
        kv = get_keys_from_kv(items)
    else:
        return HttpResponseServerError('Unexpected situation. Neither parents or key-value pairs match last operand')

    return make_response(request, kv)    

def yaml_dump(data):
    """
    This function is used to properly parse the data, so that we have (non unicode) output
    """
    
    # Helper dictionary
    data2 = {}
    
    # First remove all our uniode coding, we reencode to 'ascii'
    for k, v in data.iteritems():
        data2[k.encode('ascii', 'ignore')] = v.encode('ascii', 'ignore')
        
    return HttpResponse(yaml.dump(data2, 
                                  explicit_start=True, 
                                  explicit_end=True, 
                                  default_flow_style=False, 
                                  allow_unicode=False, 
                                  indent=4 * ' '),
                        content_type='text/yaml')

def json_dump(data):
    """
    This function is a simple wrapper, so that we have some nice json output
    """
    return HttpResponse(json.dumps(data, sort_keys=True, indent=4 * ' '),
                        content_type='text/json')

def xml_dump(data):
    stream = StringIO()
    xml = XMLWriter(stream)
    xml.start("datafields")
    for k, v in data.iteritems():
        xml.element("dataelement", name=k, value=v)
    xml.end("datafields")
    
    return_string = stream.getvalue()
    stream.close()
    return HttpResponse(return_string, content_type='text/xml')

def make_response(request, data):
    """
    This function is supposed to create some output based on the requested data.
    So based on the accept-encoding we output: xml, json, yaml etc.
    """
    
    encoding_request = request.META['HTTP_ACCEPT']
    yaml_match = re.compile(r'yaml', re.IGNORECASE)
    json_match = re.compile(r'json', re.IGNORECASE)
    xml_match = re.compile(r'xml', re.IGNORECASE)
    
    output = None
    
    if yaml_match.search(encoding_request):
        output = yaml_dump(data)
    elif json_match.search(encoding_request):
        output = json_dump(data)
    elif xml_match.search(encoding_request):
        output = xml_dump(data)
    else:
        raise Http404

    return output