import sys
import os.path
import pandas as pd
import pandas
import json
import ignore
import config
from json import JSONDecodeError
from typing import List

import mysql
import mysql.connector

import domain.Uri
import domain.OperationUriCorrelation
import domain.OperationUriCorrelation
import domain.Correlation

import pymongo
from repository import ArangodbRepository

import re
from repository import MongoDbRepository

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

def getLogs() -> List:
    # itera sobre os logs obtidos no banco de dados e retorna a lista destes logs
    try:
        myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
        mydb = myclient[config.MONGO_DB_SERVER["databasename"]]
        collection_calls = mydb["api-call-details"]

        # isso aqui Recupera um cursor a partir do filtro
        """     for x in collection_calls.find({}, { "_id": 0, "id" : 1}):
            request_id = x["id"]
        #    request_id = "D8KkloEBGjj1AzoTb38x"
            print(request_id)
            getCallsById(request_id) """

        logs = []
        # cursor = collection_calls.find()

        """ usando o pandas"""
        cursor_of_docs = list(collection_calls.find())
        list_docs = collection_calls.find()
        #df_aux = pandas.read_sql(teste)
        document_list = pandas.DataFrame(list_docs)

        for i, doc in enumerate(cursor_of_docs):
            document = pandas.DataFrame(columns=[])
            #doc["_id"] = str(doc["_id"])
            doc_id = doc["_id"]
            #serial_obj = pandas.Series({"one": "index"})
            #serial_obj.index = ["one"]
            serial_obj = pandas.Series(doc, name=doc_id)
            document = document.append(serial_obj) # este funciona, mas tá reclamando que método está deprecated
            #documentNew = pd.concat([document, serial_obj], ignore_index=True, axis="columns") # appending the serial_obj to the document series
            # clean null values
            document.dropna
            # extracts attributes equalities between the current document and the others documents in the list
            attributes_extraction(document, document_list)
            #document.drop

        # print("documents:", documents)
        #json_export = documents.to_json()
        #json_loaded = json.loads(json_export)
        # recursive_extraction(json_loaded)

        return logs
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))

