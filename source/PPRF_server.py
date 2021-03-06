import pickle
import socketserver
import time

import numpy as np

import config
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

        if data.startswith(config.SCORES_HEADER):
            data = data[len(config.SCORES_HEADER):]

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

            reply = pickle.dumps(scores)
            self.request.sendall(reply)
            with open(config.BENCH_FOLDER + "PPRF_server_sz.txt", "a+") as psz:
                psz.write(f"{len(reply)},")

        elif data.startswith(config.PIR_HEADER):

            print("Retrieving requested documents")

            t1 = time.time()
            data = data[len(config.PIR_HEADER):]
            docs = self.server.pir_func(data, self.server.file_matrix)
            t2 = time.time()

            print(f"Requested documents retrieved in {t2 - t1} seconds")

            self.request.sendall(docs.encode())
            with open(config.BENCH_FOLDER + config.PIR_SERVER_FILE, "a+") as psz:
                psz.write(f"{len(docs)},")

        else:
            raise NotImplementedError
