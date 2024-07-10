import re

def split_url(url):
    """
        Get the server, environment, API and version from the URL, considering the patters:
            "http://address:port/enviroment/api/version"
            if the environment is not present, the pattern is: "http://address:port/api/version"
            Sometimes the environment is reflect in server address, so the pattern is the seme as "http://address:port/api/version"
            It considers the semantic versioning pattern for APIs, like "v1", "v2", "v3", etc. in the url.
    """
    try:    
        parts = url.split('/')
        server = '/'.join(parts[:3])
        environment = None
        version = None
        api = None
        
        # pattern: "/api/version", case declared in swagger without server address
        if re.match(r'v\d+', parts[2]):
            version = parts[2]
            api = parts[1]
            environment = None
            server = None 
        # pattern: "http://address:port/api/version"            
        elif re.match(r'v\d+', parts[4]):
            version = parts[4]
            api = parts[3]
            environment = None
            server = f"{parts[0]}//{parts[2]}"         
        # pattern: "http://address:port/enviroment/api/version"
        elif re.match(r'v\d+', parts[5]):
            version = parts[5]
            api = parts[4]
            environment = parts[3]
            server = f"{parts[0]}//{parts[2]}" 

        return {
            'server': server,
            'environment': environment,
            'API': api,
            'version': version
        }
    except Exception as error:   
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print(f"In split_url(url) module :", __name__)
        raise error       
    
def get_server(url):
    return split_url(url)['server']

def get_environment(url):
    return split_url(url)['environment']

def get_api(url):
    return split_url(url)['API']

def get_version(url):
    return split_url(url)['version']    


def split_resource_subresources(resource_name):
    """
        split a resource name in resource and subresources
        separated by '/' in the path
        and identify the id in resource and subresources if exists
        return a dictionary with the resource name and the id if exists and the subresources with id if exists

    """
    parts = resource_name.split('/')
    resource = parts[0]
    if len(parts) > 1:
        resource_id = parts[1]
    if len(parts) > 2:
        subresource = parts[2]
    if len(parts) > 3:
        resource_id = parts[3]
    if len(parts) > 4:
        subresource_l2 = parts[4]
    if len(parts) > 5:
        resource_l2_id = parts[5:]        

    return {
        'resource': resource,
        'resource_id': resource_id,
        'subresource': subresource,
        'subresource_id': resource_id,
        'subresource_l2': subresource_l2,
        'resource_l2_id': resource_l2_id        
    }
    
    
def get_last_resource_name(resource_name):
    """
        Get the last resource in the path. The last part can´t be an number, it is considered an id
        example: 'carts/123/items/456/' -> items
        example: 'carts/123/items/456' -> items
        example: 'carts/123/items'  - > items
        example: 'carts/123'        -> carts
        example: 'carts'            -> carts
    """
    resource_name = resource_name.rstrip('/')
    parts = resource_name.split('/')   
    # Filter parts to keep every other element starting from the first    
    parts = [part for i, part in enumerate(parts) if i % 2 == 0]   
    # Iterate in reverse to find the last part that is not a number
    for part in reversed(parts):
        if not part.isdigit():  # Check if the part is not a digit
            return part
    # If all parts are numbers or the list is empty, return an empty string or a default value
    return "no-name"    
    
