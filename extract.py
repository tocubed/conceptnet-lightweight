"""
This script will extract english-only assertions from ConceptNet5, and save them as numpy arrays.
An archive will be downloaded if data.tar.bz2 does not already exist.
"""

import os.path
import shutil
import tarfile
from urllib.request import urlopen

import numpy as np
import pandas as pd

CONCEPTNET_DOWNLOAD_URL = 'http://conceptnet5.media.mit.edu/downloads/current/conceptnet5_flat_csv_5.4.tar.bz2'


def download():
    """
    Download the CSV archive from the ConceptNet site.
    """
    print("Downloading...")

    req = urlopen(CONCEPTNET_DOWNLOAD_URL)
    with open('data.tar.bz2', 'wb') as file:
        shutil.copyfileobj(req, file)


def extract():
    """
    Load english-only assertions from ConceptNet5, removing metadata, and save them as compressed numpy arrays.
    """
    print("Extracting...")

    def filter_relations(relation):
        if relation.startswith('/r/'):
            return relation[3:]  # remove '/r/' prefix
        else:
            return None

    def filter_concepts(concept):
        if concept.startswith('/c/en/') and concept != '/c/en/':
            return concept[6:]  # remove '/c/en/' prefix
        else:
            return None

    # read data from disk and filter
    assertions = []
    with tarfile.open('data.tar.bz2', 'r:bz2') as tar:
        for part in tar:
            print("Extracting part file...")

            part = tar.extractfile(part)
            part = pd.read_csv(part, delimiter='\t', usecols=[1, 2, 3], dtype=np.object, header=None,
                               converters={1: filter_relations, 2: filter_concepts, 3: filter_concepts},
                               na_filter=False)

            part.dropna(inplace=True)
            assertions.append(part)

            del part

    assertions = pd.concat(assertions)

    print("Assembling numpy arrays...")

    relations = np.sort(assertions[1].unique())
    concepts = np.unique(np.concatenate((assertions[2].unique(), assertions[3].unique())))

    # convert array of strings to array of indices
    relations_idx = {relation: idx for idx, relation in enumerate(relations)}
    concepts_idx = {concept: idx for idx, concept in enumerate(concepts)}

    assertions[1] = assertions[1].apply(lambda r: relations_idx[r])
    assertions[[2, 3]] = assertions[[2, 3]].applymap(lambda c: concepts_idx[c])

    # split into arrays by relation
    relation_edges = {str(relation): edges[[2, 3]] for relation, edges in assertions.groupby(1)}

    print("Saving numpy arrays...")

    np.savez_compressed('data.npz', relations=relations, concepts=concepts, **relation_edges)

    print("Done!")


def main():
    if not os.path.isfile('data.tar.bz2'):
        download()

    extract()


if __name__ == '__main__':
    main()
