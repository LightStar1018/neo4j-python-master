import random
import json
import csv

dataPath = '../data/'

def writeOrganizationRelCsv():
    with open(dataPath + 'organization_rel.csv', 'w', newline='') as csvfile:
        organizations=["UPC","UB","CNL","OD"]
        attrs = ['authorId','organization','type']
        type=["University","University","Company","Company"]
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()
        with open('data/authors.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                org=random.randrange(3)
                writer.writerow({'authorId': row['authorId'], 'organization': organizations[org],'type':type[org]})

def writeOrganizationCsv():
    with open(dataPath + 'organization.csv', 'w', newline='') as csvfile:
        organizations=["UPC","UB","CNL","OD"]
        attrs = ['organization','type']
        type=["University","University","Company","Company"]
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()
        writer.writerow({'organization': organizations[0],'type':type[0]})
        writer.writerow({'organization': organizations[1],'type':type[1]})
        writer.writerow({'organization': organizations[2],'type':type[2]})
        writer.writerow({'organization': organizations[3],'type':type[3]})


def writeReviewRelCsv():
    with open(dataPath + 'newReview_rel.csv', 'w', newline='') as csvfile:
        attrs = ['authorId','doi','decision','content']
        writer = csv.DictWriter(csvfile, fieldnames=attrs)
        writer.writeheader()
        decision=["Accepted","Rejected","Accepted"]
        content=["Happy Lorem Ipsum","Angry Lorem Ipsum","Mild Lorem Ipsum"]
        with open(dataPath + 'reviewers_rel.csv', newline='') as csvfile:
            counter=0
            reader = csv.DictReader(csvfile)
            for row in reader:
                writer.writerow({'authorId': row['authorId'],'doi':row['doi'],'decision':decision[counter],'content':content[counter]})
                counter = (counter+1)%3



if __name__=="__main__":
    records = []
    type=["University","University","Company","Company"]

    # if len(sys.argv) != 2:
        # print("Usage: ./authors.py all/authors/")
    writeOrganizationCsv()
    writeOrganizationRelCsv()
    writeReviewRelCsv()
