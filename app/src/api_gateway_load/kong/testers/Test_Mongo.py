import pymongo


myclient = pymongo.MongoClient('mongodb://root:Admin123@192.168.0.15:27017/')
mydb = myclient['eamining']
collection_calls = mydb["kong-api-call-details"]
teste1 = collection_calls.find_one()
teste = collection_calls.find()

print(teste.__str__)
