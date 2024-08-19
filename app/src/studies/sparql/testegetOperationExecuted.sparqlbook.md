
```sparql
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?x
WHERE { ?x  <http://www.w3.org/2000/01/rdf-schema#label>  "a14c887c27c00a55cc96c25157ed0f2c" }

```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX aPIC: <aPICall:>

SELECT (count(?api_name) as ?totalcall)
WHERE {
    ?api_call rdf:type ns_core:APICall .
    ?api_call aPIC:api_name ?api_name . 
    FILTER(?api_name = "ecommerce-carts" || ?api_name = "ecommerce-orders" || ?api_name = "payments")
}
```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX aPIO: <aPIOperation:>

SELECT distinct ?resource #?operationExecuted ?operation ?api_call
#SELECT (COUNT(?operation) AS ?operation) 
WHERE {
    ?operation a ns_core:APIOperation . 
    ?operation ^gufo:participatedIn ?api_call .
    ?api_call a ns_core:APICall .
    ?operation ^gufo:mediates ?operationExecuted .
    ?operationExecuted a ns_core:OperationExecuted .
    ?operationExecuted gufo:mediates ?resource .
    ?resource gufo:participatedIn ?api_call .
    ?resource a ns_core:APIResource . 
    FILTER(IRI(?operation) = <http://eamining.edu.pt/POST_http://192.168.0.15:8000/sandbox/ecommerce/v1/carts>
        && IRI(?api_call) = <http://eamining.edu.pt/1f61314f275fcc690049921bffac9314>
    )
}
ORDER BY ?operationExecuted
LIMIT 100


```

```sparql
# V2 - obter os recusos que participam de uma chamada de API
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX aPIO: <aPIOperation:>

SELECT distinct ?resource ?operation #?operationExecuted ?operation ?api_call
#SELECT (COUNT(?operation) AS ?operation) 
WHERE {
    ?operation a ns_core:APIOperation . 
    ?operation ^gufo:participatedIn ?api_call .
    ?api_call a ns_core:APICall .
    ?operation ^gufo:mediates ?operationExecuted .
    ?operationExecuted a ns_core:OperationExecuted .
    ?operationExecuted gufo:mediates ?resource .
    ?resource gufo:participatedIn ?api_call .
    ?resource a ns_core:APIResource . 
    FILTER(
        #IRI(?api_call) = <http://eamining.edu.pt/1f61314f275fcc690049921bffac9314>
        IRI(?api_call) = <http://eamining.edu.pt/db60373a949c022813e4e718dc353a56>
    )
}
ORDER BY ?resource
LIMIT 100
```

```sparql
# Check how much operation executed are in the model
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
SELECT (COUNT(?x) AS ?total_operations_executed) 
WHERE {
    ?x rdf:type ns_core:OperationExecuted .
}

```

```sparql
# Check how much attributes are in the model
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
SELECT (COUNT(?y) AS ?total_atributes)
WHERE {
    ?y rdf:type ns_core:Attribute .
}
```

```sparql
# Check how much frequet temporal correlation are in the model
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

SELECT (COUNT(?x) AS ?count)
WHERE {
    ?x rdf:type ns_process_view:FrequentTemporalCorrelation .
}
```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX aPIC: <aPICall:>

SELECT distinct ?api_name
WHERE {
    ?api_call rdf:type ns_core:APICall .
    ?api_call aPIC:api_name ?api_name . #isso funciona
    #?api_call aPIC:api_name "ecommerce-carts" . # não funciona
    FILTER(?api_name = "ecommerce-carts")
}

```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX attr: <http://eamining.edu.pt/core#Attribute>
PREFIX aPIR: <http://eamining.edu.pt/core#aPIR>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX aPIC: <aPICall:>


SELECT ?api_call ?resource ?attribute 
WHERE {
    #?attribute_name ns_core:attribute_name ?attribute .
    ?api_call rdf:type ns_core:APICall .
    ?api_call aPIC:api_name "ecommerce-carts" .
    ?resource rdf:type ns_core:APIResource .
    ?attribute rdf:type <http://eamining.edu.pt/core#Attribute> .
    ?attribute rdfs:label "itens.produto" .
    ?attribute_name ns_core:resource_data ?attribute .
    ?attribute_name attribute:attribute_name  .
    ?attribute attr2:attribute_value ?attributeValue .
}
LIMIT 10


```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX aPIO: <aPIOperation:>

