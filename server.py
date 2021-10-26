import pickle
import socketserver
import sys
import time

# import numpy as np

print("Loading tfidf matrix")
tfidf = pickle.load(open("tfidf.pickle", "rb"))
print("Matrix loaded")


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

        keyword_vec = pickle.loads(data)

        print("Received vector from client")
        print("Calculating scores for vector")

        t1 = time.time()
        scores = tfidf.dot(keyword_vec)
        t2 = time.time()

        print(f"Calculated scores in {t2 - t1} seconds")
        # print(len(pickle.dumps(scores)))

        self.request.sendall(pickle.dumps(scores))


if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])

    with socketserver.TCPServer((HOST, PORT), DocumentServer) as server:
        server.serve_forever()
