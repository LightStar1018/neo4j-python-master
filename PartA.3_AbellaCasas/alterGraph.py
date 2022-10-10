#!/usr/bin/env python

from neo4j import GraphDatabase, basic_auth
import os


def create(filename, query):
    def f(tx):
        result = tx.run(query)
        info = result.consume()
        nNodes = info.counters.nodes_created
        nRel = info.counters.relationships_created
        print(f'{filename} created:\n\t{nNodes} nodes\n\t{nRel} relationships')
    return f

def reviewQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (art:Article{doi:line.doi})-[rev:Reviewer]-(aut:Author{pid:line.authorId})"
              "DELETE rev "
              "MERGE (art)-[:Reviewed]-(newRev:Review{decision:line.decision,content:line.content})-[:Reviewer]-(aut)"
           )


def organizationQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "CREATE (org:Organization{name:line.organization,type:line.type})"
           )

def organizationRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (aut:Author{pid:line.authorId}), (org:Organization{name:line.organization})"
              "MERGE (aut)-[:Belongs]-(org)"
           )
def main():
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "1234")
    database = os.getenv("NEO4J_DATABASE", "") # default
    url = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    driver = GraphDatabase.driver(url, auth=basic_auth(username, password))
    with driver.session(database=database) as session:
        createQuery = create('newReview_rel.csv',reviewQuery("newReview_rel.csv") )
        session.write_transaction(createQuery)
        createQuery = create('organization.csv',organizationQuery("organization.csv") )
        session.write_transaction(createQuery)
        createQuery = create('organization_rel.csv',organizationRelQuery("organization_rel.csv") )
        session.write_transaction(createQuery)

if __name__ == '__main__':
    main()
