import random
import string
import subprocess

import numpy as np

import config

LIB_PATH = config.SHARED_FOLDER + "libdpf/"
FSSGEN_PATH = LIB_PATH + "fssgen"
FSSEVAL_PATH = LIB_PATH + "fsseval"


def dpf_gen_keys(alpha, nbits):
    cmd = [FSSGEN_PATH, str(nbits), str(alpha)]
    subprocess.run(cmd, capture_output=True, text=True)
    with open("k0", "rb") as fd:
        k0 = fd.read()
    with open("k1", "rb") as fd:
        k1 = fd.read()
    return (k0, k1)


def dpf_eval_full(key, nbits):
    # Generate a random key name
    letters = string.ascii_letters
    temp_key_filename = "/tmp/key_" + \
        ''.join(random.choice(letters) for i in range(10))
    # print(temp_key_filename)
    with open(temp_key_filename, "wb") as fd:
        fd.write(key)
    cmd = [FSSEVAL_PATH, str(nbits), temp_key_filename]
    res = subprocess.run(cmd, capture_output=True, text=True).stdout
    vect = np.frombuffer(bytes(res, 'utf-8'), 'u1') - ord('0')
    return vect


if __name__ == "__main__":
    (k0, k1) = dpf_gen_keys(123)
    # print(k0)
    # print(k1)
    vect0 = dpf_eval_full(k0)
    vect1 = dpf_eval_full(k1)

    print(vect0[123])
    print(vect1[123])