# Extracts attributes using pandas
def attributes_extraction(dataframe_json, doc_list_dataframe):
    #variables defs
    trace_outer = ""
    save_correlation = True # Controla mais a frente se a correlacao deve ser salva

    if {"uri", "clientId"}.issubset(dataframe_json.columns):
        uri = dataframe_json["uri"][0]
        client_id = dataframe_json.get("clientId")[0]
        method = dataframe_json.get("method")[0]
        request_timestamp = dataframe_json.get("receivedOnDate")[0]
    else:
        return None

    try:
        # identificar o path no swagger, pesquisar no Mongo/swaggers o path que casa dom a uri
        operation_path = MongoDbRepository.MongoDbRepository.find_fullpath_swagger(uri)
        if isinstance(dataframe_json, pandas.DataFrame):
            if (uri == "" or uri is None or pandas.isnull(uri)) or (client_id == "" or client_id is None or pandas.isnull(client_id)) or (
                    request_timestamp == "" or request_timestamp is None or pandas.isnull(request_timestamp)):
                return None

            # verifica se já existe a instância de uri, se não existir a cria
            uri_obj_rec = None
            uri_obj_aux = domain.Uri.Uri(None, uri, client_id, method, operation_path, request_timestamp)
            if not uri_obj_aux.is_valid():
                return None

            #verificar se instancia URI ja existe no Arango, senão cria
            uri_obj_rec = ArangodbRepository.ArangodbRepository.find_operation_uri(uri_obj_aux)
            if uri_obj_rec is None:
                uri_obj_rec = ArangodbRepository.ArangodbRepository.create_operation_uri(uri_obj_aux)

            # itera nos demais atributos para mapear os registros com os mesmos valores
            # então captura o nome do atributo e o valor
            # Atualiza o registro da URI condicionante e da URI condicionada
            df_aux = doc_list_dataframe.copy()
            df_doc = dataframe_json.copy()

            for row in df_doc.itertuples(index=False, name=None):
                for key, value in enumerate(row):
                    # Aqui tem que fazer outro find, ou no banco ou na colection para varrer e verificar os atributos repetidos em valores
                    # print(dataframe_json.columns.values[key], " : ", value)
                    #outer_aux_attr_name = dataframe_json.columns.values[key]
                    outer_aux_attr_name = df_doc.columns.values[key]
                    # ignorar campos registrados no ignore e campos vazios
                    if ignore.field_to_ignore(outer_aux_attr_name) or outer_aux_attr_name is None or value is None or str(value).isspace():
                        continue
                    if outer_aux_attr_name == "trace":
                        trace_outer = value

                    for aux_row in df_aux.itertuples():
                        # se os valores demais campos corresponderem, exceto o trace
                        save_correlation = True
                        for aux_cols_i, aux_col_val in enumerate(aux_row):
                            inner_aux_attr_name = df_aux.columns.values[aux_cols_i-1]
                            if aux_col_val == value:
                                inner_op_path = MongoDbRepository.MongoDbRepository.find_fullpath_swagger(aux_row.__getattribute__("uri"))
                                uri_inner = domain.Uri.Uri(None, aux_row.__getattribute__("uri"), aux_row.__getattribute__("clientId"),
                                                           aux_row.__getattribute__("method"), inner_op_path, aux_row.__getattribute__("receivedOnDate"))
                                # verifica se as duas uris calss são válidas (possuem os campos obrigatórios) e não são iguais, então savará a correlação, pois há pelo menos um atributo igual
                                #if not uri_obj_rec.__eq__(uri_inner) and uri_inner.is_valid():
                                uri_obj_rec.service_destination = get_api_destination_in_trace(aux_row.__getattribute__("trace"))
                                ArangodbRepository.ArangodbRepository.save_uri_destination(uri_obj_rec.get_id(), uri_obj_rec.service_destination)
                                correlation = ArangodbRepository.ArangodbRepository.save_edge_correlation(uri_obj_rec, uri_inner)
                                save_correlation = False  # The correlation was saved and do not need repeat or update it
                                if correlation is not None and isinstance(correlation, domain.OperationUriCorrelation.OperationUriCorrelation):
                                    # já salva a igualdade conhecida.
                                    # Save the commom values not in the trace
                                    save_correlation_matched_values(correlation, outer_aux_attr_name, inner_aux_attr_name, value)
                                    # Recupera o campo trace do log no caso do Sensedia API Gateway, pois é outra estrutura
                                    #save_matched_field_in_traces(trace_outer, trace_inner)

                                    # Recupera o campo trace do log no caso do Sensedia API Gateway, pois é outra estrutura
                                    # save_matched_field_in_traces(trace_outer, trace_inner)
                                    trace_inner = aux_row.__getattribute__("trace")
                                    if (len(trace_outer) > 0) and (len(trace_inner) > 0):
                                        # If there is repeated values in trace, save correlation
                                        # and iterate in repeated values to save in repeated attributes list
                                        # aux_match_values = get_trace_equalities(trace_outer, trace_inner)
                                        save_matched_field_in_traces(correlation, trace_outer, trace_inner)


        print("Attribute Extraction Finished")

    except Exception as error:
        print('EventBuildArango.attributes_extraction() Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))



def get_atributes_in_trace(parsed_trace_body, parent_field = "") -> dict:
    #  a partir do trace itera e cria uma dic com
    retorno = {}
    parent_aux = None
    try:
        #trace_body = get_trace_body(parsed_traces)
        if parsed_trace_body is not None:
            for k, v in parsed_trace_body.items():
                if parent_field is None or len(parent_field) < 1:
                    parent_aux = k
                else:
                    parent_aux = parent_field + "." + k
                if isinstance(v, dict):
                    aux = get_atributes_in_trace(v, parent_aux)
                    if len(aux) > 0:
                        retorno.update(aux)
                elif isinstance(v, list):
                    for log_body in v:
                        aux_dump = json.dumps(log_body)
                        aux_value = json.loads(aux_dump)
                        aux = get_atributes_in_trace(aux_value, parent_aux)
                        if len(aux) > 0:
                            retorno.update(aux)
                        print(aux)
                else:
                    aux = {parent_aux: v}
                    if len(aux) > 0:
                        retorno.update(aux)
        return retorno
    except JSONDecodeError as excinfo:
        print(f"Não foi possivel converter para json: {parsed_trace_body} | {excinfo}")
        raise
    except Exception as error:
        print('ArangoEventBuild.get_atributes_in_trace() Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        raise


# get the service destination in the trace in Sensedia
def get_api_destination_in_trace(body) -> str:
    log_body = None
    json_body = None
    trace_log = None
    api_destination = None
    try:
        #body_to_json = body.to_json(orient='records')
        json_parsed = json.loads(body)
        for trace_log in json_parsed:
            #if trace_log["message"] == "Response log" or len(trace_log["data"]["log"]["body"]) > 0:
            msg = str(trace_log["message"])
            if msg.startswith("Found matching route:"):
                s1 = msg.split(" => ")
                for i in s1:
                    if i.startswith("http"):
                        s2 = i.split(" ")
                        for j in s2:
                            if j.startswith("http"):
                                api_destination = j
                                break
                                break
                                break
                #aux_body = trace_log["data"]["log"]["body"] #it is needed rstrip because of the presence of special characters
        return api_destination
    except JSONDecodeError as excinfo:
        print("Não foi possivel converter para json: ", {trace_log}, {excinfo})
        print("in module ", __name__)
        raise
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("in module ", __name__)
        raise

# get the body of trace in Sensedia
def get_trace_body(body) -> dict:
    #expected_info = {}
    #json_trace = json.loads(parsed_traces)
    log_body = None
    json_body = None
    trace_log = None
    try:
        json_body = json.loads(body)
        for trace_log in json_body:
            #if trace_log["message"] == "Response log" or len(trace_log["data"]["log"]["body"]) > 0:
            if trace_log["message"] == "Response log":
                aux_body = trace_log["data"]["log"]["body"] #it is needed rstrip because of the presence of special characters
                aux_body = aux_body.replace("\n", "").replace("\t", "").replace('"', "'").strip()
                aux_body = aux_body.replace("'", '"')
                log_body = json.loads(aux_body)
                break
        return log_body
    except JSONDecodeError as excinfo:
        print("Não foi possivel converter para json: ", {trace_log}, {excinfo})
        raise
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("in module ", __name__)
        raise

def get_trace_equalities(trace1, trace2) -> list:
# Compare two bodytrace from Sensedia API Gateway Log and return a list with the equalities atributes

    ret = []
    try:
        trace1_body = get_trace_body(trace1)
        trace2_body = get_trace_body(trace2)
        if trace1_body is None or trace2_body is None:
            return None

        trace_1_flated = get_atributes_in_trace(trace1_body)
        trace2_flated = get_atributes_in_trace(trace2_body)

        for k, v in trace_1_flated.items():
            for ki, vi in trace2_flated.items():
                if v == vi:
                    #save_correlation_matched_values(correlation.get_id(), k, ki, v)
                    ret.append({k: v})
                print("save_matched_field_in_traces: ", k + "=" + v, ki + "=" + vi)

        return ret

    except Exception as error:
        print("Ocorreu um erro ao tentar comprara dois traces em get_trace_equalities", error)
        print("mensagem", str(error))
        print("in module ", __name__)



def find_uri(uri, client_id, request_timestamp) -> domain.Uri:
    # busca se existe registro na tabela uri, basicamente uma mesma uri chamada por um clint_id no mesmo momento

    if (uri == "" or pandas.isnull(uri)) or (client_id is None or client_id == "") or (request_timestamp is None or request_timestamp == ""):
        return None

    mydb = mysql.connector.connect(
        host=config.MYSQL_DB_SERVER["host"],
        port=config.MYSQL_DB_SERVER["port"],
        user=config.MYSQL_DB_SERVER["user"],
        password=config.MYSQL_DB_SERVER["password"]
    )

    cursor = mydb.cursor(buffered=True)

    try:

        query = ("SELECT uri, clientId, requestTimeStamp FROM EA_Discovery.uri WHERE uri = %s AND clientId = %s AND requestTimeStamp = %s")
        """query = (
            "SELECT uri, clientId, requestTimeStamp FROM EA_Discovery.uri WHERE uri = %s AND clientId = %s") """
        request_datetime = request_timestamp
        val = (uri, client_id, request_datetime)
        cursor.execute(query, val)
        record = cursor.fetchone()

        if record is not None:
            retorno = domain.Uri.Uri(record[0], record[1], record[2])
            return retorno
        else:
            return None

    except mysql.connector.Error as e:
        print("Error reading data from MySQL table", e)
        print("mensagem", str(e))
    finally:
        if mydb.is_connected():
            mydb.close()
            cursor.close()
            print("MySQL connection is closed")

"""
def create_uri(uri, client_id, request_timestamp):

    if (uri == "" or pandas.isnull(uri)) or (pandas.isnull(client_id) or client_id == "") or (pandas.isnull(request_timestamp) or request_timestamp == ""):
        return None
    try:
        mydb = mysql.connector.connect(
            host=config.MYSQL_DB_SERVER["host"],
            port=config.MYSQL_DB_SERVER["port"],
            user=config.MYSQL_DB_SERVER["user"],
            password=config.MYSQL_DB_SERVER["password"]
        )

        cursor = mydb.cursor()
        dml = "INSERT INTO EA_Discovery.uri (uri, clientId, requestTimeStamp) VALUES (%s, %s, %s)"
        #data = dateutil.parser(request_timestamp)
        dataobj = datetime.datetime.strptime(request_timestamp, '%Y/%m/%d %H:%M:%S  %z')
        vals = (uri, client_id, dataobj)
        cursor.execute(dml, vals)
        mydb.commit()

    except mydb.connector.Error as e:
        print("Error reading data from MySQL table", e)
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
    finally:
        if mydb.is_connected():
            mydb.close()
            cursor.close()
            print("MySQL connection is closed")
"""

def json_recursive_extraction(param_json_obj):
    arr = []
    print(type(param_json_obj))
    try:
        if isinstance(param_json_obj, dict):
            print("Eh um dic")
            for key, value in param_json_obj.items():
                print(key, " : ", value)
                json_recursive_extraction(value)
                # yield from recursive_extraction(value)
        elif isinstance(param_json_obj, list):
            print("Eh um list")
            for item in param_json_obj:
                print(item)
                print(param_json_obj[item])
                json_recursive_extraction(item)
                # yield from recursive_extraction(item)
        else:
            print("Não dic nor list", type(param_json_obj))

    except Exception as error:
        print("In module :", __name__)
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        raise

def save_correlation_matched_values(correlation: domain.OperationUriCorrelation.OperationUriCorrelation, antecendent_attribute_name, consequent_attribute_name, attribute_value):
    # salva na correlaçao em repeated atributes o nome do atributo e o valor correspondente.
    try:
        if correlation is None or antecendent_attribute_name is None or consequent_attribute_name is None or attribute_value is None:
            raise Exception("EventBuild.save_correlation_matched_values()", "Algum dos valores passados é None", correlation.get_id())

        # Tinha hora que invés de objeto esta sendo passsado int
        if isinstance(correlation, domain.OperationUriCorrelation.OperationUriCorrelation):
            ArangodbRepository.ArangodbRepository.save_correlation_repeated_attributes(correlation.get_id(), antecendent_attribute_name,
                                                                                       consequent_attribute_name, attribute_value)
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))
        print("In save_correlation_matched_values module :", __name__)

