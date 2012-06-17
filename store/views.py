from django.http import HttpResponse, Http404, HttpResponseServerError
from django.template import Context, loader
from models import Parent, KeyValue, get_keys_from_parent, get_keys_from_kv, parent_tree_valid
import simplejson as json
import yaml
import re
from elementtree.SimpleXMLWriter import XMLWriter
from StringIO import StringIO


def index(request):
    t = loader.get_template('store/index.html')
    c = Context()
    return HttpResponse(t.render(c))

def store(request, object_ref):
    """
    This function will check the incoming request.
    If it is an get, we will continue with looking in the database to retrieve the data
    If it is an post, we will update the database.
    """    
    if request.method == 'GET':
        return store_get(request, object_ref)
    elif request.method == 'POST':
        return store_post(request, object_ref)
    else:
        return HttpResponseServerError("Only GET and POST requests are supported")

def store_post(request, object_ref):
    """
    This function is intended to accept the presented data (if possible)
    and update the database accordingly
    """
    body = request.body
    encoded_request = request.META['CONTENT_TYPE']
    yaml_match = re.compile(r'yaml', re.IGNORECASE)
    json_match = re.compile(r'json', re.IGNORECASE)
    xml_match = re.compile(r'xml', re.IGNORECASE)
  
    data = None
    if yaml_match.search(encoded_request):
        data = yaml_load(body)
    elif json_match.search(encoded_request):
        data = json_load(body)
    elif xml_match.search(encoded_request):
        data = xml_load(body)
    else:
        return HttpResponseServerError("Unsupported format specified")
    
    if data == None:
        return HttpResponseServerError("Data could not be decoded")
    
    # If we land here, then we can assume that we have a dictionary called data
    # Which we need to add to the given item
    
    # We know that the uri is / divided. The last one is either an
    # Group identifier or an Key
        
    items = object_ref.split('/')
    # TODO: build parent properly
    
    # BUG: names now have to be unique in order to work, else tree mixup will happen
    
    pos = 0
    previous = None
    while pos < len(items):
        try:
            obj = Parent.objects.get(name = items[pos])
        except Parent.DoesNotExist:
            if pos == 0:
                obj = Parent.add_root(name = items[pos])
            else:
                obj = previous.add_child(name = items[pos])
        pos = pos + 1          
        previous = obj
        
            
    try:
        parent = Parent.objects.get(name = items[-1])
    except Parent.DoesNotExist:
        return HttpResponseServerError("Referenced parent could not be found")
    
    
    for k, v in data.iteritems():
        kv_object = None
        new_object = False
        try:
            kv_object = KeyValue.objects.get(key = k, parent_id = parent)
        except KeyValue.DoesNotExist:
            kv_object = KeyValue()
            new_object = True

        kv_object.key = k
        kv_object.value = v
        kv_object.save()
        if new_object:
            kv_object.parent_id.add(parent)
            kv_object.save()
        
    return make_response(request, { 'result' : 'ok'})

def yaml_load(data):
    """
    This function will attempt to decode the given yaml input
    and return a dictionary with key-value pairs
    """
    pass

def json_load(data):
    """
    This function will attempt to decode the given json input
    and return a dictionary with key-value pairs
    """
    decoded = None
    try:
        decoded = json.loads(data)
    except:
        # If decoding fails, then let the called handle this. We know that the caller
        # will fail if None is returned as an object
        pass
    
    if type(decoded) == type(dict()):
        return decoded
    else:
        return None

def xml_load(data):
    """
    This function will attempt to decode the given xml input
    and return a dictionary with key-value pairs
    """
    pass

def store_get(request, object_ref):
    """
    This function will check the request that came in.
    If the object_ref matches only one of the 'parent' elements, then we will throw the data of
    all key-value pairs at that level. If a specific key is requested we will only return
    the key-value pair of that item.
    """
    
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