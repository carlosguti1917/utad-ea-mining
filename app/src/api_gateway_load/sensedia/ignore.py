
ignore_field_name = [
    "revisionId",
    "sensedia.access_token",
    "sensedia.access_token_owner",
    "sensedia.api.component_type",
    "sensedia.app.developer",
    "sensedia.api.id",
    "sensedia.billing",
    "sensedia.cached_response",
    "sensedia.duration_millis",
    "sensedia.environment.id",
    "sensedia.gateway_duration_millis",
    "sensedia.product.name",
    "sensedia.response.type_status",
    "sensedia.revision.id",
    "sensedia.target_duration_millis",
    "sensedia.target_result_status",
    "sensedia.tenant.id",
    "service.name",
    "net.sock.host.addr",
    "_index",
    "_score",
    "_size",    
    "_version",
    "apiComponentType",
    "resourceId",
    "billing",
    "billingData",
    "cache",
    "duration",
    "durationMillis",
    "environmentId",
    "environmentName",
    "apiId",
    "completeUrl",
    "yearMonth",
    "gatewayDurationMillis",
    "transactionID",
    "requestID",
    "targetResultStatus",
    "targetDurationMillis",
    "callDate",
    "duration",
    "redis",
    ['_source', 'duration'],
    ['_source', 'status'],    
    ['_source', 'sensedia.operation.id'],
    ['_source', 'http.request.headers', "content-type"],
    ['_source', 'http.request.headers', "authorization"],
    ['_source', 'http.request.headers', "accept"],
    ['_source', 'http.request.headers', "accept-encoding"],
    ['_source', 'http.request.headers', "cache-control"],
    ['_source', 'http.request.headers', "content-length"],
    ['_source', 'http.request.headers', "connection"],
    ['_source', 'http.request.headers', "host"],
    ['_source', 'http.request.headers', "pragma"],
    ['_source', 'http.request.headers', "referer"],
    ['_source', 'http.request.headers', "upgrade-insecure-requests"],
    ['_source', 'http.request.headers', "user-agent"],        
    ['_source', 'http.request.headers', "x-forwarded-for"],
    ['_source', 'http.request.headers', "x-forwarded-proto"],
    ['_source', 'http.request.headers', "x-real-ip"],
    ['_source', 'http.request.headers', "x-request-id"],
    ['_source', 'http.response.headers', "access-control-allow-origin"],    
    ['_source', 'http.response.headers', "content-type"],
    ['_source', 'http.response.headers', "connection"],
    ['_source', 'http.response.headers', "content-length"],
    ['_source', 'http.response.headers', "date"],
    ['_source', 'http.response.headers', "etag"],    
    ['_source', 'http.response.headers', "server"],
    ['_source', 'http.response.headers', "vary"],
    ['_source', 'http.response.headers', "x-content-type-options"],
    ['_source', 'http.response.headers', "x-frame-options"],
    ['_source', 'http.response.headers', "x-xss-protection"],
    ['_source', 'http.response.headers', "x-ratelimit-limit"],
    ['_source', 'http.response.headers', "x-ratelimit-remaining"],
    ['_source', 'http.response.headers', "x-ratelimit-reset"],
    ['_source', 'http.response.headers', "x-ratelimit-reset-remaining"],
    ['_source', 'http.response.headers', "x-ratelimit-reset-time"],
    ['_source', 'http.response.headers', "x-ratelimit-reset-time-remaining"],
    ['_source', 'http.response.headers', "x-ratelimit-reset-time-remaining-ms"],
    ['_source', 'http.response.headers', "x-ratelimit-reset-time-ms"],
    ['_source', 'http.response.headers', "x-srv-trace"],
    ['_source', 'http.response.headers', "x-srv-span"],
    ['_source', 'trace_id'],

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


