import pickle
import socketserver
import time


class RandomVectorsServer(socketserver.BaseRequestHandler):

    def handle(self):

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
        scores = self.server.tfidf.dot(keyword_vec)
        t2 = time.time()

        print(f"Calculated scores in {t2 - t1} seconds")
        # print(len(pickle.dumps(scores)))

        self.request.sendall(pickle.dumps(scores))
