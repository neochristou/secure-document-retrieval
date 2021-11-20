import argparse

import config
from PPRF_cli import PPRFClient
from random_vecs_cli import RandomVectorsClient
from rv_opt_cli import RandomVectorsOptClient
from sdr_util import get_user_keywords, print_highest_ranked

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        description="Choose secure matrix multiplication scheme")
    arg_parser.add_argument("--scheme",
                            choices=["random-vectors", "rv-opt", "PPRF"],
                            required=True,
                            help="Scheme to be used for matrix multiplication")

    args = arg_parser.parse_args()

    words = open(config.SHARED_FOLDER + "words.txt", "r").read().split(',')
    titles = open(config.SHARED_FOLDER + "titles.txt", "r").read().split(';;;')

    kwords, kw_idxs = get_user_keywords(words)

    if args.scheme == "random-vectors":
        client = RandomVectorsClient(kwords, kw_idxs, len(words))
    if args.scheme == "rv-opt":
        client = RandomVectorsOptClient(kwords, kw_idxs, len(words))
    if args.scheme == "PPRF":
        client = PPRFClient(kwords, kw_idxs, len(words))

    res = client.request_documents()
    print_highest_ranked(res, words, titles)
