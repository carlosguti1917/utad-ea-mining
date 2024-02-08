import pyArango
from pyArango import collection
from pyArango.connection import *
from pyArango.collection import Collection, Field
from pyArango.graph import Graph, EdgeDefinition
import sys
from pyArango.connection import *
from pyArango.graph import *
from asciitree import *

conn = Connection(arangoURL="http://127.0.0.1:8529/", username="root", password="123")
# db = conn.createDatabase(name="school")
db = conn["_system"]
#print(db)

def getcollectionUris():
   aql = "FOR u IN URI_V4 RETURN u._key"
   queryResult = db.AQLQuery(aql, rawResults=True, batchSize=100)
   contador = 0
   for key in queryResult:
      #print(key)
      contador = contador + 1

   #print(contador)


def creteCorrelations():
   edge1 = db["Correlations_V3"]
   print('colletion: %s:' % edge1)

   doc1 = edge1.createDocument()
   doc1["_from"] = "URI_V3/568535"
   doc1["_to"] = "URI_V3/568489"
   doc1["_key"] = "2110790"
   doc1["_node"] = "URI_V3/568535_to_URI_V3/568489"
   doc1.save()
   ## outra opção é
   # a = myThings.createDocument()
   # b = myThings.createDocument()
   # conn = myConnections.createEdge()
   # conn.links(a, b)
   # conn["someField"] = 35
   # conn.save()  # once an edge links documents, save() and patch() can be used as with any other Document object


#Ler um graph e criar cases id
# outra opção é criar uma ARM temporal a partir das URIs

def lerGraph():
   #db = conn["transversalGraph_CorrelationsV4"]
   if not db.hasGraph("transversalGraph_CorrelationsV4"):
      raise Exception("didn't find the debian dependency graph, please import first!")

   ddGraph = db.graphs['transversalGraph_CorrelationsV4']
   #vertexCollection = ddGraph.
   #print(vertexCollection)

   #graphQuery = '''FOR URI_V4, Correlations_V4, URI_V4 IN  1..3 OUTBOUND @startNode Correlations_V4 RETURN path '''
   graphQuery = "FOR URI_V4, Correlations_V4, path IN  1..50 OUTBOUND @startNode Correlations_V4 RETURN path "

   # Tem que retornar 4 nós com caso 240
   startNode = "URI_V4/240568113"
   bindVars = {"startNode": startNode}
   queryResult = db.AQLQuery(graphQuery, bindVars=bindVars, rawResults=True)
   #print(queryResult)


   class CaseNumber():
      casenumber = 0

      def getNewCaseNumber(self):
         self.casenumber = self.casenumber + 1
         return self.casenumber


   # sub iterateable object to build up the tree for draw_tree:
   class Node(object):
      def __init__(self, name, children):
         self.case = CaseNumber()
         self.name = name
         self.children = children

      def getChild(self, searchname):
         for child in self.children:
            if child.name == searchname:
               return child
         return None

      def __str__(self):
         return self.name

   def iteratePath(edge, depth, currentNode):
      pname = edge[depth]['_node']
      subNode = currentNode.getChild(pname)

      #atualizar edge com o id do caso
      k = edge[depth]['_key']
      case = CaseNumber()
      caseid = case.getNewCaseNumber()
      updateEdge(edge, k, caseid)

      if subNode == None:
         subNode = Node(pname, [])
         currentNode.children.append(subNode)
      if len(edge) > depth + 1:
         iteratePath(edge, depth + 1, subNode)



   def updateEdge(e, k, caseid):
      updateEdgeQry2= "UPDATE @key WITH { caseid: @caseid } IN  Correlations_V4"
      bindVars2 = {"key": k, "caseid": caseid}
      query = db.AQLQuery(updateEdgeQry2, bindVars=bindVars2, rawResults=True)
      #print(query)

   # Now we fold the paths substructure into the tree:
   rootNode = Node(startNode, [])
   for path in queryResult:
      pedge = path["edges"]
      iteratePath(pedge, 0, rootNode)




   print(draw_tree(rootNode))

lerGraph()