SELECT ?resource 
#SELECT (COUNT(?resource) AS ?resource) 
WHERE {
    ?operationExecuted rdf:type ns_core:OperationExecuted .
    ?operationExecuted gufo:mediates ?resource .
    ?resource rdf:type ns_core:APIResource .
    ?operationExecuted gufo:mediates ?operation .
    ?operation rdf:type ns_core:APIOperation .
    ?operation rdfs:label ?operation_label .
    FILTER(?operation_label = 'POST_http://192.168.0.15:8000/sandbox/ecommerce/v1/carts')
}
LIMIT 10

```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>

SELECT ?resource
WHERE {
    ?operationExecuted rdf:type ns_core:OperationExecuted .
    ?operationExecuted gufo:mediates ?resource .
    ?resource rdf:type ns_core:APIResource .
    ?operationExecuted gufo:mediates <http://eamining.edu.pt#/sandbox/ecommerce/v1/carts/562> .
}

```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

SELECT DISTINCT ?consumerApp
WHERE {
    ?consumerApp rdf:type ns_core:ConsumerApp .
    FILTER NOT EXISTS {
        ?subclass rdf:type ns_process_view:Partner .
        ?subclass rdfs:subClassOf ?consumerApp .
        FILTER (?subclass != ?consumerApp)
    }
}


```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX attr: <http://eamining.edu.pt/core#Attribute>
PREFIX aPIR: <http://eamining.edu.pt/core#aPIR>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX aPIC: <aPICall:>
PREFIX attr2: <attribute:> 
#SELECT  (COUNT(?api_call) AS ?count_call) #(COUNT(?resource) AS ?resources) (COUNT(?resource) AS ?attributes)  
SELECT  ?api_call ?operation #?resource #?attribute  
WHERE {
    #?attribute_name ns_core:attribute_name ?attribute .
    ?operation rdf:type ns_core:APIOperation .
    ?operation gufo:participedIn ?api_call .
    ?api_call rdf:type ns_core:APICall .
    ?api_call aPIC:api_name "ecommerce-carts" .
    #?operationExecuted rdf:type ns_core:OperationExecuted .
    #?operationExecuted gufo:mediates ?operation .
    #?resource rdf:type ns_core:APIResource .
    #?operationExecuted gufo:mediates ?resource .
    #?resource rdf:type ns_core:APIResource .
    #?attribute rdf:type <http://eamining.edu.pt/core#Attribute> .
    #?attribute attr2:attribute_name "cliente.products.produto" .
}
LIMIT 10
```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX attr2: <attribute:>
PREFIX aPIC: <aPICall:>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX aPIR: <aPIResource:>

#SELECT (COUNT(?operation) AS ?count_call) #(COUNT(?resource) AS ?resources) (COUNT(?resource) AS ?attributes)
#SELECT (COUNT(?resource) AS ?resources) (COUNT(?resource) AS ?attributes)
SELECT distinct ?attribute_name
#SELECT distinct ?resource_name ?attribute
WHERE {
    #?api_call rdf:type ns_core:APICall .
    #?api_call aPIC:api_name "ecommerce-carts" .
    #?operation rdf:type ns_core:APIOperation .
    #?operationExecuted rdf:type ns_core:OperationExecuted .
    #?operationExecuted gufo:mediates ?operation .
    #?api_call rdf:type ns_core:APICall .
    #?api_call ^gufo:participedIn ?operation .
    ?resource rdf:type ns_core:APIResource .
    #?operationExecuted gufo:mediates ?resource .
    ?resource aPIR:resource_name ?resource_name .
    ?resource ns_core:resource_data ?attribute .
    #?attribute <attribute:attribute_name> ?attribute_name .
    ?attribute attr2:attribute_name ?attribute_name .
    #?attribute ns_core:attribute_value ?attribute_value .
    #FILTER(?resource_name = "carts" && ?attribute_name = "client.name")
    #FILTER(?attribute_name = "client.name")
    FILTER(?resource_name = "carts")

}
LIMIT 10


