#!/usr/bin/env python

from json import dumps
from neo4j import GraphDatabase, basic_auth
import os

def createGraphGDS(tx, graphName):
    result = tx.run(f"CALL gds.graph.exists('{graphName}') YIELD exists;")
    record = result.single()
    doesExist = record.value()
    if not doesExist:
        tx.run(f"CALL gds.graph.create('{graphName}', 'Article', 'Citation')")
        print(f'Graph {graphName} created.')
    else:
        print(f'Graph {graphName} already exist.')

def pageRankQuery(tx, graphName, limit = 10):
    q = f"""CALL gds.pageRank.stream('{graphName}')
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).title AS name, score
            ORDER BY score DESC, name ASC
            LIMIT {limit}"""
    result = tx.run(q)
    print('======== Page Rank =========')
    for line in result:
        title = line['name']
        score = line['score']
        print(f'{title} - {score}')

def main():
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "1234")
    database = os.getenv("NEO4J_DATABASE", "") # default
    url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(url, auth=basic_auth(username, password))

    graphName = 'art-cit-graph'

    with driver.session(database=database) as session:
        session.read_transaction(createGraphGDS, graphName)
        session.write_transaction(pageRankQuery, graphName)

if __name__ == '__main__':
    main()
