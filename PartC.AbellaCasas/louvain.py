#!/usr/bin/env python

from json import dumps
from neo4j import GraphDatabase, basic_auth
import os

def createGraphGDS(tx, graphName):
    result = tx.run(f"CALL gds.graph.exists('{graphName}') YIELD exists;")
    record = result.single()
    doesExist = record.value()
    if not doesExist:
        tx.run(f"CALL gds.graph.create('{graphName}', 'Article', {{Citation: {{orientation: 'UNDIRECTED'}} }})")
        print(f'Graph {graphName} created.')
    else:
        print(f'Graph {graphName} already exist.')

def louvainQuery(tx, graphName):
    q = f"""CALL gds.louvain.stream('{graphName}')
            YIELD nodeId, communityId
            RETURN gds.util.asNode(nodeId).title AS title, communityId
            ORDER BY communityId ASC"""
    result = tx.run(q)
    print('======== Louvain: communities =========')
    communities = dict()
    for line in result:
        communityId = line['communityId']
        title = line['title']
        if communityId not in communities:
            communities[communityId] = [title]
        else:
            communities[communityId].append(title)

    for communityId in sorted(communities, key=lambda k: len(communities[k]), reverse=True)[:10]:
        titles = communities[communityId]
        print(f'Community {communityId} (size: {len(title)})')
        for title in titles[:3]:
            print(f'\tTitle: {title}')
        print(f'--------------------------')

def main():
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "1234")
    database = os.getenv("NEO4J_DATABASE", "") # default
    url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(url, auth=basic_auth(username, password))

    graphName = 'art-cit-undir-graph'

    with driver.session(database=database) as session:
        session.read_transaction(createGraphGDS, graphName)
        session.write_transaction(louvainQuery, graphName)

if __name__ == '__main__':
    main()
