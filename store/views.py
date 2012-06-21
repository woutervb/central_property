from django.http import HttpResponse, Http404, HttpResponseServerError

from models import Tree, KeyValue, get_keys_from_tree

import simplejson as json
import yaml
import re
from StringIO import StringIO


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
  
    data = None
    if yaml_match.search(encoded_request):
        data = yaml_load(body)
    elif json_match.search(encoded_request):
        data = json_load(body)
    else:
        return HttpResponseServerError("Unsupported format specified")
    
    if data == None:
        return HttpResponseServerError("Data could not be decoded")
    
    # If we land here, then we can assume that we have a dictionary called data
    # Which we need to add to the given item
    
    # We know that the uri is / divided. The last one is either an
    # Group identifier or an Key
        
    items = object_ref.split('/')
        
    pos = 0
    previous = None
    while pos < len(items):
        try:
            obj = Tree.objects.get(name = items[pos])
        except Tree.DoesNotExist:
            if pos == 0:
                obj = Tree.add_root(name = items[pos])
            else:
                obj = previous.add_child(name = items[pos])
        pos = pos + 1          
        previous = obj
        
            
    try:
        tree = Tree.objects.get(name = items[-1])
    except Tree.DoesNotExist:
        return HttpResponseServerError("Referenced tree could not be found")
    
    
    for k, v in data.iteritems():
        kv_object = None
        new_object = False
        try:
            kv_object = KeyValue.objects.get(key = k, tree_id = tree)
        except KeyValue.DoesNotExist:
            kv_object = KeyValue()
            new_object = True

        kv_object.key = k
        kv_object.value = v
        kv_object.save()
        if new_object:
            kv_object.tree_id.add(tree)
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

def store_get(request, object_ref):
    """
    This function will check the request that came in.
    If the object_ref matches only one of the 'tree' elements, then we will throw the data of
    all key-value pairs at that level. If a specific key is requested we will only return
    the key-value pair of that item.
    """
    
    # We know that the uri is / divided. The last one is either an
    # Group identifier or an Key
    items = object_ref.split('/')

    # A temporary variable to store the tree object
    tree_obj = None
    result_obj = None
    for item in items:
        # Are we at the first item?
        if item == items[0]:
            try:
                # this root object should exist
                tree_obj = Tree.objects.get(name = item)
                result_obj = tree_obj
            except Tree.DoesNotExist:
                # The tree does not exist
                raise Http404
        else:
            try:
                objs = Tree.objects.filter(name = item)
            except Tree.DoesNotExist:
                result_obj = tree_obj
                continue
            
            for obj in objs:
                if obj.is_child_of(tree_obj):
                    tree_obj = obj
                    result_obj = obj
                    
    try:
        kv = get_keys_from_tree(result_obj)
    except:
        return HttpResponseServerError('Unable to retrieve key-value information')

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

def make_response(request, data):
    """
    This function is supposed to create some output based on the requested data.
    So based on the accept-encoding we output: json, yaml etc.
    """
    
    encoding_request = request.META['HTTP_ACCEPT']
    yaml_match = re.compile(r'yaml', re.IGNORECASE)
    json_match = re.compile(r'json', re.IGNORECASE)
    
    output = None
    
    if yaml_match.search(encoding_request):
        output = yaml_dump(data)
    elif json_match.search(encoding_request):
        output = json_dump(data)
    else:
        raise Http404

    return output
