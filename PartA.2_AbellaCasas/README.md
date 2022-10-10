# HOW TO

1. Run `python doiExtraction.py` in order to extract all DOIs from `data/raw_articles.csv`.
2. Run `retrieveAll.py` to query Semantic Scholar and retrieve information from those raw articles. This process is slow (~ 1 hour) since Semantic Scholar limits the number of queries per minute. This generates `data/all.json`.
3. Run `recordsToCsv.py` to transform `data/all.json` to all the CSVs that are needed in step 4.
4. Make sure you have read README.md and followed the steps from Loading the data.
5. Run `loadNeo4j.py` to load all the CSVs in `data/` (this step will not work until you have moved the `data/` folder into the `~/neo4j/import` folder).
