import pickle
import time
from multiprocessing import Manager, Process

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
                                                  config.PORT1, results, 0))
        vb_pickled = pickle.dumps(vector_b)
        p2 = Process(target=send_to_server, args=(config.SCORES_HEADER + vb_pickled, config.HOST,
                                                  config.PORT2, results, 1))

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
        return res
