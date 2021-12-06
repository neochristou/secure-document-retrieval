import argparse
import pickle
import socketserver

import config
from DPF_server import DPFServer
from pir_server_funcs import it_pir, naive_pir
from PPRF_opt_server import PPRFOptServer
from PPRF_server import PPRFServer
from random_vecs_server import RandomVectorsServer
from rv_opt_server import RandomVectorsOptServer
from sdr_util import create_bins

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Choose secure matrix multiplication scheme")
    arg_parser.add_argument("--scheme",
                            choices=["random-vectors",
                                     "rv-opt", "PPRF", "PPRF-opt", "DPF"],
                            required=True,
                            help="Scheme to be used for matrix multiplication")
    arg_parser.add_argument("-p", "--port",
                            type=int,
                            required=True)
    arg_parser.add_argument("--pir",
                            choices=["naive", "it-pir"],
                            required=True,
                            help="Scheme to be used for PIR")

    args = arg_parser.parse_args()

    print("Loading tfidf matrix")
    tfidf = pickle.load(open(config.SHARED_FOLDER + "tfidf.pickle", "rb"))
    print("Matrix loaded")

    print("Creating bins")
    file_matrix = create_bins()
    print(f"Created bins")

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
    if args.scheme == "DPF":
        server = DPFServer

    if args.pir == "naive":
        pir_func = naive_pir
    if args.pir == "it-pir":
        pir_func = it_pir

    with socketserver.TCPServer((config.HOST, args.port), server) as doc_server:
        doc_server.tfidf = tfidf
        doc_server.nwords = nwords
        doc_server.pir_func = pir_func
        doc_server.file_matrix = file_matrix
        doc_server.serve_forever()
