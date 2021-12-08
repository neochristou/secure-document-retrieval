import pickle
import sys
import time
from multiprocessing import Manager, Process
from random import randint

import numpy as np

import config
from sdr_util import get_random_bits, send_to_server


class RandomVectorsClient():
    """In this scheme, the client creates two (almost) identical random bitvectors,
    which differ only in the bits at the position of the words the user has chosen
    to search for --- the first bitvector has this bits set and the second doesn't.

    The client sends one vector to each server and subtracts the resulting vector
    of the first server from the second one to get the result for the word they
    were actually looking for"""

    def __init__(self, kwords, kw_idxs, nwords):
        self.kwords = kwords
        self.kw_idxs = kw_idxs
        self.nwords = nwords

    def request_scores(self):

        start_time = time.time()

        rand_bitvector = get_random_bits(self.nwords)

        print("Creating random vectors")
        t1 = time.time()

        vector_a = np.zeros((self.nwords))
        for idx in range(self.nwords):
            vector_a[idx] = (rand_bitvector & (1 << idx)) >> idx

        vector_b = np.copy(vector_a)
        for kw_idx in self.kw_idxs:
            vector_a[kw_idx] = 1
            vector_b[kw_idx] = 0

        t2 = time.time()

        print(f"Created vectors in {t2 - t1} seconds")
        print()

        # Multiprocessing in order to avoid blocking until one of the
        # server returns result
        t1 = time.time()
        manager = Manager()
        # Shared dictionary to get result back from subprocess
        results = manager.dict()

        va_pickled = pickle.dumps(vector_a)
        p1 = Process(target=send_to_server, args=(config.SCORES_HEADER + va_pickled, config.HOST,
                                                  self.port1, results, 0))
        vb_pickled = pickle.dumps(vector_b)
        p2 = Process(target=send_to_server, args=(config.SCORES_HEADER + vb_pickled, config.HOST,
                                                  self.port2, results, 1))

        p1.start()
        p2.start()
        p1.join()
        p2.join()

        r1 = pickle.loads(results[0])
        r2 = pickle.loads(results[1])

        t2 = time.time()

        print(f"Received server scores in {t2 - t1} seconds")
        print()

        print("Calculating scores")
        res = r1 - r2
        end_time = time.time()

        # Benchmarking
        with open(config.BENCH_FOLDER + "random_vecs_cli_latency.txt", "a+") as lat:
            lat.write(f"{end_time - start_time},")
        with open(config.BENCH_FOLDER + "random_vecs_cli_psz.txt", "a+") as psz:
            psz.write(f"{len(va_pickled)},")

        return res


if __name__ == "__main__":

    with open(config.SHARED_FOLDER + "words.txt", "r") as words_file:
        words = words_file.read().split(',')
    with open(config.SHARED_FOLDER + "titles.txt", "r") as titles_file:
        titles = titles_file.read().split(';;;')

    # Pick random word for benchmarking
    kw_idx = randint(0, len(words))
    kw_idxs = [kw_idx]
    kwords = [words[kw_idx]]
    client = RandomVectorsClient(kwords, kw_idxs, len(words))
    client.port1 = int(sys.argv[1])
    client.port2 = int(sys.argv[2])
    client.request_scores()
