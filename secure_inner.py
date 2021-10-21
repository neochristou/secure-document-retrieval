import numpy as np

# n = 1000
n = 10
m = 2 ** 16

print()


def TrustedInitializer():
    x0 = np.random.rand(1, n) * m
    y0 = np.random.rand(1, n) * m

    for_alice = x0
    for_bob = (y0, np.inner(x0, y0))
    return for_alice, for_bob


for_alice, for_bob = TrustedInitializer()

# alice_input = np.random.rand(1, n) * m  # One line of the tf-idf matrix
# bob_input = np.random.rand(1, n) * m  # The client's request vector
alice_input = np.full((1, n), 0.25) * m  # One line of the tf-idf matrix
bob_input = np.full((1, n), 0.5) * m  # The client's request vector

# Bob's computation (client)
y = bob_input
y0, s0 = for_bob
y1 = y - y0
# send y1 to Alice
# Alice's computation (server)
x = alice_input
x0 = for_alice
# receives y1
x1 = x + x0
r = np.random.rand(1, 1) * m
r1 = np.inner(x, y1) - r
u = r
# send (x1, r1) to Bob

# Bob's computation (client)
v = np.inner(x1, y0) + r1 - s0
# send y1 to Alice

print(u+v)
print(np.inner(x, y))
