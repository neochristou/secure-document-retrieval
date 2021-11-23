import pickle
import socketserver
import time

import numpy as np

from PPRF_GGM import *


class PPRFServer(socketserver.BaseRequestHandler):

    def handle(self):

        BUFF_SIZE = 4096  # 4 KiB
        data = b''
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break

        # print(len(data))

        pk = pickle.loads(data)  # punctured key
        print("Received vector from client")

        print("Calculating GGM")
        t1 = time.time()
        keyword_vector = np.zeros((self.server.nwords))
        for idx in range(self.server.nwords):
            if idx % 1000 == 0:
                print("Currently computing PPRF(K, {})".format(idx))
            keyword_vector[idx] = Eval(pk, idx)

        print("Calculating scores for vector")

        scores = self.server.tfidf.dot(keyword_vector)
        t2 = time.time()

        print(f"Calculated GGM and scores in {t2 - t1} seconds")
        # print(len(pickle.dumps(scores)))

        self.request.sendall(pickle.dumps(scores))