import pickle
import secrets
import socket
import time

from PPRF_GGM import *

HOST, PORT1, PORT2 = "localhost", 9998, 9999

PICKLED_VECTOR_SZ = 3798626
SEED_ENTROPY = 123

SHARED_FOLDER = "../../shared/"

words = open(SHARED_FOLDER + "words.txt", "r").read().split(',')
titles = open(SHARED_FOLDER + "titles.txt", "r").read().split(';;;')

ndocs = len(titles)
nwords = len(words)

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
print("Choosing random number")

t1 = time.time()
rand_seed = secrets.randbits(SEED_ENTROPY)
print("Rand seed : {}".format(rand_seed))
print(kw_idxs)
t2 = time.time()

print(f"Chose random number in {t2 - t1} seconds")
print()

print("Creating punctured keys")
t1 = time.time()

#initial_value = GMM(rand_seed, kw_idxs[0])
#modified_value = 1 - initial_value

# Generating punctured keys
pk1 = puncture(rand_seed, kw_idxs[0], 1)
pk2 = puncture(rand_seed, kw_idxs[0], 0)

t2 = time.time()

print(f"Created puncturedkeys in {t2 - t1} seconds")
print()

# print(len(pickle.dumps(vector_a)))

print("Sending punctured keys to servers")

t1 = time.time()

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.connect((HOST, PORT1))

pk1_pickled = pickle.dumps(pk1)
sock1.sendall(pk1_pickled)

BUFF_SIZE = 4096  # 4 KiB

data = b''
while True:
    part = sock1.recv(BUFF_SIZE)
    data += part
    if len(part) < BUFF_SIZE:
        break
r1 = pickle.loads(data)

sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock2.connect((HOST, PORT2))

pk2_pickled = pickle.dumps(pk2)
sock2.sendall(pk2_pickled)

data = b''
while True:
    part = sock2.recv(BUFF_SIZE)
    data += part
    if len(part) < BUFF_SIZE:
        break
r2 = pickle.loads(data)

t2 = time.time()

print("Size of each punctured key (in bytes): ", len(pk1))
print()

print(f"Received server scores in {t2 - t1} seconds")
print()

print(f"Calculating scores for keywords '{' '.join(kwords)}'")
res = r1 - r2


print("Highest ranked documents: ")

doc_rankings = {}

for idx, score in enumerate(res):
    if score > 0.0:
        doc_rankings[titles[idx]] = score

doc_rankings = {k: v for k, v in sorted(
    doc_rankings.items(), key=lambda item: item[1], reverse=True)}
top10 = list(doc_rankings.items())[:10]

for tup in top10:
    title, score = tup
    print(title, score)
# print(titles[len(titles) - idx], score)
