import pyArango.connection
from pyArango.connection import *
#from arango import ArangoClient
import re
import domain.Uri
import config
import pandas
import datetime
#from repository.MySqlRepository import MySqlRepository
import domain.OperationUriCorrelation
import domain.RepeatedAttributes

import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

### Static methods area

@staticmethod
def getNewDatabaseConnection(self) -> DBHandle:
    newconn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"], password=config.ARANGO_DB_SERVER["password"])
    newdatacon = self.newconn["_system"]
    return newdatacon

class ArangodbRepository:
    conn: Connection
    dtb: DBHandle

    #Instancia e cria a connexão
    def __init__(self):
        self.conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"], password=config.ARANGO_DB_SERVER["password"])
        self.dtb = self.conn["_system"]

    def getConnection(self):
        return self.conn

    def getDatabase(self):
        return self.dtb



    #TODO aqui o código visa varrer todas as URIs e construir as correlações
    # Acho que dá para fazer por AQL
    @staticmethod
    def buildCorrelationsV4():
        pass

    # Verifica se os campos requeridos da Uri estão todos preenchidos
    @staticmethod
    def check_uri_required(obj: domain.Uri.Uri) -> bool:
        '''if (obj.get_uri() == "" or pandas.isnull(obj.get_uri())) or (
                pandas.isnull(obj.get_client_id()) or obj.get_client_id() == "") or (
                pandas.isnull(obj.get_request_timestamp()) or obj.get_request_timestamp() == ""):
            print("ArangdodbRepository.check_uri_required() is false to object", str(obj))'''
        if not obj.is_valid():
            print("ArangdodbRepository.check_uri_required() is false to object", str(obj.get_uri(), ",", obj.get_client_id(), ",", obj.request_timestamp, ",", obj.get_method()))
            return False
        else:
            return True

    @staticmethod
    def create_operation_uri(uri: domain.Uri.Uri) -> domain.Uri.Uri:
        """ cria uma operation_uri e retorna o _id do o objeto criado com o _id"""
        if (uri.get_uri() == "" or pandas.isnull(uri.get_uri())) or (
                uri.get_client_id() == "" or pandas.isnull(uri.get_client_id())) or (
                uri.get_method() == "" or pandas.isnull(uri.get_method())) or (
                uri.get_operation_path() == "" or pandas.isnull(uri.get_operation_path())) or (
                pandas.isnull(uri.get_request_timestamp()) or uri.get_request_timestamp() == ""):
            #print("ArangodbRepository.create_operation_uri() não criada", vars(uri))
            return None

        conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"],
                             password=config.ARANGO_DB_SERVER["password"])
        dbconn = conn["_system"]

        try:
            collection = db[config.ARANGO_PARAMS["uri_collection"]]
            doc = collection.createDocument()
            doc["uri"] = uri.get_uri()
            doc["client_id"] = uri.get_client_id()
            doc["method"] = uri.get_method()
            doc["request_time_stamp"] = uri.get_request_timestamp()
            doc["operation_path"] = uri.get_operation_path()
            doc["operation_identifier"] = uri.get_operation_identifier()
            doc["service_destination"] = uri.service_destination
            doc.save()
            vid = doc["_id"]
            uri.set_id(vid)
            return uri

        except Exception as error:
            print("classs:", __name__, "file:", __file__, "class:", __class__)
            print('create_operation_uri () Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            raise


    @staticmethod
    def getNewCaseId(self):
        max_caseid = 0
        aql = "for c in " + config.ARANGO_PARAMS["edge_collection"] + " COLLECT AGGREGATE max = MAX(c.case_id) RETURN {max} "
        queryResult = self.dtb.AQLQuery(aql, rawResults=True, batchSize=100)
        for r in queryResult:
            max_caseid = r["max"]

        if max_caseid is None:
            max_caseid = 0

        return max_caseid + 1

    @staticmethod
    def get_correlation_repeated_attributes(correlation_id, antecedent_attribute_name,
                                             consequent_attribute_name,
                                             attribute_value):

        rp_att: domain.RepeatedAttributes.ReapeatedAttributes = None

        conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"],
                          password=config.ARANGO_DB_SERVER["password"])
        dbconn = conn["_system"]
        try:
            if correlation_id is not None and antecedent_attribute_name is not None and consequent_attribute_name is not None and attribute_value is not None:
                qry = "FOR doc in " + config.ARANGO_PARAMS["edge_collection"] + "  " \
                                " FILTER doc._id == @id" \
                                    " for a in doc.repeated_attributes " \
                                        "FILTER a.antecedent_attribute_name == @antecedent_attribute_name " \
                                        " and a.consequent_attribute_name == @consequent_attribute_name " \
                                        " and a.attribute_value == @attribute_value " \
                                    " return a"

                bindVars = {"id": correlation_id, "antecedent_attribute_name": antecedent_attribute_name,
                            "consequent_attribute_name": consequent_attribute_name,
                            "attribute_value": attribute_value}
                queryResult = db.AQLQuery(qry, bindVars=bindVars, rawResults=True)
                #TODO lembrar da quantidade
                for key in queryResult:
                    rp_att = domain.RepeatedAttributes.ReapeatedAttributes(correlation_id, key["antecedent_attribute_name"], key["consequent_attribute_name"], key["attribute_value"])
                return rp_att

        except Exception as error:
            print("classe:", __class__, __file__)
            print('save_correlation_repeated_attributes() Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("in module", __name__)
            raise

    #Retorna todas as URIs que tenham pelo menos um correspondente subsequente
    @staticmethod
    def getUris(self):
        # "AND (REGEX_MATCHES(uc.uri, '(\/[0-9]+\/)')) == (REGEX_MATCHES(ur.uri, '(\/[0-9]+\/)')) " \
        #             "AND STARTS_WITH(uc.uri, LEFT(ur.uri, 50)) " \
        # ua=uri antecedent (uc)
        # uc=uri consequent (ur)
        aql = "FOR uc IN " + config.ARANGO_PARAMS["uri_collection"] + " " \
                "FOR ua in " + config.ARANGO_PARAMS["uri_collection"] + " " \
                    "filter uc.requestTimeStamp >= ua.requestTimeStamp AND ua._id != uc._id  AND uc.clientId == ua.clientId " \
                    "AND ua.uri != uc.uri " \
              "RETURN {ua, uc} "

        queryResult = self.dtb.AQLQuery(aql, rawResults=True, batchSize=100)

        #reg_pattern = '(\/[0-9]+\/?)'
        #re.compile(reg_pattern)
        return queryResult

    #Retorna todas as URIs que tenham pelo menos um correspondente subsequente
    @staticmethod
    def getUriCorrelations(self):
        try:
            aql = "FOR c in " + config.ARANGO_PARAMS["edge_collection"] + " RETURN c "
            db_a = self.dtb
            queryResult = db_a.AQLQuery(aql, rawResults=True, batchSize=100)
            return queryResult

        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))

    @staticmethod
    def find_operation_uri(uri: domain.Uri.Uri) -> domain.Uri.Uri:
        # busca se existe registro na collection Operation_URI, basicamente uma mesma uri chamada por um clint_id
        # no mesmo momento
        # TODO tem que levar em consideração outros atributos, talvez o header, por exemplo, podem haver dois POST para a mesma URI /recurso ao mesmo tempo
        if (uri.get_uri() == "" or pandas.isnull(uri.get_uri())) or (
                pandas.isnull(uri.get_client_id()) or uri.get_client_id() == "") or (
                pandas.isnull(uri.get_request_timestamp()) or uri.get_request_timestamp() == ""):
            return None

        conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"],
                             password=config.ARANGO_DB_SERVER["password"])
        dbconn = conn["_system"]

        try:
            aql = "FOR u IN " + config.ARANGO_PARAMS["uri_collection"] + " " \
                  " FILTER u.uri == @uri " \
                  " && u.client_id == @client_id " \
                  " && u.request_time_stamp == @request_time_stamp " \
                  " && u.method == @method " \
                  " RETURN u "

            bindVars = {"uri": uri.get_uri(), "client_id": uri.get_client_id(),
                        "method": uri.get_method(), "request_time_stamp": uri.get_request_timestamp()}
            queryResult = dbconn.AQLQuery(aql, bindVars=bindVars, rawResults=True)


            for key in queryResult:
                # TODO acertar os paramentros
                ret = domain.Uri.Uri(key["_id"], key["uri"], key["client_id"], key["method"], key["operation_path"], key["request_time_stamp"])
                return ret
            else:
                return None

        except Exception as error:
            print('ArangodbRepository.find_operation_uri() Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            print("in module", __name__)

    @staticmethod
    def find_operation_uri_correlation(antecedent: domain.Uri.Uri, consequent: domain.Uri.Uri) -> domain.OperationUriCorrelation.OperationUriCorrelation:
        # busca uma correlação no banco de dados
        ret = None

        conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"],
                             password=config.ARANGO_DB_SERVER["password"])
        dbconn = conn["_system"]

        try:
            aql = "FOR c IN " + config.ARANGO_PARAMS["edge_collection"] + " " \
                    " FILTER c._from == @pfrom && c._to == @pto " \
                  " RETURN c "

            bindVars = {"pfrom": antecedent.get_id(), "pto": consequent.get_id()}
            queryResult = dbconn.AQLQuery(aql, bindVars=bindVars, rawResults=True)

            for key in queryResult:
                ret = domain.OperationUriCorrelation.OperationUriCorrelation(key["_id"], key["_from"],
                                                                             key["_to"], key["node"])
            #if (queryResult is not None) and (queryResult.count > 0):
            #    ret = domain.OperationUriCorrelation.OperationUriCorrelation(queryResult["_id"], queryResult["_from"], queryResult["_to"], queryResult["node"])

            return ret

        except Exception as error:
            print('ArangodbRepository.find_operation_uri_correlation() Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))
            raise


    @staticmethod
    def loadGraph(self, graphName, startNode):
        var_uri_collection_name = "URI_V5"
        var_edge_name = "Operation_Uri_Correlation"
        try:
            dba = self.dtb
            if not dba.hasGraph(graphName):
                raise Exception("didn't find the informed graph!")

            ddGraph = dba.graphs[graphName]

            graphQuery = "FOR " + config.ARANGO_PARAMS["uri_collection"] + ", " + config.ARANGO_PARAMS["edge_collection"] + ", path IN  1..50 OUTBOUND @startNode " + config.ARANGO_PARAMS["edge_collection"] + " RETURN path "

            # Tem que retornar 4 nós com caso 240
            #bindVars = {"uri": var_uri_collection_name, "edge": var_edge_name, "startNode": startNode}
            bindVars = {"startNode": startNode}
            graphResult = dba.AQLQuery(graphQuery, bindVars=bindVars, rawResults=True)
            return graphResult

        except Exception as error:
            print('Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))

    @staticmethod
    def save_edge_correlation(uri1: domain.Uri.Uri, uri2: domain.Uri.Uri) -> domain.OperationUriCorrelation.OperationUriCorrelation:
        """Cria ou atualiza a correlação
            Se uri não existir cria a uri
            itera nos atributos e atualiza o mapa de atributos da uri e das correspondencias na correlacao"""

        ret: domain.OperationUriCorrelation.OperationUriCorrelation = None  # guarda o retorno

        conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"], password=config.ARANGO_DB_SERVER["password"])
        dbconn = conn["_system"]

        if uri1.__eq__(uri2) and uri2.is_valid() and uri1.is_valid():
            #print("uri1.__eq__(uri2) or invalid", vars(uri1), vars(uri2))
            return None
        elif ArangodbRepository.check_uri_required(uri1) and ArangodbRepository.check_uri_required(uri2):
            try:
                # verifica se as uris já existem e recupera os id
                obj1 = ArangodbRepository.find_operation_uri(uri1)
                obj2 = ArangodbRepository.find_operation_uri(uri2)
                if obj1 is None:
                    obj1 = ArangodbRepository.create_operation_uri(uri1)
                if obj2 is None:
                    obj2 = ArangodbRepository.create_operation_uri(uri2)

                if obj1 is None or obj2 is None:
                    return None

                # verifica qual é o maior para registrar na ordem. Se obj2 > obj1 inverte
                if obj1.get_request_timestamp() > obj2.get_request_timestamp():
                    aux = obj2
                    obj2 = obj1
                    obj1 = aux

                # não grava se as duas URIs forem iguais ou se correlation já existir
                if obj1.id != obj2.id:
                    correlation = ArangodbRepository.find_operation_uri_correlation(obj1, obj2)
                    if correlation is None:
                        edge = db[config.ARANGO_PARAMS["edge_collection"]]
                        doc = edge.createDocument()
                        doc["_from"] = obj1.id
                        doc["_to"] = obj2.id
                        #doc1["_key"] = "2110790"
                        node = str(obj1.get_operation_identifier()) + "_TO_" + str(obj2.get_operation_identifier())
                        doc["node"] = node
                        doc.save()
                        doc_id = doc["_id"]
                        #ret = domain.OperationUriCorrelation(doc_id, obj1.id, obj2.id, node)
                        ret = domain.OperationUriCorrelation.OperationUriCorrelation(doc["_id"], doc["_from"], doc["_to"], doc["node"])
                    else:
                        # incrementa a quantidade de correlacoes encontrada
                        #qtd = correlation.get_quantity() + 1
                        #dml = "UPDATE EA_Discovery.Correlation SET quantity=%s WHERE id=%s "
                        #val = (qtd, correlation.id)
                        #cursor.execute(dml, val)
                        #mydb.commit()
                        #correlation.set_quantity(qtd)
                        ret = correlation

                return ret

            except Exception as error:
                print('ArangodbRepository.save_edge_correlation() Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print("in module", __name__)
                raise

    @staticmethod
    def save_correlation_repeated_attributes(correlation_id, antecedent_attribute_name,
                                             consequent_attribute_name,
                                             attribute_value):

        #ret: domain.RepeatedAttributes.ReapeatedAttributes = None  # guarda o retorno
        # TODO verificar necessidade de atualizar os atributos, só faz sentido se fosse por path e não pela URI
        rp_att: domain.RepeatedAttributes.ReapeatedAttributes = None

        conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"], password=config.ARANGO_DB_SERVER["password"])
        dbconn = conn["_system"]

        if correlation_id is not None and antecedent_attribute_name is not None and consequent_attribute_name is not None and attribute_value is not None:
            try:
                #TODO find atributos para verificar se já existe e incrementar de 1
                #rp_att = MySqlRepository.find_correlation_repeated_attributes(correlation_id, antecedent_attribute_name, consequent_attribute_name, attribute_value)
                teste = ArangodbRepository.get_correlation_repeated_attributes(correlation_id, antecedent_attribute_name, consequent_attribute_name, attribute_value)
                if rp_att is None:
                    updateEdgeQry = "FOR doc in " + config.ARANGO_PARAMS["edge_collection"] + "  " \
                                    " FILTER doc._id == @id" \
                                    " UPDATE doc WITH { repeated_attributes : " \
                                        " PUSH(doc.repeated_attributes, " \
                                            " {'antecedent_attribute_name': @antecedent_attribute_name, " \
                                                " 'consequent_attribute_name': @consequent_attribute_name, " \
                                                " 'attribute_value': @attribute_value}) " \
                                    "} IN " + config.ARANGO_PARAMS["edge_collection"] + ""

                    bindVars = {"id": correlation_id, "antecedent_attribute_name": antecedent_attribute_name,
                                    "consequent_attribute_name": consequent_attribute_name, "attribute_value": attribute_value}
                    query = db.AQLQuery(updateEdgeQry, bindVars=bindVars, rawResults=True)

                else:
                    # incrementa a quantidade de correlacoes encontrada
                    #TODO incrementar no banco de dados
                    qtd = rp_att.get_quantity() + 1
                    rp_att.set_quantity(qtd)
                    ret = rp_att
                    print("save_correlation_repeated_attributes: incrementado de 1 = ", ret)

            except Exception as error:
                print('save_correlation_repeated_attributes() Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print("in module", __name__)
                raise

    @staticmethod
    def save_uri_destination(uri_id, destination):
        conn = Connection(arangoURL=config.ARANGO_DB_SERVER["host"], username=config.ARANGO_DB_SERVER["user"], password=config.ARANGO_DB_SERVER["password"])
        dbconn = conn["_system"]

        if uri_id is not None and destination is not None:
            try:
                qry = "FOR doc in " + config.ARANGO_PARAMS["edge_collection"] + "  " \
                        " FILTER doc._id == @id " \
                            " UPDATE doc WITH { service_destination: @service_destination } " \
                            " IN " + config.ARANGO_PARAMS["edge_collection"] + " "

                bindVars = {"id": uri_id, "service_destination": destination}
                query = db.AQLQuery(qry, bindVars=bindVars, rawResults=True)

            except Exception as error:
                print('save_correlation_repeated_attributes() Ocorreu problema {} '.format(error.__class__))
                print("mensagem", str(error))
                print("in module", __name__)
                raise

    @staticmethod
    def setPathCaseId(e, k, caseid):
      updateEdgeQry2= "UPDATE @key WITH { case_id: @case_id } IN  " + config.ARANGO_PARAMS["edge_collection"]
      bindVars2 = {"key": k, "case_id": caseid}
      query = db.AQLQuery(updateEdgeQry2, bindVars=bindVars2, rawResults=True)
      print(query)





conn: Connection = Connection(arangoURL="http://127.0.0.1:8529/", username="root", password="123")
# db = conn.createDatabase(name="school")
db = conn["_system"]
edge_correlations = db["Correlations_V4"]

#"AND (REGEX_MATCHES(uc.uri, '(\/[0-9]+\/)')) == (REGEX_MATCHES(ur.uri, '(\/[0-9]+\/)')) " \
#             "AND STARTS_WITH(uc.uri, LEFT(ur.uri, 50)) " \

#ua=uri antecedent (uc)
#uc=uri consequent (ur)
aql = "FOR uc IN URI_V4 " \
        "FOR ua in URI_V4 " \
            "filter uc.requestTimeStamp >= ua.requestTimeStamp AND ua._id != uc._id  AND uc.clientId == ua.clientId " \
            "AND ua.uri != uc.uri " \
        "RETURN {ua, uc} "

queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100)
#document = queryResult[0]
#print(document)
reg_pattern = '(\/[0-9]+\/?)'
re.compile(reg_pattern)

def createEdgeCorrelation(doc):
    # ua=uri antecedent
    # uc=uri consequent
    print('colletion: %s:' % edge_correlations)
    try:
        doc1 = edge_correlations.createDocument()
        doc1["_from"] = config.ARANGO_PARAMS["uri_collection"] + "/" + doc["ua"]["_key"]
        doc1["_to"] = config.ARANGO_PARAMS["uri_collection"] + "/" + doc["uc"]["_key"]
        #doc1["_key"] = "2110790"
        doc1["_node"] = doc["ua"]["operationName"] + " to " + doc["uc"]["operationName"]
        doc1.save()
        print("correlation saved" + doc1["_node"])
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))

def searchUriCorrelations():
    try:
        for d in queryResult:
            uc_resource_match = re.search(reg_pattern, d["ua"]["uri"])
            if uc_resource_match:
                uc_resource_id = str(d["ua"]["uri"][uc_resource_match.start(): uc_resource_match.end()]).replace("/", "")
                if uc_resource_id:
                    ur_resource_match = re.search(reg_pattern, d["uc"]["uri"])
                    ur_resource_id = str(d["uc"]["uri"][ur_resource_match.start(): ur_resource_match.end()]).replace("/", "")
                    print("ua_resource_id=" + uc_resource_id + ", uc_resource_id=" + ur_resource_id)
                    if uc_resource_id == ur_resource_id:
                        print(d["ua"]["uri"] + " --> " + d["uc"]["uri"])
                        createEdgeCorrelation(d)
            else:
                print("uc root")
                print(d["ua"]["uri"] + " --> " + d["uc"]["uri"])
    except Exception as error:
        print('Ocorreu problema {} '.format(error.__class__))
        print("mensagem", str(error))