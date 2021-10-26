import pickle
import random
import socket
import time

import numpy as np

HOST, PORT1, PORT2 = "localhost", 9998, 9999

PICKLED_VECTOR_SZ = 3798626

words = open("words.txt", "r").read().split(',')
titles = open("titles.txt", "r").read().split(';;;')

ndocs = len(titles)
nwords = len(words)

while True:
    try:
        kword = input("Provide the keyword you want to search for: ")
        kw_idx = words.index(kword)
        break
    except ValueError:
        print("Keyword doesn't exist in word list")


print(f"Picked word {kword} (idx = {kw_idx})")

print("Creating random vectors")

t1 = time.time()

rand_bitvector = random.getrandbits(nwords)

vector_a = np.zeros((nwords))
for idx in range(nwords):
    if rand_bitvector & (1 << idx):
        vector_a[idx] = 1

vector_b = np.copy(vector_a)
vector_a[kw_idx] = 1
vector_b[kw_idx] = 0

t2 = time.time()

print(f"Created vectors in {t2 - t1} seconds")

# print(len(pickle.dumps(vector_a)))

print("Sending vectors to servers")

t1 = time.time()

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.connect((HOST, PORT1))

sock1.sendall(pickle.dumps(vector_a))

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

sock2.sendall(pickle.dumps(vector_b))

data = b''
while True:
    part = sock2.recv(BUFF_SIZE)
    data += part
    if len(part) < BUFF_SIZE:
        break
r2 = pickle.loads(data)

t2 = time.time()

print(f"Received server scores in {t2 - t1} seconds")

print(f"Calculating scores for keyword {kword}")
res = r1 - r2


print("Highest ranked documents: ")

for idx, score in enumerate(res):
    if score > 0.0:
        print(titles[idx], score)
        print(titles[len(titles) - idx], score)