# compare two traces of Sensedia API Gateway. If their fields values match, it save the equality in correlation
def save_matched_field_in_traces(correlation: domain.Correlation.Correlation, trace1, trace2):
        outer_trace_body = get_trace_body(trace1)
        flated_outer_body = get_atributes_in_trace(outer_trace_body)
        inner_trace_body = get_trace_body(trace2)
        flated_inner_body = get_atributes_in_trace(inner_trace_body)
        print("saving save_matched_field_in_traces = ", flated_outer_body, " : ", flated_inner_body)
        # Iterate in the attibute values obtained in the two traces and save the attibute matched in the correlations
        if (correlation is not None) and (len(flated_outer_body) > 0) and (len(flated_inner_body) > 0):
            for k, v in flated_outer_body.items():
                for ki, vi in flated_inner_body.items():
                    if v == vi:
                        # Antes verifica se o attributo já não está criado
                        if ArangodbRepository.ArangodbRepository.get_correlation_repeated_attributes(correlation.get_id(), k, ki, v) is not None:
                            save_correlation_matched_values(correlation.get_id(), k, ki, v)
                            print("EventBuildArango.save_matched_field_in_traces: ", k, "= ", v, ki, " = ", vi)
                        #TODO caso o atributo exista tem que incrementar a quantidade

