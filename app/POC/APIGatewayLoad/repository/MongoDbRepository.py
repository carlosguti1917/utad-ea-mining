import pymongo
import config
import domain.Uri
import pandas
import re

class MongoDbRepository:

    def __init__(self):
        pass

    # Verifica se os campos requeridos da Uri estão todos preenchidos
    @staticmethod
    def find_fullpath_swagger(uri: str) -> str:
        server = None
        path = None
        retorno = None
        try:
            myclient = pymongo.MongoClient(config.MONGO_DB_SERVER["host"])
            mydb = myclient[config.MONGO_DB_SERVER["databasename"]]
            collection_swaggers = mydb["swaggers"]

            # isso aqui Recupera um cursor a partir do filtro no mongo
            '''for x in collection_swaggers.find({}, { "uri": 0, "id" : 1}):
                request_id = x["id"]
                print(request_id)'''

            """ usando o pandas"""
            #cursor_of_docs = list(collection_swaggers.find())
            cursor_of_docs = collection_swaggers.find()
            #document_list = pandas.DataFrame(cursor_of_docs)

            #atributtes to discovery the route. Basically is the composition of servers and paths

            for i, doc in enumerate(cursor_of_docs):
                document = pandas.DataFrame(columns=[])
                #servers = [x for x in doc.servers if x.url == uri_base_path]
                for i_server in doc.get("servers"):
                    if i_server.get("url") in uri:
                        server = i_server.get("url")
                        break

                # get the right path
                # TODO tratar os campos da query string; Ex. ['/carts/', '350', '?client_id=', '287', 'ec', '8', 'b', '9', '-f', '794', '-', '39', 'd', '6', '-ab', '38', '-', '1329', 'b', '647', 'e', '9', 'db']
                if server is None:
                    break
                uri_parts = re.split("(\?)", uri[len(server):])
                if uri_parts is not None and len(uri_parts) > 1:
                    query_string = uri_parts[1]
                resouces = re.split("([0-9]+)", uri_parts[0])
                pattern_string = r"(?!(?!.*{0}/)"
                r_count = 0
                for j in range(len(resouces)):
                    resouce_name = resouces[j].replace("/", "")
                    resouce = resouces[j]
                    if resouce_name is not None and len(resouce_name) > 1 and not resouce_name.isdigit():
                        if r_count == 0:
                            #pattern_string = re.sub(r"{0}}", resouce_name, pattern_string)
                            pattern_string = pattern_string.format(resouce_name)
                        else:
                            pattern_string = pattern_string + "|(?!.*/" + resouce_name + "/.*)"
                        r_count = r_count + 1

                #closign the patter_string
                pattern_string = pattern_string + ")/.*$"
                #pattern_string = pattern_string.replace(pattern_string, new_pattern_string)

                # sorting the path bay its lenght
                paths = doc.get("paths")
                ordered_paths = sorted(doc.get("paths"), key=lambda k: len(doc.get("paths")[k]), reverse=True)
                ordered_paths = sorted(ordered_paths, key=len, reverse=True)
                pattern = re.compile(pattern_string)
                for i_path in ordered_paths:
                    inner_path = re.search(pattern, i_path)
                    if inner_path is not None:
                        path = inner_path.string

            if server is None:
                print("Server not found", uri)
                return None
            if path is None:
                print("MongoDvRepository.find_fullpath_swagger(): path not found para uri ", uri)
                return None

            retorno = server + path
            return retorno

        except Exception as error:
            print("MongoDvRepository.find_fullpath_swagger() uri:", uri)
            print(__class__, __name__, __file__)
            print('MongoDvRepository.find_fullpath_swagger() Ocorreu problema {} '.format(error.__class__))
            print("mensagem", str(error))