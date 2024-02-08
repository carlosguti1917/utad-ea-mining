
ignore_field_name = [
    "revisionId",
    "Index",
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
    "responsePayload",
    "requestPayload",
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
    "responseHeaders",
    "baseUrl",
    "httpStatus"
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