def trace_parser() -> list:
    """Intera sobre todas as chamadas da API e returna uma lista com as informações dos "cartid", "cliente" ou "dataPedido" """

    myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
    mydb = myclient[config.MONGO_DB_SERVER["databasename"]]
    collection_calls = mydb["api-call-details"]

    # Acho que está tudo em api-call-details, não precisa deste join com api-calls
    stage_lookup_calls = {
        '$lookup': {
            'from': 'api-calls',
            'localField': 'requestID',
            'foreignField': 'requestID',
            'as': 'details',
        }
    }

    stage_match = {"$match": {"apiId": 1578}}

    stage_limit_1 = {"$limit": 30}

    pipeline = [
        stage_lookup_calls,
        stage_match,
        stage_limit_1
    ]

    result = list(collection_calls.aggregate(pipeline))

    # calls = result["calls"]

    expected_info = []

    print(len(result))

    for call in result:
        id_da_call = call["id"]
        # req_call = requests.get(id_call_url + id_da_call, headers=my_headers)
        # chamadas_especificas_por_id = req_call.json()
        # chamadas_especificas_por_id = call.json()
        traces = call["trace"]
        if traces is not None:
            parsed_traces = json.loads(traces)

        for trace_log in parsed_traces:
            if trace_log["message"] == "Request log" or trace_log["message"] == "Response log":
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


