import argparse

import config
from DPF_cli import DPFClient
from it_pir_cli import ITPIRClient
from naive_pir_cli import NaivePIRClient
from PPRF_cli import PPRFClient
from random_vecs_cli import RandomVectorsClient
from rv_opt_cli import RandomVectorsOptClient
from sdr_util import choose_document, get_highest_ranked, get_user_keywords

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Choose secure matrix multiplication scheme")
    arg_parser.add_argument("--scheme",
                            choices=["random-vectors",
                                     "rv-opt", "PPRF", "PPRF-opt", "DPF"],
                            required=True,
                            help="Scheme to be used for matrix multiplication")

    arg_parser.add_argument("--pir",
                            choices=["naive", "it-pir"],
                            required=True,
                            help="Scheme to be used for PIR")

    arg_parser.add_argument("--ports",
                            required=True,
                            nargs=2,
                            help="Scheme to be used for PIR")

    args = arg_parser.parse_args()

    with open(config.SHARED_FOLDER + "words.txt", "r") as words_file:
        words = words_file.read().split(',')
    with open(config.SHARED_FOLDER + "titles.txt", "r") as titles_file:
        titles = titles_file.read().split(';;;')

    kwords, kw_idxs = get_user_keywords(words)

    if args.scheme == "random-vectors":
        mm_client = RandomVectorsClient(kwords, kw_idxs, len(words))
    if args.scheme == "rv-opt":
        mm_client = RandomVectorsOptClient(kwords, kw_idxs, len(words))
    if args.scheme == "PPRF" or args.scheme == "PPRF-opt":  # opt is on server
        mm_client = PPRFClient(kwords, kw_idxs, len(words))
    if args.scheme == "DPF":
        mm_client = DPFClient(kwords, kw_idxs, len(words))

    port1_arg, port2_arg = args.ports
    mm_client.port1 = int(port1_arg)
    mm_client.port2 = int(port2_arg)
    scores = mm_client.request_scores()
    highest_ranked = get_highest_ranked(scores, words, titles)
    doc, doc_idx = choose_document(highest_ranked)

    if args.pir == "naive":
        pir_client = NaivePIRClient(doc_idx, len(titles))
    if args.pir == "it-pir":
        pir_client = ITPIRClient(doc)

    pir_client.port1 = int(port1_arg)
    pir_client.port2 = int(port2_arg)
    doc = pir_client.retrieve_document()
    print("Requested document:")
    print(doc.decode())
