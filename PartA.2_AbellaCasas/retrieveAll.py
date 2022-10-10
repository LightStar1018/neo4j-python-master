#!/usr/bin/env python

from os.path import exists
import json
from json import JSONDecodeError
import requests
import sys
import time
import math


data = []
doiFP = 'data/dois.json'
destFP = 'data/all.json'

# Be careful not to interrupt while saving the data since open(,w) truncates the file
def saveData(newData):
    global data
    with open(destFP, 'w') as f:
        data = data + newData
        print('Saving work...', end='')
        json.dump(data, f)
        print('saved!')

def sleep(seconds = (60*5)):
    print(f'Sleeping for {seconds} seconds')
    sleepInterval = 15
    for i in range(math.ceil(seconds/sleepInterval)):
        time.sleep(sleepInterval)
        print(f'{seconds-((i+1)*sleepInterval)} seconds remaining...')

def main():
    global data
    try:
        with open(destFP) as f:
            data = json.load(f)
    except FileNotFoundError:
        pass
    except JSONDecodeError:
        pass

    alreadyProcessedDois = []
    for article in data:
        alreadyProcessedDois.append(article['doi'])

    todoDois = []
    with open(doiFP) as f:
        allDois = json.load(f)['dois']
        todoDois = list(set(allDois) - set(alreadyProcessedDois))

    print(f'{len(todoDois)} elements to process')
    if todoDois:
        i = 0
        newData = []
        for index, doi in enumerate(todoDois):
            try:
                r = requests.get('https://api.semanticscholar.org/v1/paper/' + doi)
                if int(r.status_code/100) == 2:
                    print(f'doi {doi} successfully retrieved.')
                    newData.append(r.json())
                    i += 1
                    if i == 5 or i >= len(todoDois):
                        saveData(newData)
                        newData = []
                        i = 0
                elif r.status_code == 403 or r.status_code == requests.codes['too_many_requests']:
                    # Semantic scholar is returning 403 instead of 429 :-)
                    print('Too many requests')
                    saveData(newData)
                    newData = []
                    i = 0
                    rem = len(todoDois) - index
                    print(f'{rem} elements to finish...')
                    sleep(60*5)
                else:
                    print(f'Unexpected status code: {r.status_code}')
                    sys.exit(-1)
            except KeyboardInterrupt:
                    saveData(newData)
                    break
            except Exception as e:
                pass

    print("All doi from dois.json are processed")

if __name__=="__main__":
    main()