def _get_log_from_pymongo_cursor():
    pass
    """ Usando o próprio cursor do pymongo"""
    # print("documents:", documents)
    # json_export = documents.to_json()
    # json_loaded = json.loads(json_export)
    # recursive_extraction(json_loaded)

"""
    for x in collection_calls.find():
        # pprint(x)
        #pprint(" ** {apiId}, {trace}".format(
        #        apiId=x['apiId'],
        #        trace=x['trace'],
                #body=x['body'],
         #       )
         #   )

        # obj1 = x['trace']
        # print('*** obj1', obj1)
        # dicJsonTrace = json.loads(obj1)
        # dic_json_call = json.loads(x)
        # logs.append(dic_json_call)

        # varrer o json para obter os atributos e valores
        # for call in dic_json_call:
        # json_dump = json.dumps(x)
        cursor_list = list(x)
        json_dump = dumps(cursor_list)
        json_loaded = json.loads(json_dump)
        # recursive_extraction(json_loaded)
        for key, value in x.items():
            print("chave", key, "valor=", value)
            # recursive_extration(value)
            if key == "trace":
                parsed_traces = json.loads(json_dump)
                # trace_parser(parsed_traces)

        # pprint(obj1[0])

    #return logs """


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

    aux = {}
    if body_log.get("cliente"):
        if body_log.get("cliente"):
            aux["cliente"] = body_log["cliente"].get("codigo")
        if body_log.get("numPedido"):
            aux["numPedido"] = body_log.get("numPedido")
        if body_log.get("cart"):
            # aux["cartid"] = body_log["cart"].get("cartid")
            aux["cartid"] = body_log["cart"]
            aux["cliente"] = body_log["cart"].get("cliente")

        return aux
    return {}


#logs = getLogs()

