import secrets
import socket
import time


def get_user_keywords(words):
    """Read words user wants to search for"""

    while True:
        try:
            # kwords = input(
            #     "Provide the keyword you want to search for: ").split(" ")
            kwords = ["computer"]
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


def print_highest_ranked(scores, words, titles):
    """Print the titles of the documents with the highest scores"""

    doc_rankings = {}

    for idx, score in enumerate(scores):
        if score > 0.0:
            doc_rankings[titles[idx]] = score

    doc_rankings = {k: v for k, v in sorted(
        doc_rankings.items(), key=lambda item: item[1], reverse=True)}
    top10 = list(doc_rankings.items())[:10]

    print("Highest ranked documents: ")
    for tup in top10:
        title, score = tup
        print(title, score)
    # print(titles[len(titles) - idx], score)
