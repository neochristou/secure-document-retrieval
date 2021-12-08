import secrets
import sys
import time
from multiprocessing import Manager, Process
from random import randint

import config
from sdr_util import send_to_server


class NaivePIRClient:
    """Retrieves the requested document plus a number of other random documents"""

    def __init__(self, doc_idx, ndocs):
        self.doc_idx = doc_idx
        self.ndocs = ndocs

    def retrieve_document(self):

        start_time = time.time()

        random_idxs = []

        print("Picking random documents to request")

        for _ in range(config.NAIVE_PIR_NUM_DOCS - 1):
            random_idxs.append(secrets.randbelow(self.ndocs))

        # Insert the desired document idx in a random spot
        rand_idx = secrets.randbelow(len(random_idxs))
        random_idxs.insert(rand_idx, self.doc_idx)

        # Request half of the random list from each server
        lst_mid = len(random_idxs)//2
        doc_list1 = ','.join(str(idx)
                             for idx in random_idxs[:lst_mid]).encode()
        doc_list2 = ','.join(str(idx)
                             for idx in random_idxs[lst_mid:]).encode()

        manager = Manager()
        # Shared dictionary to get result back from subprocess
        results = manager.dict()

        p1 = Process(target=send_to_server, args=(config.PIR_HEADER + doc_list1,
                                                  config.HOST, self.port1,
                                                  results, 0))
        p2 = Process(target=send_to_server, args=(config.PIR_HEADER + doc_list2,
                                                  config.HOST, self.port2,
                                                  results, 1))

        print("Requesting random documents from servers")
        t1 = time.time()
        p1.start()
        p2.start()
        p1.join()
        p2.join()

        t2 = time.time()
        print(f"Retrieved requsted documents in {t2 - t1} seconds")

        # Only return the correct document
        if rand_idx < lst_mid:
            res = results[0]
        else:
            res = results[1]
            rand_idx -= lst_mid

        res = res.split(config.DOCS_DELIM.encode())
        correct_doc = res[rand_idx]

        end_time = time.time()

        # Benchmarking
        with open(config.BENCH_FOLDER + "naive_pir_cli_latency.txt", "a+") as lat:
            lat.write(f"{end_time - start_time},")
        with open(config.BENCH_FOLDER + "naive_pir_cli_psz.txt", "a+") as psz:
            psz.write(f"{len(doc_list1)},")

        return correct_doc


if __name__ == "__main__":

    with open(config.SHARED_FOLDER + "titles.txt", "r") as titles_file:
        titles = titles_file.read().split(';;;')

    rand_doc = randint(0, len(titles))
    # Pick random word for benchmarking
    client = NaivePIRClient(rand_doc, len(titles))
    client.port1 = int(sys.argv[1])
    client.port2 = int(sys.argv[2])
    client.retrieve_document()
