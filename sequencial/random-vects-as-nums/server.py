import pickle
import socketserver
import sys
import time

import numpy as np

SHARED_FOLDER = "../../shared/"

print("Loading tfidf matrix")
tfidf = pickle.load(open(SHARED_FOLDER + "tfidf.pickle", "rb"))
print("Matrix loaded")

words = open(SHARED_FOLDER + "words.txt", "r").read().split(',')
nwords = len(words)


class DocumentServer(socketserver.BaseRequestHandler):

    def handle(self):
        global tfidf
        global nwords

        BUFF_SIZE = 4096  # 4 KiB
        data = b''
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break

        num = int(data)

        print("Received number from client")
        print()

        print("Turning number into numpy array")
        t1 = time.time()
        keyword_vec = np.zeros((nwords))
        for idx in range(nwords):
            keyword_vec[idx] = (num & (1 << idx)) >> idx
        t2 = time.time()
        print(f"Turned number into array in {t2 - t1} seconds")

        print("Calculating scores for vector")

        t1 = time.time()
        scores = tfidf.dot(keyword_vec)
        t2 = time.time()

        print(f"Calculated scores in {t2 - t1} seconds")

        self.request.sendall(pickle.dumps(scores))


if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])

    with socketserver.TCPServer((HOST, PORT), DocumentServer) as server:
        server.serve_forever()
