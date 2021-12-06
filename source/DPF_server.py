import pickle
import socketserver
import time

import config
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

        if data.startswith(config.SCORES_HEADER):
            data = data[len(config.SCORES_HEADER):]
            # k = pickle.loads(data)  # key
            k = data  # key
            print("Received query key from client")

            print("Calculating query vector")
            t1 = time.time()
            keyword_vector = dpf_eval_full(k, config.NWORD_BITS)[
                :self.server.nwords]

            print("Calculating scores for vector")

            scores = self.server.tfidf.dot(keyword_vector)
            t2 = time.time()

            print(f"Calculated GGM and scores in {t2 - t1} seconds")
            # print(len(pickle.dumps(scores)))

            self.request.sendall(pickle.dumps(scores))

        elif data.startswith(config.PIR_HEADER):

            print("Retrieving requested documents")

            t1 = time.time()
            data = data[len(config.PIR_HEADER):]
            docs = self.server.pir_func(data, self.server.file_matrix)
            t2 = time.time()

            print(f"Requested documents retrieved in {t2 - t1} seconds")

            self.request.sendall(docs)
        else:
            raise NotImplementedError
