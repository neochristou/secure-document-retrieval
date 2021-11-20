import pickle
import socketserver
import time

import numpy as np


class RandomVectorsOptServer(socketserver.BaseRequestHandler):

    def handle(self):

        BUFF_SIZE = 4096  # 4 KiB
        data = b''
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break

        num = int.from_bytes(data, "big")

        print("Received number from client")
        print()

        print("Turning number into numpy array")
        t1 = time.time()
        keyword_vec = np.zeros((self.server.nwords))
        for idx in range(self.server.nwords):
            keyword_vec[idx] = (num & (1 << idx)) >> idx
        t2 = time.time()
        print(f"Turned number into array in {t2 - t1} seconds")

        print("Calculating scores for vector")

        t1 = time.time()
        scores = self.server.tfidf.dot(keyword_vec)
        t2 = time.time()

        print(f"Calculated scores in {t2 - t1} seconds")
        self.request.sendall(pickle.dumps(scores))
