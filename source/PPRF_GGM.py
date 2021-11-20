import random

# nbits = log2(nbr of keywords)
# nwords = 474808
nbits = 19  # The height of the tree

# Size of the PRF values (in bits)
nbits_rng = 1


def prng(K):
    random.seed(K)
    randbits = random.getrandbits(2*nbits_rng)
    # print("{:b}".format(randbits))
    G0 = randbits >> nbits
    G1 = randbits & ((1 << nbits_rng) - 1)
    # print("{:b} :: {:b}".format(G0, G1))
    return G0, G1


def GMM(K, idx):
    curr = K
    # iterate through the bits of idx padded to nbits
    for b in bin(idx)[2:].zfill(nbits):
        G0, G1 = prng(curr)
        if b == '0':
            curr = G0
        elif b == '1':
            curr = G1
    return curr


def compute_node(K, s):
    # print("Computing node at : " + s)
    curr = K
    for b in s:
        # print(b)
        G0, G1 = prng(curr)
        if b == '0':
            curr = G0
        elif b == '1':
            curr = G1
    return curr


# Return Kx, the punctured key that allows evaluation
# everywhere but on idx = x
# Format of the punctured key:
# [(neighbor, neighbor value) for neighbor in path_to_x] + [(x, v)]
def puncture(K, x, v):
    # find the neighbors of the nodes in the path from root to x
    Nx = []
    curr = 0
    level = 1
    for b in bin(x)[2:].zfill(nbits):
        curr = curr << 1
        neigh = curr | (1 - int(b))
        neigh = bin(neigh)[2:].zfill(level)
        Nx.append(neigh)
        curr |= int(b)
        level += 1

    punctured_key = []
    for n in Nx:
        punctured_key.append((n, compute_node(K, n)))

    punctured_key.append((x, v))
    return punctured_key


def Eval(punctured_key, idx):
    # print("Requesting idx : {} from punctured key".format(idx))
    is_punctured_point = True
    for i in range(nbits):
        bits = bin(idx)[2:].zfill(nbits)
        node = bits[:nbits - i]
        left = bits[nbits-i:]
        (n, n_value) = punctured_key[nbits - i - 1]
        # print("Current level : {}. Known value at that level : {}".format(node, n))
        # print("Left to eval : {}".format(left))
        if (node == n):
            is_punctured_point = False
            # print("Anchor point found at level {}".format(nbits - i))
            curr = n_value
            for b in left:
                G0, G1 = prng(curr)
                if b == '0':
                    curr = G0
                elif b == '1':
                    curr = G1
            return curr
    if is_punctured_point:
        x, v = punctured_key[-1]
        assert(idx == x)
        # print("Punctured point requested")
        return v


if __name__ == "__main__":
    KEY = 10

    pk = puncture(KEY, 3, 999)

    print("Direct eval : {}. Eval with pk : {}".format(GMM(KEY, 5), Eval(pk, 5)))
    print("Direct eval : {}. Eval with pk : {}".format(GMM(KEY, 6), Eval(pk, 6)))
    print("Direct eval : {}. Eval with pk : {}".format(GMM(KEY, 7), Eval(pk, 7)))
    print("Direct eval : {}. Eval with pk : {}".format(
        GMM(KEY, 85), Eval(pk, 85)))
    print("Direct eval : {}. Eval with pk : {}".format(GMM(KEY, 3), Eval(pk, 3)))
