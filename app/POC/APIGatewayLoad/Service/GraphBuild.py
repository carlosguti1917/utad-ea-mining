import repository.ArangodbRepository
import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import config
from asciitree import *



class GraphBuild:

    def __init__(self):
        pass

    @staticmethod
    def getCalls(begindate):
        return begindate

    @staticmethod
    def getCallDetails(request_id):
        print(request_id)
        return request_id

    @staticmethod
    def saveCallDetails(dicJson):
        print("****dicJson ****", dicJson)

    # sub iterateable object to build up the tree for draw_tree:
    @staticmethod
    class Node(object):
        def __init__(self, name, children, caseid):
            self.caseid = caseid
            self.name = name
            self.children = children

        def getCaseid(self):
            return self.caseid

        def getChild(self, searchname):
            for child in self.children:
                if child.name == searchname:
                    return child
            return None

        def __str__(self):
            return self.name

    @staticmethod
    def loadGraph(beginDate, graphName):
        repo = repository.ArangodbRepository.ArangodbRepository()
        if graphName is None:
            graphName = "default_graph"

        #urisList = repo.getUris()
        correlationList = repo.getUriCorrelations(repo)

        for c in correlationList:
            # start node for the graph
            startNode = c["_from"]
            pgraph = repo.loadGraph(repo, graphName, startNode)
            case_id = 0
            for path in pgraph:
                pedge = path["edges"]
                # Verify if the rootNode has a case id,  if not create to it
                if 'case_id' in pedge[0]:
                    case_id = pedge[0]['case_id']
                else:
                    if len(pedge) > 1:
                        #repo = repository.ArangodbRepository.ArangodbRepository()
                        case_id = repo.getNewCaseId(repo)
                    # updateEdge(edge, k, case_id)
                    #repo.setPathCaseId(edge, k, case_id)
                rootNode = GraphBuild.Node(startNode, [], case_id)
                GraphBuild.iteratePath(pedge, 0, rootNode)
                print(draw_tree(rootNode), "case_id:", case_id)
                case_id = 0
                #iteratePath(pedge, 0, rootNode)
            #TODO pensar que as correlações (Elas pode supostamente fazer parte de mais de um caminho candidato




    # Verfica se o path já tem um caseid, caso não tenha, obtém o último case id e cria um novo para o path
    @staticmethod
    def iteratePath(edge, depth, currentNode):
        #pcaseid = None
        pname = edge[depth]['node']
        subNode = currentNode.getChild(pname)

        #atualizar edge com o id do caso
        k = edge[depth]['_key']
        # Verify if it has a case id,  if not create to it
        if 'case_id' in edge[depth]:
            caseid =  edge[depth]['case_id']
        else:
            caseid  = currentNode.getCaseid()
            # Se o case id for maior que zero atualiza a correlação com o caseid, senão ignora
            if caseid > 0:
                repo = repository.ArangodbRepository.ArangodbRepository()
                repo.setPathCaseId(edge, k, caseid)

        if subNode == None:
            subNode = GraphBuild.Node(pname, [], caseid)
            currentNode.children.append(subNode)
        if len(edge) > depth + 1:
            #iteratePath(edge, depth + 1, subNode)
            GraphBuild.iteratePath(edge, depth + 1, subNode)



# Executa rotina de loader
beginDate = "2022-06-27T00:00:00.015Z"
#x = LoaderCalls(beginDate)
graph_name = "default_graph"

x = GraphBuild().loadGraph(beginDate, graph_name)
