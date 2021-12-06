import json
import os
import secrets
import socket
import time

import binpacking
import numpy as np

import config


def get_user_keywords(words):
    """Read words user wants to search for"""

    while True:
        try:
            kwords = input(
                "Provide the keyword you want to search for: ").split(" ")
            # kwords = ["computer"]
            kw_idxs = [words.index(kword) for kword in kwords]
            break
        except ValueError:
            print("Keyword doesn't exist in word list")

    print(
        f"Picked words '{' '.join(kwords)}' (idx = {' '.join(str(kw_idx) for kw_idx in kw_idxs)})")
    print()

    return kwords, kw_idxs


def get_random_bits(length):
    """Get a length-bit random number"""

    print("Choosing random number")

    t1 = time.time()
    rand_bitvector = secrets.randbits(length)
    t2 = time.time()

    print(f"Chose random number in {t2 - t1} seconds")
    print()

    return rand_bitvector


def send_to_server(data, host, port, results, pid):

    BUFF_SIZE = 4096

    print(f"Sending data to server at port {port}")
    print(f"Size of data: {len(data)}")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    sock.sendall(data)

    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            break

    results[pid] = data


def get_highest_ranked(scores, words, titles):
    """Print the titles of the documents with the highest scores"""

    doc_rankings = {}

    for idx, score in enumerate(scores):
        if score > 0.0:
            doc_rankings[titles[idx]] = (score, idx)

    doc_rankings = {k: v for k, v in sorted(
        doc_rankings.items(), key=lambda item: item[1][0], reverse=True)}
    top10 = list(doc_rankings.items())[:10]

    return top10


def choose_document(candidates):
    """ Choose the document to retrieve from the server"""

    print("Choose document to retrieve from the highest ranked documents: ")

    for i, tup in enumerate(candidates):
        doc, (score, doc_idx) = tup
        author, title = doc.split('___')
        print(f"[{i}] {title : <50} by {author : <30} (Score: {score})")

    while True:
        try:
            choice = int(input("Index of document to retrieve: "))
            doc, (_, doc_idx) = candidates[choice]
            return doc, doc_idx
        except IndexError:
            print("Wrong index!")

    return None


def load_document(doc_idx, titles):
    docname = titles[doc_idx] + '.txt'
    with open(config.DOCS_PATH + docname, 'r') as doc:
        return doc.read()


def create_bins():

    file_sizes = {}
    file_contents = {}
    for filename in os.listdir(config.DOCS_PATH):
        with open(config.DOCS_PATH + filename, 'rb') as file:
            contents = file.read()
            file_len = len(contents)
            file_sizes[filename] = file_len
            file_contents[filename] = contents

    max_file = max(file_sizes, key=file_sizes.get)
    max_size = file_sizes[max_file]
    # print(f"Largest file (in bytes): {max_file}: {max_size}")

    bins = binpacking.to_constant_volume(file_sizes, max_size)

    bin_metadata = {}
    file_matrix = []
    for row_num, file_bin in enumerate(bins):
        row = b''
        doc_start = 0
        for title, size in file_bin.items():
            contents = file_contents[title]
            row += contents
            bin_metadata[title] = (row_num, doc_start, size)
            doc_start += size
        row += b'\x00' * (max_size - len(row))
        file_matrix.append(row)

    # Save the bin metadata
    # bins_json = json.dumps(bin_metadata)
    # with open(config.SHARED_FOLDER + 'bins.json', 'w') as f:
    #     f.write(bins_json)

    return file_matrix


def byte_xor(b1, b2):
    n_b1 = np.frombuffer(b1, dtype='uint8')
    n_b2 = np.frombuffer(b2, dtype='uint8')
    return (n_b1 ^ n_b2).tobytes()


if __name__ == "__main__":
    create_bins()
