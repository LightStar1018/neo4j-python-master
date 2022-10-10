#HOW TO

This script requires the A2 script to be run to completion, as it makes use of data it loads into the database, A3 is not needed due to not using any of the data it adds, nor the new graph morphology affecting the queries

1. Modify the credentials present in `queries.py`, as seen in the following lines to match your database's credentials:

```python
username = os.getenv("NEO4J_USER", user) #user
password = os.getenv("NEO4J_PASSWORD", password) #password
database = os.getenv("NEO4J_DATABASE", databaseName) # database name
```

2. Run `queries.py` to execute the queries, to avoid spamming the console, the print output is limited and only displays the numbers of rows found, to obtain more information, the len() function can be removed from the print
