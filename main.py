import numpy as np
import itertools


N = 4

graph = {}  # (state, move) -> state
states = {}  # state -> meta


def generate_all_states():
	n_fields = N * N
	yield from itertools.product(range(3), repeat=n_fields)


def unpack_state(s):
	return np.resize(s, (N, N))


def remove_rotations():
	new = {}
	for s in states:





def main():
	...


if __name__ == "__main__":
	main()
