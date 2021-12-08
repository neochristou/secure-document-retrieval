import pickle
import socketserver
import time

import config


class RandomVectorsServer(socketserver.BaseRequestHandler):

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
            keyword_vec = pickle.loads(data)

            print("Received vector from client")
            print("Calculating scores for vector")

            t1 = time.time()
            scores = self.server.tfidf.dot(keyword_vec)
            t2 = time.time()

            print(f"Calculated scores in {t2 - t1} seconds")

            reply = pickle.dumps(scores)
            self.request.sendall(reply)

            with open(config.BENCH_FOLDER + "random_vectors_server_sz.txt", "a+") as psz:
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
