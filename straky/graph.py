import itertools
from .board import Board


class GameGraph:
	def __init__(self, board: Board):
		self.Board = board
		self.NormalizedStates = None
		self.Graph = None
		self.Terminals = None

	def prepare_normalized_states(self):
		self.NormalizedStates = {}  # state -> normalized_state

		for i, s in enumerate(itertools.product(range(3), repeat=self.Board.N**2)):
			if not i % 1000000:
				print(i)
			if s in self.NormalizedStates:
				continue
			eqs = self.Board.generate_equivalent_states(s)
			for s_ in eqs:
				self.NormalizedStates[s_] = eqs[0]

	def save_normalized_states(self, fname):
		assert self.NormalizedStates

		with open(fname, "w") as f:
			for k, v in self.NormalizedStates.items():
				if k == v:
					continue
				print("{} {}".format(
					int("".join(str(c) for c in k), 3),
					int("".join(str(c) for c in v), 3)
				), file=f)

	def load_normalized_states(self, fname):
		self.NormalizedStates = {}
		with open(fname) as f:
			for line in f:
				k, v = line.split(" ")
				self.NormalizedStates[number_to_base(int(k), 3, length=self.Board.N**2)] = number_to_base(int(v), 3, length=self.Board.N**2)
		return self.NormalizedStates
	
	def normalize_state(self, s):
		if s not in self.NormalizedStates:
			return s
		return self.NormalizedStates[s]
	
	def build_graph(self):
		# TODO: use networkx
		assert self.NormalizedStates is not None

		self.Graph = {}  # state -> ((move, *args) -> state)
		self.Terminals = {}

		s_init = self.Board.empty_state()
		frontier = {s_init}

		while frontier:
			s = frontier.pop()

			# Check if state is terminal
			winners = self.Board.get_winners(s)
			if winners:
				self.Graph[s] = None
				self.Terminals[s] = winners
				continue

			for move, s_next in self.Board.generate_possible_moves(s):
				s_next = self.normalize_state(s_next)
				if s not in self.Graph:
					self.Graph[s] = {}
				self.Graph[s][move] = s_next

				# Add unexplored
				if s_next not in self.Graph:
					frontier.add(s_next)


def number_to_base(n, b, length):
	# https://stackoverflow.com/questions/2267362/how-to-convert-an-integer-to-a-string-in-any-base
	digits = []
	while n:
		digits.append(int(n % b))
		n //= b
	while len(digits) < length:
		digits.append(0)
	return tuple(digits[::-1])
