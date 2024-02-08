from pprint import pprint

import requests
import json
from json import JSONDecodeError


def trace_parser() -> list:
    """Intera sobre todas as chamadas da API e returna uma lista com as informações dos "cartid", "cliente" ou "dataPedido" """
    calls_url = "https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls"
    id_call_url = "https://manager-apiplatform.sensedia.com/api-manager/api/v3/calls/"
    sesssion = requests.session()
    sesssion.headers.update()

    my_headers = {
        "Content-Type": "application/json",
        "Sensedia-Auth": "306ae5fd-c4dc-3592-b12c-2b3f9a6e0e22",
    }

    req = requests.get(calls_url, headers=my_headers)

    response = req.json()
    calls = response["calls"]

    expected_info = []

    for call in calls:
        id_da_call = call["id"]
        req_call = requests.get(id_call_url + id_da_call, headers=my_headers)
        chamadas_especificas_por_id = req_call.json()
        traces = chamadas_especificas_por_id["trace"]
        parsed_traces = json.loads(traces)
        for trace_log in parsed_traces:
            if trace_log["message"] == "Response log":
                try:
                    logs_body = json.loads(trace_log["data"]["log"]["body"])
                    if isinstance(logs_body, list):
                        for log_body in logs_body:
                            aux = expected_response_parser(log_body)
                            if len(aux) > 0:
                                expected_info.append(aux)
                    else:
                        aux = expected_response_parser(logs_body)
                        if len(aux) > 0:
                            expected_info.append(aux)
                except JSONDecodeError as excinfo:
                    print(f"Não foi possivel converter para json: {trace_log} | {excinfo}")
                    pass

    return expected_info


def expected_response_parser(body_log: dict) -> dict:
    """Pega as infomações do "cartid", "cliente" ou "dataPedido" e retorna um dict

    Attributes:
        body_log: dict do body do log do trace
        example: {
            "numPedido": 1001,
            "dataPedido": "2021-08-06T12:59:59.550-03:00",
            "codigo": 12345,
            "statusPedidos": "APROVADO",
            "origem": "App IOS",
            "cart": {
                "cartid": 3456,
                "cliente": 12345,
                "itens": [
                    {"sku": 12, "produto": "Produto 1", "valor": 99.99},
                    {"sku": 34, "produto": "Produto 2", "valor": 199.99},
                    {"sku": 35, "produto": "Produto 2", "valor": 299.99},
                ],
            },
        }
    Returns: dict com as informações "cartid", "cliente" ou "dataPedido"
        example:
        {'numPedido': 1001, 'cartid': 3456, 'cliente': 12345}
    """
    if body_log.get("numPedido"):
        aux = {
            "numPedido": body_log.get("numPedido"),
        }
        if body_log.get("cart"):
            aux["cartid"] = body_log["cart"].get("cartid")
            aux["cliente"] = body_log["cart"].get("cliente")

        return aux
    return {}


resp = trace_parser()
pprint(resp)


class TestFunc:
    def test_func(
            self,
    ):
        response = trace_parser()
        print(response)
        assert len(response) == 5


c = TestFunc()
print(c)
