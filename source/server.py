import argparse
import pickle
import socketserver

import config
from PPRF_server import PPRFServer
from PPRF_opt_server import PPRFOptServer
from random_vecs_server import RandomVectorsServer
from rv_opt_server import RandomVectorsOptServer

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Choose secure matrix multiplication scheme")
    arg_parser.add_argument("--scheme",
                            choices=["random-vectors", "rv-opt", "PPRF", "PPRF-opt"],
                            required=True,
                            help="Scheme to be used for matrix multiplication")
    arg_parser.add_argument("-p", "--port",
                            type=int,
                            required=True)

    args = arg_parser.parse_args()

    print("Loading tfidf matrix")
    tfidf = pickle.load(open(config.SHARED_FOLDER + "tfidf.pickle", "rb"))
    print("Matrix loaded")

    words = open(config.SHARED_FOLDER + "words.txt", "r").read().split(',')
    nwords = len(words)

    if args.scheme == "random-vectors":
        server = RandomVectorsServer
    if args.scheme == "rv-opt":
        server = RandomVectorsOptServer
    if args.scheme == "PPRF":
        server = PPRFServer
    if args.scheme == "PPRF-opt":
        server = PPRFOptServer

    with socketserver.TCPServer((config.HOST, args.port), server) as doc_server:
        doc_server.tfidf = tfidf
        doc_server.nwords = nwords
        doc_server.serve_forever()