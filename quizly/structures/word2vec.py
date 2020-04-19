import spacy

spacy.prefer_gpu()
nlp = spacy.load("en_core_web_md")


def word2vec_similarity(one: str, two: str) -> float:
    return nlp(one).similarity(nlp(two))
