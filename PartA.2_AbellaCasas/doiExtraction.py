#!/usr/bin/env python

import json
import re

dois = []
# raw_articles has a bad encoding, utf-8 won't work
with open('../data/raw_articles.csv', newline='', encoding='cp1252') as fd:
    lines = fd.readlines()
    pattern = re.compile('.*https://doi.org/([^\"]+)')
    i = 0
    for line in lines:
        if i > 1000:
            break
        try:
            dois.append(re.match(pattern, line).group(1))
            i += 1
        except Exception as e:
            pass

with open('../data/dois.json', 'w', newline='') as f:
    json.dump({'dois': dois}, f)