```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX aPIC: <aPICall:>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>


SELECT distinct ?api_call ?request_time
WHERE {
    ?api_call a ns_core:APICall .
    ?api_call aPIC:request_time ?request_time.
    ?consummer_app gufo:participatedIn ?api_call .
    ?consummer_app a ns_core:ConsumerApp .
    FILTER(
        IRI(?consummer_app) = <http://eamining.edu.pt/acmeapp>  
        && xsd:dateTime(?request_time) > xsd:dateTime("2024-04-15T12:54:34Z")
    )          
}  
order by ?request_time  
```

```sparql
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX gufo: <http://purl.org/nemo/gufo#>
            PREFIX ns_core: <http://eamining.edu.pt/core#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX aPIC: <aPICall:>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT distinct ?api_call ?request_time
            WHERE {
                ?api_call a ns_core:APICall .
                ?api_call aPIC:request_time ?request_time.
                ?consummer_app gufo:participatedIn ?api_call .
                ?consummer_app a ns_core:ConsumerApp .
                FILTER(
                    IRI(?consummer_app) = <http://eamining.edu.pt/acmeapp>  
                    && xsd:dateTime(?request_time) > '2024-04-15T12:54:34.155000+00:00'^^xsd:dateTime
                    && ?request_time > '2024-04-15T12:54:34.155000+00:00'^^xsd:dateTime
                )          
            }  
            order by ?request_time

            
```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX gufo: <http://purl.org/nemo/gufo#>
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

SELECT DISTINCT ?ftc #?antecedent ?consequent
WHERE {
    ?ftc a ns_process_view:FrequentTemporalCorrelation .
    # ?ftc gufo:mediates ?antecedent .
    # ?antecedent a ns_process_view:APIAntecedentActivity .
    # ?ftc gufo:mediates ?consequent .
    # ?consequent a ns_process_view:APIConsequentActivity .
    # FILTER (
    #     ?antecedent.name  = '1f61314f275fcc690049921bffac9314' && ?consequent = '8815d10cf19f330023b98f4cdb1d695c'
    # )                        
}

LIMIT 10
```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

SELECT ?activity_connection
WHERE {
    ?activity_connection a ns_process_view:APIActivitiesConnection .
}

limit 10


```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT (MAX(xsd:integer(REPLACE(?label, "case_id : ", ""))) AS ?maxValue)
#SELECT distinct (xsd:integer(REPLACE(?label, "case_id : ", "")) as ?case_id)
WHERE {
    ?activity_connection a ns_process_view:APIActivitiesConnection .
    ?activity_connection rdfs:label ?label .
    FILTER(REGEX(?label, "case_id : [0-9]+"))
}
```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX ns_process_view: <http://eamining.edu.pt/process-view#>

SELECT ?activity_connection
WHERE {
    ?activity_connection a ns_process_view:APIActivitiesConnection .
    ?activity_connection rdfs:label ?label .
    #FILTER(REGEX(?label, "partner : (.+)"))
    FILTER(
        ?label = "partner : OpenApp")

}

LIMIT 10
```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX aPIR: <aPIResource:>
PREFIX ns_data_relation_view: <http://eamining.edu.pt/data-relation-view#>

SELECT ?resource
WHERE {
    ?resource a ns_core:APIResource .
    ?resource aPIR:resource_uri ?resource_uri .
    FILTER( 
        #FILTER(REGEX(?label, "case_id : [0-9]+"))
        #?resource_uri = "/sandbox/ecommerce/v1/carts/17/itens"
        REGEX(?resource_uri, "/sandbox/ecommerce/v1/carts/\\d+/itens")
        #REGEX(?resource_uri, "/sandbox/ecommerce/v1/carts/[0-9]+/itens")
    )

}

```

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX ns_core: <http://eamining.edu.pt/core#>
PREFIX aPIR: <aPIResource:>
PREFIX ns_data_relation_view: <http://eamining.edu.pt/data-relation-view#>

SELECT ?resource
WHERE {
    ?resource a ns_core:APIResource .
    ?resource aPIR:resource_uri ?resource_uri .
    FILTER( 
        REGEX(?resource_uri, "/ecommerce/v")
    )

}
```
