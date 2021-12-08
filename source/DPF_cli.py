import pickle
import sys
import time
from multiprocessing import Manager, Process
from random import randint

import numpy as np

import config
from DPF import *
from sdr_util import get_random_bits, get_user_keywords, send_to_server


class DPFClient():

    def __init__(self, kwords, kw_idxs, nwords):
        self.kwords = kwords
        self.kw_idxs = kw_idxs
        self.nwords = nwords

    def request_scores(self):

        print("Choosing random seed")

        start_time = time.time()
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
        k0, k1 = dpf_gen_keys(self.kw_idxs[0], config.NWORD_BITS)

        t2 = time.time()

        print(f"Created punctured keys in {t2 - t1} seconds")
        print()

        print("Sending punctured keys to servers")

        # Multiprocessing in order to avoid blocking until one of the
        # server returns result
        t1 = time.time()
        manager = Manager()
        # Shared dictionary to get result back from subprocess
        results = manager.dict()

        p1 = Process(target=send_to_server, args=(config.SCORES_HEADER + k0, config.HOST,
                                                  self.port1, results, 0))
        p2 = Process(target=send_to_server, args=(config.SCORES_HEADER + k1, config.HOST,
                                                  self.port2, results, 1))

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
        end_time = time.time()

        # Benchmarking
        with open(config.BENCH_FOLDER + "DPF_cli_latency.txt", "a+") as lat:
            lat.write(f"{end_time - start_time},")
        with open(config.BENCH_FOLDER + "DPF_cli_psz.txt", "a+") as psz:
            psz.write(f"{len(k0)},")

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
    client = DPFClient(kwords, kw_idxs, len(words))
    client.port1 = int(sys.argv[1])
    client.port2 = int(sys.argv[2])
    client.request_scores()
