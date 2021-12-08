import pickle
import socketserver
import time

import numpy as np

import config


class RandomVectorsOptServer(socketserver.BaseRequestHandler):

    def handle(self):

        BUFF_SIZE = 4096  # 4 KiB

        data = b''
        while True:
            part = self.request.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                break

        if data.startswith(config.SCORES_HEADER):
            data = data[len(config.SCORES_HEADER):]
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
            reply = pickle.dumps(scores)
            self.request.sendall(reply)
            with open(config.BENCH_FOLDER + "rv_opt_server_sz.txt", "a+") as psz:
                psz.write(f"{len(reply)},")

        elif data.startswith(config.PIR_HEADER):

            print("Retrieving requested documents")

            t1 = time.time()
            data = data[len(config.PIR_HEADER):]
            docs = self.server.pir_func(data, self.server.file_matrix)
            t2 = time.time()

            print(f"Requested documents retrieved in {t2 - t1} seconds")

            self.request.sendall(docs)
            with open(config.BENCH_FOLDER + config.PIR_SERVER_FILE, "a+") as psz:
                psz.write(f"{len(docs)},")
        else:
            raise NotImplementedError
