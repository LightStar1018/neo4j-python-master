#!/usr/bin/env python

"""Generates authors.csv, authors_rel.csv, coauthors_rel.csv, reviewers_rel.csv"""
import json
import csv
import sys
import random
from utils import getRandList, bfs
from datetime import date
from typing import Dict

dataRoute = '../data/'

# Extra keywords for the database community
dbKeywords = ["data management", "indexing", "data modeling", "big data", "data processing", "data storage", "data querying"]
fpKeywords = ["functional programming", "type theory", "category theory", "lambda calculus"]

# Database conferences
dbConferences = ["EDBT"]
fpJournals = ["ICFP"]

def writeAuthorsCsv(records):
    authorsDict = dict()
    with open(dataRoute + 'authors.csv', 'w', newline='') as csvfile:
        attrs = ['authorId','name', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()

        def addAuthors(authors):
            for author in authors:
                authorId = author['authorId']
                if authorId:
                    if authorId not in authorsDict:
                        authorsDict[authorId] = author

        for record in records:
            addAuthors(record['authors'])
            for citation in record['citations']:
                addAuthors(citation['authors'])

        for (authorId, author) in authorsDict.items():
            row = dict()
            for attr in attrs:
                if attr in author:
                    row[attr] = author[attr]
            writer.writerow(row)

    return list(authorsDict.keys())

def writeAuthorsRelCsv(records):
    with open(dataRoute + 'authors_rel.csv', 'w', newline='') as csvfile:

        attrs = ['authorId','doi']
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()

        for record in records:
            authorId = record['authors'][0]['authorId']
            if authorId:
                writer.writerow({'authorId': authorId, 'doi': record['doi']})

        for record in records:
            for citation in record['citations']:
                if citation['doi']:
                    authorId = citation['authors'][0]['authorId']
                    if authorId:
                        writer.writerow({'authorId': authorId, 'doi': citation['doi']})

# That could be merged with writeAuthorsRelCsv but decoupling is lost.
def writeCoauthorsRelCsv(records):
    with open(dataRoute + 'coauthors_rel.csv', 'w', newline='') as csvfile:

        attrs = ['authorId','doi']
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()

        for record in records:
            for author in record['authors']:
                authorId = author['authorId']
                if authorId:
                    writer.writerow({'authorId': authorId, 'doi': record['doi']})

        for record in records:
            for citation in record['citations']:
                if citation['doi']:
                    for author in citation['authors']:
                        authorId = author['authorId']
                        if authorId:
                            writer.writerow({'authorId': authorId, 'doi': citation['doi']})

def writeReviewersRelCsv(records, authorsId):
    def getExcluded(authors):
        excluded = []
        for author in record['authors']:
            excluded.append(author['authorId'])
        return excluded

    with open(dataRoute + 'reviewers_rel.csv', 'w', newline='') as csvfile:

        attrs = ['authorId','doi']
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()

        dois = []
        for record in records:
            if record['doi']:
                excluded = getExcluded(record['authors'])
                dois.append((record['doi'], excluded))
                for citation in record['citations']:
                    if citation['doi']:
                        excluded = getExcluded(citation['authors'])
                        dois.append((citation['doi'], excluded))

        nAuthors = len(authorsId)
        for (doi, excluded) in dois:
            for i in getRandList(0, nAuthors-1, size=3, excluded=excluded):
                authorId = authorsId[i]
                writer.writerow({'authorId': authorId, 'doi': doi})

def getArticlesFromJSON(records) -> Dict[str, object]:
    articlesDict = dict()

    def addArticles(articles):
        for article in articles:
            if 'doi' in article and article['doi']:
                doi = article['doi']
                if doi not in articlesDict:
                    articlesDict[doi] = article

    addArticles(records)
    for record in records:
        addArticles(record['citations'])

    return articlesDict

def getArticlesGraph(records):
    graph = dict()

    uniqueArticles = set()
    for record in records:
        if 'doi' in record and record['doi']:
            article = record['doi']
            citations = [citation['doi'] for citation in record['citations'] if 'doi' in citation and citation['doi']]
            graph[article] = citations
            for citation in citations:
                uniqueArticles.add(citation)
    for doi in uniqueArticles:
        if doi not in graph:
            graph[doi] = []

    return graph

def writeArticlesCsv(records, datesOfPublication):
    with open(dataRoute + 'articles.csv', 'w', newline='') as csvfile:
        attrs = ['doi','title', 'abstract', 'publication_date']
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()

        articlesDict = getArticlesFromJSON(records)

        for (doi, article) in articlesDict.items():
            row = dict()
            for attr in attrs:
                if attr == 'publication_date':
                    # datesOfPublication only contains the dates of articles published
                    if doi in datesOfPublication:
                        row[attr] = datesOfPublication[doi]
                if attr in article:
                    if article[attr] == None:
                        row[attr] = article[attr]
                    else:
                        row[attr] = article[attr].replace(',', ' ')
            writer.writerow(row)

def writeCitationsCsv(records):
    with open(dataRoute + 'citations_rel.csv', 'w', newline='') as csvfile:
        attrs = ['article_doi','cited_by_doi']
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()
        for record in records:
            if 'doi' in record and record['doi']:
                article = record['doi']
                for citation in record['citations']:
                    if 'doi' in citation and citation['doi']:
                        cited_by = citation['doi']
                        writer.writerow({attrs[0]: article, attrs[1]: cited_by})

def writeKeywordsCsv(records, dbArticles, fpArticles):
    keywords = set(dbKeywords + fpKeywords)

    with open(dataRoute + 'keywords_rel.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['doi', 'keyword'])
        writer.writeheader()
        for record in records:
            doi = record['doi']
            for topic in record['topics']:
                keyword = topic['topic']
                keywords.add(keyword)
                writer.writerow({'doi': doi, 'keyword': keyword})
        # Additional keywords for database community
        for doi in dbArticles:
            [keyword] = random.sample(dbKeywords, 1)
            writer.writerow({'doi': doi, 'keyword': keyword})
        # Additional keywords for fp community
        for doi in fpArticles:
            [keyword] = random.sample(fpKeywords, 1)
            writer.writerow({'doi': doi, 'keyword': keyword})

    with open(dataRoute + 'keywords.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['name'])
        writer.writeheader()
        for keyword in keywords:
            writer.writerow({'name': keyword})

def previousYear(myDate):
    return myDate.replace(year = myDate.year - 1)

cities=None
def getCity():
    global cities
    if cities is None:
        cities = []
        with open(dataRoute + 'cities.json', 'rt') as f:
            datum = json.load(f)
            for record in datum:
                cities.append(record['city'])
    r = random.randint(0, len(cities)-1)
    return cities[r]

def split(xs, chunks):
    """Split a list in n random fragments. Careful, it shuffles the original collection."""
    random.shuffle(xs)
    n = len(xs)//chunks
    for i in range(0, len(xs), n):
        yield xs[i:i + n]

def getPages():
    pageBegin = random.randint(1, 300)
    pageEnd = pageBegin + max(int(random.gauss(15, 5)), 3)
    return (pageBegin, pageEnd)

# def articlesDAG(records, articles):
    # gr = dict()
    # for (k, vs) in enumerate(getArticlesGraph(records)):
        # if k in articles: gr[article] = [v for v in vs if (v in articles)]
    # matrix = []
    # def go(rem):
        # if len(rem) != 0:
            # visited = bfs(graph, rem[0])
            # matrix.append(visited)
            # go([x for x in rem if x not in visited])
    # go(articles)

def writeConferencesJournalsCsv(records):
    # Key: doi, value: date of publication
    datesOfPublication = dict()

    conferencesName = ['International Conference on Software Engineering'
                      , 'IEEE Symposium on Security and Privacy'
                      ] + dbConferences
    nConferences = len(conferencesName)

    journalsNames = ['Proceedings of the IEEE International Conference on Computer Vision'
                    , 'IEEE Transactions on Pattern Analysis and Machine Intelligence'
                    ] + fpJournals
    nJournals = len(journalsNames)

    allDois = list(getArticlesFromJSON(records).keys())
    (articlesForConferences, articlesForJournals) = split(allDois, chunks=2)
    conferenceArticles = dict(zip(conferencesName, split(articlesForConferences, chunks=nConferences)))
    journalArticles = dict(zip(journalsNames, split(articlesForJournals, chunks=nJournals)))

    nEditions = 10 # arbitrary
    nVolumes = 10 # arbitrary

    with open(dataRoute + 'conferences.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['name'])
        writer.writeheader()
        for name in conferencesName:
            writer.writerow({'name': name})

    with open(dataRoute + 'journals.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['name'])
        writer.writeheader()
        for name in journalsNames:
            writer.writerow({'name': name})

    with open(dataRoute + 'conference_edition_rel.csv', 'w', newline='') as csvfile1:
        writer1 = csv.DictWriter(csvfile1, fieldnames=['conference', 'edition'])
        writer1.writeheader()
        with open(dataRoute + 'article_edition_rel.csv', 'w', newline='') as csvfile2:
            writer2 = csv.DictWriter(csvfile2, fieldnames=['article', 'edition'])
            writer2.writeheader()
            with open(dataRoute + 'editions.csv', 'w', newline='') as csvfile3:
                writer3 = csv.DictWriter(csvfile3, fieldnames=['name','date','city'])
                writer3.writeheader()
                for conferenceName in conferencesName:
                    nArticlesPerEdition = int(len(conferenceArticles[conferenceName])//nEditions)
                    today = date.today()
                    for i in range(nEditions):
                        editionName = f'{conferenceName}-{i}'
                        editionDate = previousYear(today)
                        today = editionDate
                        city = getCity()
                        writer1.writerow({'conference': conferenceName, 'edition': editionName})
                        writer3.writerow({'name': editionName,'date': editionDate, 'city': city})
                        start = i*nArticlesPerEdition
                        for j in range(start, start + nArticlesPerEdition - 1):
                            articleDOI = conferenceArticles[conferenceName][j]
                            datesOfPublication[articleDOI] = editionDate
                            writer2.writerow({'article': articleDOI,'edition': editionName})

    with open(dataRoute + 'journal_volume_rel.csv', 'w', newline='') as csvfile1:
        writer1 = csv.DictWriter(csvfile1, fieldnames=['journal', 'volume'])
        writer1.writeheader()
        with open(dataRoute + 'article_volume_rel.csv', 'w', newline='') as csvfile2:
            writer2 = csv.DictWriter(csvfile2, fieldnames=['article', 'volume', 'pageBegin', 'pageEnd'])
            writer2.writeheader()
            with open(dataRoute + 'volumes.csv', 'w', newline='') as csvfile3:
                writer3 = csv.DictWriter(csvfile3, fieldnames=['name','date','volume'])
                writer3.writeheader()
                for journalName in journalsNames:
                    nArticlesPerVolume = int(len(journalArticles[journalName])//nVolumes)
                    today = date.today()
                    for i in range(nVolumes):
                        volume = i
                        volumeName = f'{journalName}-{i}'
                        journalDate = previousYear(today)
                        today = journalDate
                        writer1.writerow({'journal': journalName, 'volume': volumeName})
                        writer3.writerow({'name': volumeName,'date': journalDate, 'volume': volume})
                        start = i*nArticlesPerVolume
                        for j in range(start, start + nArticlesPerVolume - 1):
                            articleDOI = journalArticles[journalName][j]
                            datesOfPublication[articleDOI] = journalDate
                            (pageBegin, pageEnd) = getPages()
                            writer2.writerow({'article': articleDOI,'volume': volumeName, 'pageBegin': pageBegin, 'pageEnd': pageEnd})

    return ( datesOfPublication
           , conferenceArticles[dbConferences[0]]
           , journalArticles[fpJournals[0]]
           )


if __name__=="__main__":
    records = []

    with open(dataRoute + 'all.json', 'rt') as f:
        records = json.load(f)

    # if len(sys.argv) != 2:
        # print("Usage: ./authors.py all/authors/")

    authorsId = writeAuthorsCsv(records)
    writeAuthorsRelCsv(records)
    writeCoauthorsRelCsv(records)
    writeReviewersRelCsv(records, authorsId)
    writeCitationsCsv(records)
    (datesOfPublication, dbArticles, fpArticles) = writeConferencesJournalsCsv(records)
    writeArticlesCsv(records, datesOfPublication)
    writeKeywordsCsv(records, dbArticles, fpArticles)
