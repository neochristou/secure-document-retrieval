
import pickle
import time
from multiprocessing import Manager, Process

import config
from sdr_util import get_random_bits, send_to_server


class RandomVectorsOptClient():
    """ Optimized version of RandomVectors client:
    send the random vector as bytes instead of a pickled
    numpy array in order to save space"""

    def __init__(self, kwords, kw_idxs, nwords):
        self.kwords = kwords
        self.kw_idxs = kw_idxs
        self.nwords = nwords

    def request_scores(self):

        print("Choosing random numbers")
        t1 = time.time()

        num_a = get_random_bits(self.nwords)
        num_b = num_a

        t2 = time.time()
        print(f"Chose random number in {t2 - t1} seconds")
        print()

        print("Setting keyword bits")
        t1 = time.time()

        for kw_idx in self.kw_idxs:
            # Set the keyword bit for num_a, clear it for num_b
            num_a |= (1 << kw_idx)
            num_b &= ~(1 << kw_idx)

        a_bitlen = (num_a.bit_length() + 7) // 8
        a_enc = num_a.to_bytes(a_bitlen, "big")
        b_bitlen = (num_b.bit_length() + 7) // 8
        b_enc = num_b.to_bytes(b_bitlen, "big")

        t2 = time.time()

        print(f"Created numbers in {t2 - t1} seconds")
        print()

        t1 = time.time()

        # Multiprocessing in order to avoid blocking until one of the
        # server returns result

        manager = Manager()
        # Shared dictionary to get result back from subprocess
        results = manager.dict()

        p1 = Process(target=send_to_server, args=(config.SCORES_HEADER + a_enc, config.HOST,
                                                  config.PORT1, results, 0))
        p2 = Process(target=send_to_server, args=(config.SCORES_HEADER + b_enc, config.HOST,
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
