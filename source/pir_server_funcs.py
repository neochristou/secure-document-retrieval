import time

import numpy as np

import config
from DPF import *
from sdr_util import byte_xor, load_document


def naive_pir(doc_idxs, *_):

    titles = open(config.SHARED_FOLDER + "titles.txt", "r").read().split(';;;')
    doc_idxs = [int(doc_idx) for doc_idx in doc_idxs.split(b',')]

    print("Retrieving documents")

    t1 = time.time()
    results = ''
    for doc_idx in doc_idxs:
        doc = load_document(doc_idx, titles)
        results += doc + config.DOCS_DELIM
    t2 = time.time()
    print(f"Retrieved docuemnts in {t2 - t1} seconds")

    return results.encode()


def it_pir(key, file_matrix):

    print("Expanding client's query")

    keyword_vector = dpf_eval_full(key, config.BIN_BITS)
    num_bins = len(file_matrix)
    bin_size = len(file_matrix[0])
    result = bytearray(bin_size)
    bins_to_retrieve = np.where(keyword_vector == 1)[0].tolist()

    print("Creating result vector")

    t1 = time.time()
    for bin_idx in bins_to_retrieve:
        if bin_idx >= num_bins:
            break
        file_bin = file_matrix[bin_idx]
        result = byte_xor(result, file_bin)
    t2 = time.time()

    print(f"Created result vector in {t2 - t1} seconds")

    return result
