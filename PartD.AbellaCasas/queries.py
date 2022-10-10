#!/usr/bin/env python

from json import dumps
from neo4j import GraphDatabase, basic_auth
import os

class Community():
    def __init__(self, name, keywords):
        self.name = name
        self.keywords = keywords

def query1(tx, community):
    """Defines a community in the graph"""
    q = """MERGE (comm: Community{name: $name})
           WITH comm
           MATCH (kw: Keyword)
           WHERE kw.keyword in $keywords
           MERGE (comm)-[:Related]-(kw)"""
    result = tx.run(q, {'name': community.name, 'keywords': community.keywords})
    info = result.consume()
    nNodes = info.counters.nodes_created
    nRel = info.counters.relationships_created
    print(f'{community.name} created:\n\t{nNodes} nodes\n\t{nRel} relationships')
    print('')

def query2(tx, community):
    """Checks if a conference belongs to the given keywords community"""
    q = """MATCH (n)-[:Holds|Publishes]-()-[:Present|Features]-(art:Article)
           OPTIONAL MATCH (art:Article)-[:Has]-(kw: Keyword)
           WITH n, count(distinct art) as total, sum(CASE WHEN kw.keyword in $keywords THEN 1 ELSE 0 END) as subtotal
           WHERE subtotal/total >= 0.9
           MATCH (comm: Community{name: $name})
           MERGE (n)-[:Belongs]-(comm)
           RETURN n.name as name
        """
    result = tx.run(q, {'name': community.name, 'keywords': community.keywords})
    print(f'Community: {community.name}')
    for record in result:
        print(record['name'])
    print('')


def createProjectionQuery3(tx,communityName):
    result = tx.run(f"CALL gds.graph.exists('commCalc') YIELD exists;")
    record = result.single()
    doesExist = record.value()
    if doesExist:
        result = tx.run(f"CALL gds.graph.drop('commCalc');")
    res=tx.run("CALL gds.graph.create.cypher('commCalc',"
           "\"MATCH (c:Community {name: '"+communityName+"'})-[:Belongs]-()-[]-()-[]-(art:Article) RETURN id(art) as id\","
           "\"MATCH ((c:Community {name: '"+communityName+"'})-[:Belongs]-()-[]-()-[]-(art:Article)) MATCH (art)-[:Citation]->(art2:Article)-[]-()-[]-()-[:Belongs]-(c) RETURN id(art) as source, id(art2) as target\") "
        "YIELD graphName, nodeCount, relationshipCount, createMillis")
    for line in res:
        print("Cypher projection has " +str(line["nodeCount"])+" nodes and "+str(line["relationshipCount"])+ " relationships")
    print(f'Graph commCalc created.')

    res=tx.run("CALL gds.pageRank.stream('commCalc') YIELD nodeId, score RETURN gds.util.asNode(nodeId).doi AS doi,score ORDER BY score DESC LIMIT 100;")
    doiList=[]
    for line in res:
        doiList.append(line["doi"])
    tx.run(" MATCH (art:Article) WHERE art.doi IN $doiList"
           " MATCH (comm:Community {name: $commName})"
           " MERGE (art)-[:Top100]-(comm)",doiList=doiList,commName=communityName)

def query4(tx):
    """Gets review candidates and gurus"""
    result = tx.run("MATCH (aut:Author)-[:Coauthor]-(art:Article)-[:Top100]-(c:Community)"
                    "WITH aut,c,count(art) AS articles "
                    "MERGE (aut)-[:ReviewCandidate]-(c) "
                    "WITH aut,c,articles "
                    "WHERE articles>1 "
                    "MERGE (aut)-[:ReviewGuru]-(c) ")
    info = result.consume()
    nNodes = info.counters.nodes_created
    nRel = info.counters.relationships_created
    print(f'ReviewCandidate and ReviewGuru created:\n\t{nNodes} nodes\n\t{nRel} relationships')
    print('')

def main():
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "1234")
    database = os.getenv("NEO4J_DATABASE", "") # default
    url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(url, auth=basic_auth(username, password))

    dbCommunity = Community('database', ["data management", "indexing", "data modeling", "big data", "data processing", "data storage", "data querying"])
    fpCommunity = Community('functional programming', ["functional programming", "type theory", "category theory", "lambda calculus"])
    communities=['database','functional programming']
    with driver.session(database=database) as session:
        for community in [dbCommunity, fpCommunity]:
            session.write_transaction(query1, community)
            session.write_transaction(query2, community)
        for community in communities:
            session.write_transaction(createProjectionQuery3,community)
        session.write_transaction(query4)

if __name__ == '__main__':
    main()
