import pickle
import random

import numpy as np

print("Loading tfidf matrix")
tfidf = pickle.load(open("tfidf.pickle", "rb"))
print("Matrix loaded")

words = open("words.txt", "r").read().split(',')
titles = open("titles.txt", "r").read().split(';;;')

ndocs = tfidf.shape[0]
nwords = tfidf.shape[1]

# kw_idx = random.randint(0, nwords)
# kword = words[kw_idx]
kword = "computer"
kw_idx = words.index(kword)
print(f"Picked word {kword}, (idx = {kw_idx})")

print("Creating random vectors")
rand_bitvector = random.getrandbits(nwords)

vector_a = np.zeros((nwords))
for idx in range(nwords):
    if rand_bitvector & (1 << idx):
        vector_a[idx] = 1

vector_b = np.copy(vector_a)
vector_a[kw_idx] = 1
vector_b[kw_idx] = 0

res_a = tfidf.dot(vector_a)
res_b = tfidf.dot(vector_b)

res = res_a - res_b

for idx, score in enumerate(res):
    if score > 0.0:
        print(titles[idx], score)
        print(titles[len(titles) - idx], score)

real_query = np.zeros((nwords))
real_query[kw_idx] = 1
real_res = tfidf.dot(real_query)

print("Real query results:")
for idx, score in enumerate(real_res):
    if score > 0.0:
        print(titles[idx], score)
        print(titles[len(titles) - idx], score)
