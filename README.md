# Introduction
This project has as a goal to provide a service to store at a central place key-value pairs, that can be used by loosely connected, but related servers.

These servers will have some kind of hierarchy, which can be administered in the tool. This means that elements that are the same for multiple servers only have to be defined once.

The remote servers will obtain acces by using a rest interface. Modifications can be made either via a web interface or via a rest interface.

The rest interface will support multiple output formats e.g. Yaml, JSON

# Framework
The whole service will be developed using the [Django] framework. This will give the most flexibility as it will handle a lot of webapp related setup. (And Python is a lot of fun ;) )

# Example
If we have an hierarchical store like the example below:

    root
      key0 - value0
      child
        key1 - value1
      child2
        key2 - value2
        
* A get call to http://<_hostname_>/root will retrieve **key0 - value0**
* A get call to http://<_hostname_>/root/child1 will retrieve **key0 - value0** and **key1 - value1**
* A get call to http://<_hostname_>/root/child2 will retrieve **key0 - value0** and **key2 - value2**
* A get call to http://<_hostname_>/root/child2/key2 will retrieve **key2 - value2**
* A get call to http://<_hostname_>/root/key2 will retrieve nothing
* A get call to http://<_hostname_>/root/key0 will retrieve **key0 - value0**

Remember that key0, key1 and key2 in the above example don't have to be unique!

Extending the above example with child3 gives the following options


    root
      key0 - value0
      child1
        key1 - value1
        child3
          key0 - value0
      child2
        key2 - value2

Now requesting key0 (or all key's) from child3 will only return the value as specified by this child! So it is possible to set global settings while overriding them locally.
The webinterface will make this clear (even as comments in the responses, if permitted by the response format)

# Example curl usage
One easy way to test this, is by using curl. The following example(s) can be used to query the data. The below example can be copy and pasted to a console when an instance is running and curl is available.

	# Put some data in the database, when running locally using runserver
	curl -v --header "Accept: application/json" --header "Content-Type: text/json" --data "{ \"sample_key\" : \"Data for the sample_key\" }" http://localhost:8000/store/root/child1
    # And retrieve this data
    curl -v --header "Accept: application/json" http://localhost:8000/store/root/child1
    curl -v --header "Accept: application/yaml" http://localhost:8000/store/root/child1

# Puppet integration
One of the reasons to start this project is to have a 'central' location where key-value pairs can be defined which can be used in other project.
For puppet integration a 'hiera-foreman' compatibel interface has been created. More information about this plugin can be found here: [https://github.com/torrancew/hiera-foreman]

# License
This project is licensed under [GPLv2].

[Django]: https://www.djangoproject.com 
[GPLv2]: http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
[https://github.com/torrancew/hiera-foreman]: https://github.com/torrancew/hiera-foreman