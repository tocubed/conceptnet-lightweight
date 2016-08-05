import os.path
from itertools import takewhile
from operator import itemgetter

import numpy as np

DATA_FILENAME = os.path.join(os.path.dirname(__file__), 'data.npz')


class Concept(int):
    """
    Wraps a ConceptNet array index. Used to lookup and return concepts.
    """
    def __new__(cls, idx):
        return super(Concept, cls).__new__(cls, idx)


class ConceptNet:
    """
    Provides access to english-only concepts from ConceptNet5.
    """

    def __init__(self):
        """
        Read and initialize relation, concept, and assertion arrays from disk.
        """
        data = np.load(DATA_FILENAME)
        self.relations = data['relations']
        self.concepts = data['concepts']

        self.assertions = dict()
        for i, relation in enumerate(self.relations):
            edges = data[str(i)]
            self.assertions[relation] = edges[np.lexsort((edges[:, 1], edges[:, 0]))]

            flipped = np.fliplr(edges)
            self.assertions[('!', relation)] = flipped[np.lexsort((flipped[:, 1], flipped[:, 0]))]

    def related(self, relation, concept, inverse=False):
        """
        Find all concepts related to a concept by a relation.

        :param str relation: the relation as a string, sans the implied '/r/'
        :param Concept concept: the concept as an index
        :param bool inverse: whether to use relations in reverse, inward edges vs. outward
        :rtype: list of Concept

        >>> cn = ConceptNet()
        >>> related = cn.related('UsedFor', cn.concept('apple'))
        >>> [cn.string(c) for c in related][:8]
        ['bait_deer', 'bait_trap', 'compute', 'cook', 'create_music', 'dessert', 'eat', 'enjoy_fruit']
        """
        if inverse:
            relation = ('!', relation)

        edges = self.assertions[relation]
        idx = self._binary_search(edges[:, 0], concept)

        result = []
        if idx is not None:
            result = list(map(itemgetter(1), takewhile(lambda e: e[0] == concept, edges[idx:])))
        return result

    def concept(self, string):
        """
        Convert concept from a string to a Concept. Return None if concept does not exist.

        :param str string: the concept as a string, sans the implied '/c/en'
        :rtype: Concept or None

        >>> cn = ConceptNet()
        >>> cn.concept('apple')
        290450
        """
        idx = self._binary_search(self.concepts, string)
        return Concept(idx) if idx is not None else None

    def string(self, concept):
        """
        Convert Concept to a string.

        :param Concept concept: the concept as an index
        :rtype: str

        >>> cn = ConceptNet()
        >>> cn.string(Concept(290450))
        'apple'
        """
        return self.concepts[concept]

    @staticmethod
    def _binary_search(a, value):
        """
        Perform binary search and return left-most index, or None if value is not found.
        """
        i = np.searchsorted(a, value)
        return i if i != len(a) and a[i] == value else None
