import os.path
import shutil
from urllib.request import urlopen

import numpy as np
import pandas as pd

CONCEPTNET_DOWNLOAD_URL = 'http://conceptnet5.media.mit.edu/downloads/current/conceptnet5_flat_csv_5.4.tar.bz2'


def download():
    """
    Download the CSV archive from the ConceptNet site.
    """
    req = urlopen(CONCEPTNET_DOWNLOAD_URL)
    with open('data.tar.bz2', 'wb') as file:
        shutil.copyfileobj(req, file)


def extract():
    """
    Extract english-only assertions from ConceptNet5, sans metadata, and save them as compressed numpy arrays.
    """
    def assertions_filter(df):
        relations_only = df[1].str.startswith('/r/')
        english_only = df[2].str.startswith('/c/en/') & df[3].str.startswith('/c/en/')

        concepts_only = (df[2] != '/c/en/') & (df[3] != '/c/en/')

        return relations_only & english_only & concepts_only

    assertions = pd.DataFrame()
    for file in ASSERTION_FILES:
        df_iter = pd.read_csv(file, delimiter='\t', usecols=[1, 2, 3], header=None, iterator=True, chunksize=2 ** 16)
        assertions = pd.concat([assertions] + [chunk[assertions_filter(chunk)] for chunk in df_iter])

    relations = np.sort(assertions[1].unique())
    concepts = np.unique(np.concatenate((assertions[2].unique(), assertions[3].unique())))

    relations_idx = {relation: idx for idx, relation in enumerate(relations)}
    concepts_idx = {concept: idx for idx, concept in enumerate(concepts)}

    assertions[1] = assertions[1].apply(lambda r: relations_idx[r])
    assertions[[2, 3]] = assertions[[2, 3]].applymap(lambda c: concepts_idx[c])

    relation_edges = {str(relation): group[[2, 3]] for relation, edges in assertions.groupby(1)}
    np.savez_compressed('data.npz', relations=relations, concepts=concepts, **relation_edges)


def main():
    if not os.path.isfile('data.tar.bz2'):
        download()

    extract()


if __name__ == '__main__':
    main()