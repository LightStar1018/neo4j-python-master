#!/usr/bin/env python

from json import dumps
from neo4j import GraphDatabase, basic_auth
import os

def deleteAll(tx):
    tx.run("""MATCH (n) DETACH DELETE (n)""")
    print('Deleted all nodes and relationships')

def createIndex(tx, node, pk):
    result = tx.run(f"CREATE INDEX IF NOT EXISTS FOR (n: {node}) ON (n.{pk})")
    info = result.consume()
    nIndexes = info.counters.indexes_added
    print(f'{nIndexes} new indexes added')

def create(filename, query):
    def f(tx):
        result = tx.run(query)
        info = result.consume()
        nNodes = info.counters.nodes_created
        nRel = info.counters.relationships_created
        print(f'{filename} created:\n\t{nNodes} nodes\n\t{nRel} relationships')
    return f

##########################
#### Concepts Queries ####
##########################

def authorsQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "CREATE (:Author{pid: line.authorId, name: line.name})"
           )

def articlesQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
               "FIELDTERMINATOR ','\n"
               "CREATE (:Article{doi: line.doi, title: line.title, abstract: line.abstract, date: date(line.publication_date)})"
            )

def keywordsQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
               "FIELDTERMINATOR ','\n"
               "CREATE (:Keyword{keyword: line.name})"
            )

def conferencesQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
               "FIELDTERMINATOR ','\n"
               "CREATE (:Conference{name: line.name})"
            )

def editionsQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
               "FIELDTERMINATOR ','\n"
               "CREATE (:Edition{name: line.name, date: date(line.date), city: line.city})"
            )

def journalsQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
               "FIELDTERMINATOR ','\n"
               "CREATE (:Journal{name: line.name})"
            )

def volumesQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
               "FIELDTERMINATOR ','\n"
               "CREATE (:Volume{name: line.name, date: date(line.date), volume: line.volume})"
            )

###############################
#### Relationships Queries ####
###############################

def authorsRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (article:Article{doi: line.doi})"
              "MATCH (author:Author{pid: line.authorId})"
              "MERGE (author)-[:Author]-(article)"
            )

def coauthorsRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (article:Article{doi: line.doi})"
              "MATCH (author:Author{pid: line.authorId})"
              "MERGE (author)-[:Coauthor]-(article)"
            )

def reviewersRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (article:Article{doi: line.doi})"
              "MATCH (author:Author{pid: line.authorId})"
              "MERGE (author)-[:Reviewer]-(article)"
            )

def citationsRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (origin:Article{doi: line.cited_by_doi})\n"
              "MATCH (dest:Article{doi: line.article_doi})\n"
              "WHERE origin.date <= dest.date\n"
              "MERGE (origin)-[:Citation]->(dest)"
            )

def keywordsRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (article:Article{doi: line.doi})"
              "MATCH (keyword:Keyword{keyword: line.keyword})"
              "MERGE (article)-[:Has]-(keyword)"
            )

def conferenceEditionRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (conf:Conference{name: line.conference})"
              "MATCH (edition:Edition{name: line.edition})"
              "MERGE (conf)-[:Holds]->(edition)"
            )

def articleEditionRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (edition:Edition{name: line.edition})"
              "MATCH (article:Article{doi: line.article})"
              "MERGE (edition)-[:Present]-(article)"
            )

def journalVolumeRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (journal:Journal{name: line.journal})"
              "MATCH (volume:Volume{name: line.volume})"
              "MERGE (journal)-[:Publishes]->(volume)"
            )

def volumeArticleRelQuery(filename):
    return ( f"LOAD CSV WITH HEADERS FROM \'file:///{filename}\' AS line\n"
              "FIELDTERMINATOR ','\n"
              "MATCH (volume:Volume{name: line.volume})"
              "MATCH (article:Article{doi: line.article})"
              "MERGE (volume)-[:Features{pageBegin: toInteger(line.pageBegin), pageEnd: toInteger(line.pageEnd)}]->(article)"
            )

#############################################

def main():
    username = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "1234")
    database = os.getenv("NEO4J_DATABASE", "") # default
    url = os.getenv("NEO4J_URI", "bolt://localhost:7687")

    driver = GraphDatabase.driver(url, auth=basic_auth(username, password))

    with driver.session(database=database) as session:
        nodeQueries = [ ('authors.csv', authorsQuery)
                      , ('articles.csv', articlesQuery)
                      , ('keywords.csv', keywordsQuery)
                      , ('conferences.csv', conferencesQuery)
                      , ('editions.csv', editionsQuery)
                      , ('journals.csv', journalsQuery)
                      , ('volumes.csv', volumesQuery)
                      ]

        relQueries = [ ('authors_rel.csv', authorsRelQuery)
                     , ('coauthors_rel.csv', coauthorsRelQuery)
                     , ('reviewers_rel.csv', reviewersRelQuery)
                     , ('citations_rel.csv', citationsRelQuery)
                     , ('keywords_rel.csv', keywordsRelQuery)
                     , ('conference_edition_rel.csv', conferenceEditionRelQuery)
                     , ('article_edition_rel.csv', articleEditionRelQuery)
                     , ('journal_volume_rel.csv', journalVolumeRelQuery)
                     , ('article_volume_rel.csv', volumeArticleRelQuery)
                     ]

        session.write_transaction(deleteAll)

        for (filename, getQuery) in nodeQueries:
            createQuery = create(filename, getQuery(filename))
            session.write_transaction(createQuery)

        session.write_transaction(createIndex, 'Author','pid')
        session.write_transaction(createIndex, 'Article','doi')
        session.write_transaction(createIndex, 'Keyword','keyword')
        session.write_transaction(createIndex, 'Conference','name')
        session.write_transaction(createIndex, 'Journal','name')
        session.write_transaction(createIndex, 'Edition','name')
        session.write_transaction(createIndex, 'Volume','name')
        # Performance wise
        session.write_transaction(createIndex, 'Article','date')
        session.write_transaction(createIndex, 'Volume','date')

        for (filename, getQuery) in relQueries:
            createQuery = create(filename, getQuery(filename))
            session.write_transaction(createQuery)

if __name__ == '__main__':
    main()
