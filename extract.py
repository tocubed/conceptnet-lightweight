from collections import defaultdict


def _is_wanted_assertion(relation, concept_origin, concept_target):
    relation_marker = '/r/'
    english_concept_marker = '/c/en/'
    return relation.startswith(relation_marker) and concept_origin.startswith(english_concept_marker) and concept_target.startswith(english_concept_marker) \
        and len(concept_origin) > len(english_concept_marker) and len(concept_target) > len(english_concept_marker)


def _strip_markers(relation, concept_origin, concept_target):
    return relation[3:], concept_origin[6:], concept_target[6:]


def get_assertions():
    assertion_files = ["data/assertions/part_0" + str(n) + ".csv" for n in range(8)]

    for file in assertion_files:
        with open(file, encoding='utf-8') as assertions:
            for assertion in assertions:
                relation, concept_origin, concept_target = assertion.split('\t')[1:4]
                if _is_wanted_assertion(relation, concept_origin, concept_target):
                    yield _strip_markers(relation, concept_origin, concept_target)


if __name__ == '__main__':
    relations = set()
    concepts = set()
    for relation, concept_origin, concept_target in get_assertions():
        relations.add(relation)
        concepts.add(concept_origin)
        concepts.add(concept_target)

    relations = sorted(list(relations))
    concepts = sorted(list(concepts))

    with open("relations", mode='w+', encoding='utf-8') as relations_file:
        relations_file.writelines(map(lambda s: s + '\n', relations))

    with open("concepts", mode='w+', encoding='utf-8') as concepts_file:
        concepts_file.writelines(map(lambda s: s + '\n', concepts))

    relation_to_i = {relation: i for i, relation in enumerate(relations)}
    concept_to_i = {concept: i for i, concept in enumerate(concepts)}

    assertions = defaultdict(list)
    for relation, concept_origin, concept_target in get_assertions():
        assertions[relation_to_i[relation]].append((concept_to_i[concept_origin], concept_to_i[concept_target]))

    for relation, edges in assertions.items():
        with open("assertions/" + str(relation), mode='w+') as assertions_file:
            assertions_file.writelines(map(lambda t: ' '.join(map(str, t)) + '\n', sorted(edges)))
