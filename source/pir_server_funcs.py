import config
from sdr_util import load_document


def naive_pir(doc_idxs):

    titles = open(config.SHARED_FOLDER + "titles.txt", "r").read().split(';;;')
    doc_idxs = [int(doc_idx) for doc_idx in doc_idxs.split(b',')]

    results = ''
    for doc_idx in doc_idxs:
        doc = load_document(doc_idx, titles)
        results += doc + config.DOCS_DELIM

    return results
