# Introduction
This project has as a goal to provide a service to store at a central place 
key-value pairs, that can be used by loosely connected, but related servers.

These servers will have some kind of hierarchy, which can be administered in 
the tool. This means that elements that are the same for multiple servers 
only have to be defined once.

The remote servers will obtain acces by using a rest interface. Modifications 
can be made either via a web interface.

The rest interface will support multiple output formats e.g. Yaml, json

# Framework
The whole service will be developed using the [Django] framework. This will 
give the most flexibility as it will handle a lot of webapp related setup. 
(And Python is a lot of fun ;) )

# Example
The tool works best if an reverse dns tree is used as hierarchie. Using such
an setup means that it becomes simple to support puppet, as nodes will be 
passed via the hiera plugin as a fqdn of the host.
If we have an hierarchical store like the example below:

    nl
      key0 - value0
      vanbommelonline
        key1 - value1
      sidn
        key2 - value2
        
* A get call to http://<_hostname_>/nl will retrieve **key0 - value0**
* A get call to http://<_hostname_>/nl/vanbommelonline will retrieve 
**key0 - value0** and **key1 - value1**
* A get call to http://<_hostname_>/nl/sidn will retrieve 
**key0 - value0** and **key2 - value2**
* A get call to http://<_hostname_>/nl/key2 will retrieve nothing

Remember that key0, key1 and key2 in the above example have to be unique!. But
it is possible to connect an key-value pair to multiple locations in the
hierarchy

Extending the above example with www gives the following options


    nl
      key0 - value0
      vanbommelonline
        key1 - value1
        www
          key0 - value0
      sidn
        key2 - value2

Now requesting key0 (or all key's) from www will only return the value as 
specified by this child! So it is possible to set global settings while 
overriding them locally.
The webinterface will make this clear.

# Example curl usage
One easy way to test this, is by using curl. The following example(s) can be 
used to query the data. The below example can be copy and pasted to a console 
when an instance is running and curl is available.

Add the example manually using the webinterface, and then execute the 
commands below on the commandline.
  
    # And retrieve this data
    curl -v --header "Accept: application/json" \
     http://localhost:8000/store/nl/vanbommelonline
    curl -v --header "Accept: application/yaml" \
     http://localhost:8000/store/nl/vanbommelonline

# Puppet integration
This project is combined with a hiera compatible backend. This backend which
will allow intergration between puppet and central_property can be found
on github [https://github.com/woutervb/hiera-central_property].

To use the puppet integration it is required that the full fqdn (reversed)
hierachy is used (up to the point that is required for host specific
definitions)

# License
This project is licensed under [GPLv2].

[Django]: https://www.djangoproject.com 
[GPLv2]: http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
[https://github.com/woutervb/hiera-central_property]: 
https://github.com/woutervb/hiera-central_property