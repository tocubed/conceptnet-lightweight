import numpy as np
import pandas as pd

ASSERTION_FILES = ["data/assertions/part_0" + str(n) + ".csv" for n in range(8)]


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


extract()
