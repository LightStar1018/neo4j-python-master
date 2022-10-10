#HOW TO

This script requires the A2 script to be run to completion, as it makes use of the generated CSVs and data it loads into the database.

1.Run "createNewCSVs.py" to generate the new data to load and alter the database graph.

2.Move the new generated CSVs ("newReview_rel.csv","organization.csv","organization_rel.csv") into the $NEO4J_HOME/import folder, so that it can be accessed by the neo4j database.

3.Modify the credentials present in "alterGraph.py", as seen in the following lines to match your database's credentials:

```python
username = os.getenv("NEO4J_USER", user) #user
password = os.getenv("NEO4J_PASSWORD", password) #password
database = os.getenv("NEO4J_DATABASE", databaseName) # database name
```

4.Run "alterGraph.py" to alter and add new data to the database
