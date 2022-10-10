#!/usr/bin/env python

"""
In case retrieveAll.py malfunctions, this script provides a way to remove duplicates from all.json
"""
import json

with open('data/all.json', mode='r') as f:
    records = json.load(f)

uniqueData = []
uniqueDois = []

for record in records:
    doi = record['doi']
    if doi not in uniqueDois:
        uniqueDois.append(doi)
        uniqueData.append(record)

with open('data/all.json', mode='w') as f:
    json.dump(uniqueData, f)
    print('Task completed.')
