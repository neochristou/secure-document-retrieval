import pickle
import socketserver
import sys
import time

import numpy as np
from PPRF_GGM import *

print("Loading tfidf matrix")
tfidf = pickle.load(open("../shared/tfidf.pickle", "rb"))
print("Matrix loaded")

nwords = len(open("../shared/words.txt", "r").read().split(','))

class DocumentServer(socketserver.BaseRequestHandler):

    def handle(self):
        global tfidf

        BUFF_SIZE = 4096  # 4 KiB
        data = b''
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break

        # print(len(data))

        pk = pickle.loads(data) # punctured key
        keyword_vector = np.zeros((nwords))
        for idx in range(nwords):
            if idx % 1000 == 0: print("Currently computing PPRF(K, {})".format(idx))
            keyword_vector[idx] = Eval(pk, idx)

        print("Received vector from client")
        print("Calculating scores for vector")

        t1 = time.time()
        scores = tfidf.dot(keyword_vector)
        t2 = time.time()

        print(f"Calculated scores in {t2 - t1} seconds")
        # print(len(pickle.dumps(scores)))

        self.request.sendall(pickle.dumps(scores))


if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])

    with socketserver.TCPServer((HOST, PORT), DocumentServer) as server:
        server.serve_forever()
