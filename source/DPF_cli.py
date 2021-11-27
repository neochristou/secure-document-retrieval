import pickle
import time
from multiprocessing import Manager, Process

import numpy as np

import config
from DPF import *
from sdr_util import get_random_bits, send_to_server


class DPFClient():

    def __init__(self, kwords, kw_idxs, nwords):
        self.kwords = kwords
        self.kw_idxs = kw_idxs
        self.nwords = nwords

    def request_scores(self):

        print()
        print("Choosing random number")

        t1 = time.time()

        rand_seed = get_random_bits(config.SEED_ENTROPY)
        print("Rand seed : {}".format(rand_seed))

        t2 = time.time()
        print(f"Chose random number in {t2 - t1} seconds")
        print()

        print("Creating punctured keys")
        t1 = time.time()

        # initial_value = GMM(rand_seed, kw_idxs[0])
        # modified_value = 1 - initial_value

        # Generating DPF keys
        k0, k1 = dpf_gen_keys(self.kw_idxs[0])

        t2 = time.time()

        print(f"Created puncturedkeys in {t2 - t1} seconds")
        print()

        print("Sending punctured keys to servers")

        t1 = time.time()
        # Multiprocessing in order to avoid blocking until one of the
        # server returns result
        t1 = time.time()
        manager = Manager()
        # Shared dictionary to get result back from subprocess
        results = manager.dict()

        p1 = Process(target=send_to_server, args=(config.SCORES_HEADER + k0, config.HOST,
                                                  config.PORT1, results, 0))
        p2 = Process(target=send_to_server, args=(config.SCORES_HEADER + k1, config.HOST,
                                                  config.PORT2, results, 1))

        p1.start()
        p2.start()
        p1.join()
        p2.join()

        r1 = pickle.loads(results[0])
        r2 = pickle.loads(results[1])

        t2 = time.time()

        print("Size of key (in bytes): ", len(k0))
        print()

        print(f"Received server scores in {t2 - t1} seconds")
        print()

        res = np.abs(r1 - r2)
        return res
