import json
import time
from multiprocessing import Manager, Process

import config
from DPF import *
from sdr_util import byte_xor, send_to_server


class ITPIRClient:
    """Information theoretic PIR"""

    def __init__(self, doc_title):
        self.doc_title = doc_title

    def retrieve_document(self):

        with open(config.SHARED_FOLDER + 'bins.json', 'r') as metadata_file:
            metadata = json.loads(metadata_file.read())

        doc_name = self.doc_title + '.txt'
        doc_row = metadata[doc_name]
        doc_row_idx, doc_start, doc_size = doc_row

        k0, k1 = dpf_gen_keys(doc_row_idx, config.BIN_BITS)

        manager = Manager()
        # Shared dictionary to get result back from subprocess
        results = manager.dict()

        p1 = Process(target=send_to_server, args=(config.PIR_HEADER + k0,
                                                  config.HOST, config.PORT1,
                                                  results, 0))
        p2 = Process(target=send_to_server, args=(config.PIR_HEADER + k1,
                                                  config.HOST, config.PORT2,
                                                  results, 1))

        print("Requesting random documents from servers")
        t1 = time.time()
        p1.start()
        p2.start()
        p1.join()
        p2.join()

        t2 = time.time()
        print(f"Retrieved requsted documents in {t2 - t1} seconds")

        r1 = results[0]
        r2 = results[1]

        dec_row = byte_xor(r1, r2)

        correct_doc = dec_row[doc_start: doc_start + doc_size]

        return correct_doc
