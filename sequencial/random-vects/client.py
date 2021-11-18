import pickle
import secrets
import socket
import time

import numpy as np

HOST, PORT1, PORT2 = "localhost", 9998, 9999

PICKLED_VECTOR_SZ = 3798626

SHARED_FOLDER = "../../shared/"

words = open(SHARED_FOLDER + "words.txt", "r").read().split(',')
titles = open(SHARED_FOLDER + "titles.txt", "r").read().split(';;;')

ndocs = len(titles)
nwords = len(words)

while True:
    try:
        # kwords = input(
        #     "Provide the keyword you want to search for: ").split(" ")
        kwords = ["computer", "science"]
        kw_idxs = [words.index(kword) for kword in kwords]
        break
    except ValueError:
        print("Keyword doesn't exist in word list")


print(
    f"Picked words '{' '.join(kwords)}' (idx = {' '.join(str(kw_idx) for kw_idx in kw_idxs)})")

print()
print("Choosing random number")

t1 = time.time()
rand_bitvector = secrets.randbits(nwords)
t2 = time.time()

print(f"Chose random number in {t2 - t1} seconds")
print()

print("Creating random vectors")
t1 = time.time()

vector_a = np.zeros((nwords))
for idx in range(nwords):
    vector_a[idx] = (rand_bitvector & (1 << idx)) >> idx

vector_b = np.copy(vector_a)
for kw_idx in kw_idxs:
    vector_a[kw_idx] = 1
    vector_b[kw_idx] = 0

t2 = time.time()

print(f"Created vectors in {t2 - t1} seconds")
print()

# print(len(pickle.dumps(vector_a)))

print("Sending vectors to servers")

t1 = time.time()

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.connect((HOST, PORT1))

va_pickled = pickle.dumps(vector_a)
sock1.sendall(va_pickled)

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

vb_pickled = pickle.dumps(vector_b)
sock2.sendall(vb_pickled)

data = b''
while True:
    part = sock2.recv(BUFF_SIZE)
    data += part
    if len(part) < BUFF_SIZE:
        break
r2 = pickle.loads(data)

t2 = time.time()

print("Size of each vector (in bytes): ", len(va_pickled))
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
