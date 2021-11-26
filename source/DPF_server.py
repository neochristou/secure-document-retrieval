import pickle
import socketserver
import time

import numpy as np

from DPF import *


class DPFServer(socketserver.BaseRequestHandler):

    def handle(self):

        BUFF_SIZE = 4096  # 4 KiB
        data = b''
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break

        # print(len(data))

        #k = pickle.loads(data)  # key
        k = data # key
        print("Received query key from client")

        print("Calculating query vector")
        t1 = time.time()
        keyword_vector = dpf_eval_full(k)[:self.server.nwords]

        print("Calculating scores for vector")

        scores = self.server.tfidf.dot(keyword_vector)
        t2 = time.time()

        print(f"Calculated GGM and scores in {t2 - t1} seconds")
        # print(len(pickle.dumps(scores)))

        self.request.sendall(pickle.dumps(scores))
