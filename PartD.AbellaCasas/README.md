#HOW TO

This script requires the A2 script to be run to completion, as it makes use of data it loads into the database, A3 is not needed due to not using any of the data it adds, nor the new graph morphology affecting the queries

1. Modify the credentials present in `queries.py`, as seen in the following lines to match your database's credentials:

```python
username = os.getenv("NEO4J_USER", user) #user
password = os.getenv("NEO4J_PASSWORD", password) #password
database = os.getenv("NEO4J_DATABASE", databaseName) # database name
```

2. Run `queries.py` to run all queries that composes section D. The queries are executed in order and each one prints some information of returned by the query. For more details, see `queries.py`.
