print("Started Adding the Users.");
print("Started Adding the Users.");
print("Started Adding the Users.");
console.log("Started Adding the Users.");
console.log("Started Adding the Users.");
console.log("Started Adding the Users.");


dbAdmin = db.getSiblingDB('admin')
dbAdmin.auth('root', 'Admin123');
dbAdmin.createUser(
  {
    user: "tester",
    pwd:  "tester123",
    roles: [ { role: "readWrite", db: "eadatabase" }]
  }
);

db = db.getSiblingDB('eadatabase');
db.auth('root', 'Admin123');

db.createUser(
    {
      user: "tester",
      pwd:  "tester123",
      roles: [ { role: "readWrite", db: "eadatabase" }]
    }
  );

db.createCollection("collection_test", {name: "Teste John Doe", age: 30});
db.insertOne({
  nome: "teste",
  age: 25
})

console.log("Finishing Adding the Users.");
console.log("Finishing Adding the Users.");
console.log("Finishing Adding the Users.");
