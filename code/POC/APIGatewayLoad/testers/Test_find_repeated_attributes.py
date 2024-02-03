import unittest

import Service.EventBuildArango as eb

trace = [{"timeMillis":3,"message":"Choosing route between 1138 possible alternatives","data":null,"encryptContent":false},{"timeMillis":4,"message":"Found matching route: apiplatform.sensedia.com/sandbox/commerce/v1/carts/ => https://9ea47488-10da-4ef5-8cc9-b0bdd94906e2.mock.pstmn.io/carts (extraPath: /3456/itens)","data":null,"encryptContent":false},{"timeMillis":4,"message":"Destination to forward request: https://9ea47488-10da-4ef5-8cc9-b0bdd94906e2.mock.pstmn.io/carts/3456/itens (header 'Host': 9ea47488-10da-4ef5-8cc9-b0bdd94906e2.mock.pstmn.io)","data":null,"encryptContent":false},{"timeMillis":4,"message":"Executing API Interceptors","data":null,"encryptContent":false},{"timeMillis":4,"message":"Executing OAuth Interceptor","data":null,"encryptContent":false},{"timeMillis":5,"message":"Retrieved token: TokenInfo [type=App, code=319b7e7d3767c27a0c19d988d4f20001, status=APPROVED]","data":null,"encryptContent":false},{"timeMillis":20,"message":"Retrieved token: TokenInfo [type=AccessToken, code=dff9e58687dae9cf0426ff1a033b0891, status=ACTIVE]","data":null,"encryptContent":false},{"timeMillis":20,"message":"Executing Log Interceptor","data":null,"encryptContent":false},{"timeMillis":20,"message":"Request log","data":{"log":{"headers":"host: 9ea47488-10da-4ef5-8cc9-b0bdd94906e2.mock.pstmn.io\nclient_id: 319b7e7d3767c27a0c19d988d4f20001\naccess_token: dff9e58687dae9cf0426ff1a033b0891\ncontent-type: application/json\nuser-agent: PostmanRuntime/7.29.0\naccept: */*\ncache-control: no-cache\npostman-token: c7c47151-87f7-4ac6-b7e1-efd2e95fcaef\naccept-encoding: gzip, deflate, br\ncontent-length: 114\nx-forwarded-for: 54.86.50.139\nx-forwarded-proto: https\nx-envoy-external-address: 54.86.50.139\nx-request-id: 291e13b8-f77f-4b4a-9769-3d1a16417120","method":"POST","execution-point":"FIRST","body":"{\r\n    \"cart_id\" : 3456,\r\n    \"client\":  12345,\r\n    \"product_sku\" : 124,\r\n    \"quantity\" : 1,\r\n    \"origem\": 1\r\n}","url":"http://apiplatform.sensedia.com/sandbox/commerce/v1/carts/3456/itens"},"type":"LOG"},"encryptContent":false},{"timeMillis":20,"message":"Executing Log Interceptor","data":null,"encryptContent":false},{"timeMillis":20,"message":"Request log","data":{"log":{"headers":"host: 9ea47488-10da-4ef5-8cc9-b0bdd94906e2.mock.pstmn.io\nclient_id: 319b7e7d3767c27a0c19d988d4f20001\naccess_token: dff9e58687dae9cf0426ff1a033b0891\ncontent-type: application/json\nuser-agent: PostmanRuntime/7.29.0\naccept: */*\ncache-control: no-cache\npostman-token: c7c47151-87f7-4ac6-b7e1-efd2e95fcaef\naccept-encoding: gzip, deflate, br\ncontent-length: 114\nx-forwarded-for: 54.86.50.139\nx-forwarded-proto: https\nx-envoy-external-address: 54.86.50.139\nx-request-id: 291e13b8-f77f-4b4a-9769-3d1a16417120","method":"POST","execution-point":"FIRST","body":"{\r\n    \"cart_id\" : 3456,\r\n    \"client\":  12345,\r\n    \"product_sku\" : 124,\r\n    \"quantity\" : 1,\r\n    \"origem\": 1\r\n}","url":"http://apiplatform.sensedia.com/sandbox/commerce/v1/carts/3456/itens"},"type":"LOG"},"encryptContent":false},{"timeMillis":20,"message":"Forwarding request to 'https://9ea47488-10da-4ef5-8cc9-b0bdd94906e2.mock.pstmn.io/carts/3456/itens' with HTTP Timeout: socket: 10000 - connection: 10000","data":null,"encryptContent":false},{"timeMillis":803,"message":"Request forwarded successfully. Received http status: HTTP/1.1 200 OK , 450 bytes and 782 milliseconds.","data":null,"encryptContent":false},{"timeMillis":803,"message":"Executing API Interceptors","data":null,"encryptContent":false},{"timeMillis":803,"message":"Executing Log Interceptor","data":null,"encryptContent":false},{"timeMillis":805,"message":"Response log","data":{"log":{"headers":"date: Mon, 27 Jun 2022 11:55:26 GMT\ncontent-type: text/html; charset=utf-8\nconnection: keep-alive\nserver: nginx\nx-srv-trace: v=1;t=001857111b4d71ab\nx-srv-span: v=1;s=32b368965753ea13\naccess-control-allow-origin: *\nx-ratelimit-limit: 120\nx-ratelimit-remaining: 118\nx-ratelimit-reset: 1656330974\netag: W/\"1c2-R7RjN/TDtIcnfOSJYyhKwRIaNxI\"\nvary: Accept-Encoding","execution-point":"SECOND","body":"{\n    \"cart\": 3456,\n    \"orderDate\": \"2020-07-06T12:59:59.550-03:00\",\n    \"cliente\": {\n        \"codigo\": 12345,\n        \"name\": \"Carlos Pinheiro\",\n        \"document\": \"123456789-1\"\n    },    \n    \"products\": [\n        {\n            \"produto\" : \"Panela de Barro\",\n            \"sku\" : 123,\n            \"valor\": 99.99\n        }\n    ],\n    \"statusPedidos\": {\n        \"code\": 1,\n        \"description\": \"waiting payment\"\n    },\n    \"origem\": \"e-commerce\"\n}","status":200},"type":"LOG"},"encryptContent":false},{"timeMillis":805,"message":"Executing Log Interceptor","data":null,"encryptContent":false},{"timeMillis":805,"message":"Response log","data":{"log":{"headers":"date: Mon, 27 Jun 2022 11:55:26 GMT\ncontent-type: text/html; charset=utf-8\nconnection: keep-alive\nserver: nginx\nx-srv-trace: v=1;t=001857111b4d71ab\nx-srv-span: v=1;s=32b368965753ea13\naccess-control-allow-origin: *\nx-ratelimit-limit: 120\nx-ratelimit-remaining: 118\nx-ratelimit-reset: 1656330974\netag: W/\"1c2-R7RjN/TDtIcnfOSJYyhKwRIaNxI\"\nvary: Accept-Encoding","execution-point":"SECOND","body":"{\n    \"cart\": 3456,\n    \"orderDate\": \"2020-07-06T12:59:59.550-03:00\",\n    \"cliente\": {\n        \"codigo\": 12345,\n        \"name\": \"Carlos Pinheiro\",\n        \"document\": \"123456789-1\"\n    },    \n    \"products\": [\n        {\n            \"produto\" : \"Panela de Barro\",\n            \"sku\" : 123,\n            \"valor\": 99.99\n        }\n    ],\n    \"statusPedidos\": {\n        \"code\": 1,\n        \"description\": \"waiting payment\"\n    },\n    \"origem\": \"e-commerce\"\n}","status":200},"type":"LOG"},"encryptContent":false},{"timeMillis":805,"message":"Returning response to client","data":null,"encryptContent":false},{"timeMillis":806,"message":"Saving trace","data":null,"encryptContent":false}]


class Test_correlation_repeated_attributes():

    a = eb.get_api_destination_in_trace(trace)
    print(str(a))

if __name__ == '__main__':
    Test_correlation_repeated_attributes()
