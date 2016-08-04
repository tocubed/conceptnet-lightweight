import os.path

import numpy as np
import pandas as pd

RELATIONS_FILEPATH = os.path.join(os.path.dirname(__file__), 'relations')
CONCEPTS_FILEPATH = os.path.join(os.path.dirname(__file__), 'concepts')
ASSERTIONS_FILEPATH = os.path.join(os.path.dirname(__file__), 'assertions/')


class Concept(int):
    def __new__(cls, idx):
        return super(Concept, cls).__new__(cls, idx)


class ConceptNet:

    def __init__(self):
        self.relations = pd.read_csv(RELATIONS_FILEPATH, squeeze=True, dtype=np.object, header=None).values
        self.concepts = pd.read_csv(CONCEPTS_FILEPATH, squeeze=True, dtype=np.object, header=None).values

        self.assertions = dict()
        for i, relation in enumerate(self.relations):
            self.assertions[relation] = pd.read_csv(ASSERTIONS_FILEPATH + str(i), delimiter=' ', dtype=np.uint32, header=None).values

            flipped = np.fliplr(self.assertions[relation])
            self.assertions[('!', relation)] = flipped[np.lexsort((flipped[:, 1], flipped[:, 0]))]

    def related(self, relation, concept, inverse=False):
        if inverse:
            relation = ('!', relation)

        edges = self.assertions[relation]
        idx = self._binary_search(edges[:, 0], concept)

        result = []
        if idx is not None:
            # start = idx    #end = (increment idx while ...) # TODO simplify this loop
            while idx < len(edges) and edges[idx][0] == concept:
                result.append(edges[idx][1])
                idx += 1
        return result

    def concept(self, name):
        idx = self._binary_search(self.concepts, name)
        return Concept(idx) if idx is not None else None

    def name(self, concept):
        return self.concepts[concept]

    @staticmethod
    def _binary_search(a, x):
        i = np.searchsorted(a, x)
        return i if i != len(a) and a[i] == x else None


if __name__ == '__main__':
    cn = ConceptNet()

    cpt = input()
    while cpt != 'Q':
        cpt = input()
        print(cpt, cn.concept(cpt))
        for related in cn.related('Antonym', cn.concept(cpt), inverse=True):
            print("(!, Antonym)", cpt, cn.name(related))
