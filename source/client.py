import argparse

import config
from naive_pir_cli import NaivePIRClient
from PPRF_cli import PPRFClient
from random_vecs_cli import RandomVectorsClient
from rv_opt_cli import RandomVectorsOptClient
from sdr_util import choose_document, get_highest_ranked, get_user_keywords

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Choose secure matrix multiplication scheme")
    arg_parser.add_argument("--scheme",
                            choices=["random-vectors", "rv-opt", "PPRF"],
                            required=True,
                            help="Scheme to be used for matrix multiplication")

    arg_parser.add_argument("--pir",
                            choices=["naive"],
                            required=True,
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
    if args.scheme == "PPRF":
        mm_client = PPRFClient(kwords, kw_idxs, len(words))

    scores = mm_client.request_scores()
    highest_ranked = get_highest_ranked(scores, words, titles)
    doc_idx = choose_document(highest_ranked)

    if args.pir == "naive":
        pir_client = NaivePIRClient(doc_idx, len(titles))

    doc = pir_client.retrieve_document()
    print("Requested document:")
    print(doc.decode())
