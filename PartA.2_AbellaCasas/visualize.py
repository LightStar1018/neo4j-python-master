#!/usr/bin/env python

import pandas as pd

def visualize(f):
    df = pd.read_csv(f, sep=',', header='infer')
    (nrows, ncols) = df.shape
    print(f"""{f}
      shape ({nrows}, {ncols})
      attrs {list(df.columns)}""")

if __name__=="__main__":
    files = [ 'data/authors.csv'
            , 'data/authors_rel.csv'
            , 'data/coauthors_rel.csv'
            , 'data/reviewers_rel.csv'
            , 'data/articles.csv'
            , 'data/citations_rel.csv'
            , 'data/keywords.csv'
            , 'data/keywords_rel.csv'
            , 'data/conferences.csv'
            , 'data/editions.csv'
            , 'data/conference_edition_rel.csv'
            , 'data/article_edition_rel.csv'
            , 'data/journals.csv'
            , 'data/volumes.csv'
            , 'data/journal_volume_rel.csv'
            , 'data/article_volume_rel.csv'
            ]
    [*map(visualize, files)] # lovely python
