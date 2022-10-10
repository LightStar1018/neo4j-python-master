# Graph Data Models

Statement [here](./statement.pdf)

## The database

We have prepared a folder `data/` with the data already processed since generating the data (`partA2` and `partA3`) is quite time consuming.

## Neo4j

We prepared a `docker-compose` file to start a `neo4j` docker image with the appropiate folders and ports. Run `docker-compose up` in the root of this project.

## Loading the data

```bash
# Copy data to the import folder of neo4j
NEO4J_IMPORT=~/neo4j/import
cp -r data $NEO4J_IMPORT && mv -f $NEO4J_IMPORT/data/* $NEO4J_IMPORT && rm -r $NEO4J_IMPORT/data

# Run the load script
cd partA2
pipenv shell
./loadNeo4j.py

cd partA3
pipenv shell
./alterGraph.py
```

### Authentication

> If you are using the provided docker-compose you can skip this section you can skip this section.

The easiest way to change the authentication parameters of the scripts for your `neo4j` instance is to define the following environment variables:

- `NEO4J_USER` (default: neo4j)
- `NEO4J_PASSWORD` (default: 1234)
- `NEO4J_DATABASE` (default: "")
- `NEO4J_URI` (default: bolt://localhost:7687)

Alternatively, you can modify this part on each script.
