
ignore_field_name = [
    "_score",
    "_ignored",
    "_index",
    "@version",
    "authenticated_entity",  
    "accept",    
    "access-control-allow-origin",      
    "balancer_latency",
    "balancer_latency_ns",
    "cache-control"    
    "content-length",
    "content-type",
    "connection",    
    "enabled",
    "etag",
    "https_redirect_status_code",
    "kong",
    "kong_internal",
    "latencies",    
    "port",
    "protocol",
    "protocols",    
    "proxy",    
    "path_handling",
    "pragma",
    "preserve_host",    
    "retries",
    "read_timeout",
    "request_buffering",
    "response_buffering",    
    "regex_priority",    
    "tries",    
    "server",
    "size",
    "strip_path",    
    "user-agent",    
    "vary",       
    "version",   
    "via",     
    "x-kong-proxy-latency",
    "x-kong-response-latency",
    "x-kong-upstream-latency",    
    "x-ratelimit-remaining", 
    "x-srv-span-id",
    "x-ratelimit-limit",
    "x-srv-trace",
    "x-ratelimit-reset",   
    "write_timeout",     
    "ws_id",
    ['_ignored', '0'],
    ['_source', 'latencies'],
    ['_source', 'request', 'headers', 'accept'],  
    ['_source', 'request', 'headers', 'accept-encoding'],  
    ['_source', 'request', 'headers', 'authorization'],      
    ['_source', 'request', 'headers', 'cache-control'],  
    ['_source', 'request', 'headers', 'connection'],     
    ['_source', 'request', 'headers', 'content-length'],  
    ['_source', 'request', 'headers', 'content-type'],  
    ['_source', 'request', 'headers', 'user-agent'],  
    ['_source', 'request', 'headers', 'postman-token'],  
    ['_source', 'request', 'size'],  
    ['_source', 'response', 'headers', 'access-control-allow-origin'],
    ['_source', 'response', 'headers', 'connection'],    
    ['_source', 'response', 'headers', 'content-length'],    
    ['_source', 'response', 'headers', 'content-type'], 
    ['_source', 'response', 'headers', 'etag'], 
    ['_source', 'response', 'headers', 'vary'], 
    ['_source', 'response', 'headers', 'via'], 
    ['_source', 'response', 'headers', 'x-kong-upstream-latency'],   
    ['_source', 'response', 'headers', 'x-kong-proxy-latency'],    
    ['_source', 'response', 'headers', 'x-ratelimit-limit'],
    ['_source', 'response', 'headers', 'x-ratelimit-remaining'],    
    ['_source', 'response', 'headers', 'x-ratelimit-reset'],  
    ['_source', 'response', 'headers', 'x-srv-span'], 
    ['_source', 'response', 'headers', 'x-srv-trace'], 
    ['_source', 'response', 'size'],
    ['_source', 'route', 'https_redirect_status_code'],     
    ['_source', 'route', 'methods'],         
    ['_source', 'route', 'path_handling'],     
    ['_source', 'route', 'protocols'],         
    ['_source', 'route', 'request_buffering'], 
    ['_source', 'route', 'response_buffering'],      
    ['_source', 'route', 'strip_path'],     
    ['_source', 'route', 'ws_id'],      
    ['_source', 'service', 'enabled'],        
    ['_source', 'service', 'write_timeout'],      
    ['_source', 'service', 'port'],  
    ['_source', 'service', 'read_timeout'],  
    ['_source', 'service', 'retries'],  
    ['_source', 'service', 'ws_id'],  
    ['_source', '@version'],  
    ['_source', 'tags'],    
    ['_source', 'tries'],    
    "read_timeout"
]


def field_to_ignore(field_name: str) -> bool:
    try:
        ret = ignore_field_name.count(field_name)
        if ret > 0:
            return True
        else:
            return False
    except ValueError:
        return False
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))


def check_ignored_key_existence(dictionary, keys):
    try:
        # Iterate through each key in the list of keys
        for key in keys:
            # Access the value associated with the current key
            dictionary = dictionary[key]
        # If all keys are successfully accessed, return True
        return True
    except (KeyError, TypeError):
        # If any key is not found or if a non-dict type is encountered, return False
        return False