#!/usr/bin/env python

from neo4j import GraphDatabase, basic_auth
import os



def query1(tx):
    result = tx.run(f" MATCH ((conf:Conference)-[:Holds]-(edi:Edition)-[:Present]-(art:Article)-[cit:Citation]->(art2:Article)) \n"
             "WITH conf,art,count(cit) as citations ORDER BY conf, count(cit) DESC \n"
             "WITH conf, collect([art,citations]) AS toCut UNWIND toCut[0..3] AS cut RETURN conf,cut[0],cut[1];")
    res=[]
    for line in result:
        res.append((line["conf"],line["cut[0]"],line["cut[1]"]))
    return res

def query2(tx):
    result = tx.run(f"MATCH ((conf:Conference)-[:Holds]-(ed:Edition)-[:Present]-(Art:Article)-[:Coauthor]-(aut:Author)) "
                    f"WITH conf,aut,count(DISTINCT ed) as numEds "
                    f"WHERE numEds>3  "
                    f"RETURN conf,aut;")
    res=[]
    for line in result:
        res.append((line["conf"],line["aut"]))
    return res

def query3(tx,year):
    result = tx.run(f"MATCH ((jor:Journal)-[pub:Publishes]-(vol:Volume)-[:Features]-(art:Article)) "
                    f"OPTIONAL MATCH ((art:Article)-[cit:Citation]->(cited:Article)) "
                    f"WHERE vol.date.year>($year-3) AND vol.date.year<$year AND cited.date.year=$year "
                    f"WITH count(cited) AS cited, count(art) as publications, jor "
                    f"RETURN (cited*1.0) / (publications*1.0) AS IF,jor,$year AS year, cited, publications",year=year)
    res=[]
    for line in result:
        res.append((line["IF"],line["jor"],line["year"]))
    return res



# That is a query 4 where the hindex is obtained in the query itself, this is very inefficient and would only be good if network costs were REALLY high
#MATCH ((aut:Author)-[:Author]-(art:Article)) OPTIONAL MATCH ((art:Article)-[cit:Citation]-(art2:Article)) WITH aut, art, count(cit) as citations ORDER BY aut, citations DESC WITH aut,range(1,count(art)) as articles,collect(citations) AS citations UNWIND articles as articleNum WITH aut,articleNum,citations WHERE articleNum<=citations[articleNum-1] OR (articleNum=1 AND citations[0]=0) RETURN aut,sum(CASE WHEN citations[articleNum-1]<>0 THEN 1 ELSE 0 END) as hindex

def query4(tx):
    result = tx.run(f"MATCH ((aut:Author)-[:Coauthor]-(art:Article)) "
                    f"OPTIONAL MATCH ((art:Article)-[cit:Citation]->(art2:Article)) "
                    f"WITH aut, art, count(cit) as citation "
                    f"ORDER BY aut, citation DESC "
                    f"WITH aut,COLLECT(citation) AS citations "
                    f"RETURN aut,citations")
    res=[]
    for line in result:
        counter=0
        for val in line["citations"]:
            if counter<=val:
                counter+=1
            else:
                break
        res.append((line["aut"],counter))
    return res

def main():
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "1234")
    database = os.getenv("NEO4J_DATABASE", "") # default
    url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(url, auth=basic_auth(username, password))
    with driver.session(database=database) as session:
        result=session.read_transaction(query1)
        print(len(result))
        result=session.read_transaction(query2)
        print(len(result))
        result=session.read_transaction(query3,2020)
        print(len(result))
        result=session.read_transaction(query4)
        print(len(result))


if __name__ == '__main__':
    main()
