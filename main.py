import abc
import typing
import numpy as np
import itertools
import random


class Board:
	VizTiles = "_░█"

	def __init__(self, n):
		self.N = n
		self.Moves = {
			"p": self.place,
			"fr": self.flip_row,
			"fc": self.flip_column,
			"il": self.insert_left,
			"ir": self.insert_right,
			"it": self.insert_top,
			"ib": self.insert_bottom,
		}
		self.MoveDescription = {
			"p": "Player {player} places tile {2} at column {0}, row {1}.",
			"fr": "Player {player} flips row {0}.",
			"fc": "Player {player} flips column {0}.",
			"il": "Player {player} inserts tile {1} to the left of row {0}.",
			"ir": "Player {player} inserts tile {1} to the right of row {0}.",
			"it": "Player {player} inserts tile {1} at the top of column {0}.",
			"ib": "Player {player} inserts tile {1} at the bottom of column {0}.",
		}

	def empty_state(self):
		"""
		Generate empty board state
		"""
		return tuple(0 for _ in range(self.N**2))

	def random_state(self):
		"""
		Generate random board state
		"""
		return tuple(random.choice([0,1,2]) for _ in range(self.N**2))

	def state_from_string(self, s, tiles=None):
		"""
		Create state from string representation
		"""
		m = {t: i for i, t in itertools.chain(enumerate(self.VizTiles), enumerate("_XO"), enumerate("012"))}
		if tiles:
			assert len(tiles) == 3
			assert " " not in tiles
			assert "\n" not in tiles
		return tuple(
			m[t]
			for t in s.strip().replace("\n", "")
		)
	
	
	def viz(self, s):
		"""
		Visualize board state
		"""
		out = []
		for i, f in enumerate(s):
			if i and not i % self.N:
				out.append("\n")
			out.append(self.viz_tile(f))
		return "".join(out)
	
	def viz_tile(self, tile):
		"""
		Visualize tile
		"""
		return self.VizTiles[tile]*2

	def rotate_board_left(self, s):
		"""
		Rotate the entire board 90 degrees to the left
		"""
		return tuple(
			s[col*self.N+row]
			for row in range(self.N)
			for col in range(self.N-1, -1, -1)
		)

	def rotate_board_right(self, s):
		"""
		Rotate the entire board 90 degrees to the right
		"""
		return tuple(
			s[col*self.N+row]
			for row in range(self.N-1, -1, -1)
			for col in range(self.N)
		)

	def reflect_board_vertically(self, s):
		"""
		Flip the entire board horizontally
		"""
		return tuple(
			s[col*self.N+row]
			for col in range(self.N)
			for row in range(self.N-1, -1, -1)
		)

	def reflect_board_horizontally(self, s):
		"""
		Flip the entire board horizontally
		"""
		return tuple(
			s[col*self.N+row]
			for col in range(self.N-1, -1, -1)
			for row in range(self.N)
		)
	
	def generate_equivalent_states(self, s) -> typing.List[typing.Tuple[int]]:
		"""
		Generate a list of all possible rotated and reflected states which are equivalent to the input state.
		"""
		states = {s}

		# Mirror
		s_ = self.reflect_board_vertically(s)
		states.add(s_)
		
		# Rotations
		for sx in [s, s_]:
			for _ in range(3):
				sx = self.rotate_board_left(sx)
				states.add(sx)

		# Sort
		states = sorted(states)
			
		return states
	
	def place(self, s, col, row, color):
		"""
		Place a tile at an empty position
		"""
		assert s[self.N*row+col] == 0
		return tuple(
			c if (i != self.N*row+col) else color
			for i, c in enumerate(s)
		)

	def flip_row(self, s, row):
		"""
		Invert all tiles in a selected row
		"""
		return tuple(
			(-c % 3) if (i // self.N == row) else c
			for i, c in enumerate(s)
		)

	def flip_column(self, s, col):
		"""
		Invert all tiles in a selected column
		"""
		return tuple(
			(-c % 3) if (i % self.N == col) else c
			for i, c in enumerate(s)
		)

	def insert_left(self, s, row, color):
		"""
		Insert a tile at the left side of a selected row, pushing the entire row to the right 
		and discarding the rightmost tile.
		"""
		new = (
			s[:self.N*row] 
			+ (color,) + s[self.N*row:self.N*(row+1)-1] 
			+ s[self.N*(row+1):]
		)
		return tuple(new)

	def insert_right(self, s, row, color):
		"""
		Insert a tile at the right side of a selected row, pushing the entire row to the left 
		and discarding the leftmost tile.
		"""
		new = (
			s[:self.N*row] 
			+ s[self.N*row+1:self.N*(row+1)] + (color,)
			+ s[self.N*(row+1):]
		)
		return tuple(new)

	def insert_top(self, s, col, color):
		"""
		Insert a tile at the top of a selected column, pushing the entire column down
		and discarding the bottom-most tile.
		"""
		new = []
		for i, c in enumerate(s):
			if i % self.N != col:
				new.append(c)
			elif i < self.N:
				new.append(color)
			else:
				new.append(s[i-self.N])
		return tuple(new)

	def insert_bottom(self, s, col, color) -> typing.Tuple[int]:
		"""
		Insert a tile at the bottom of a selected column, pushing the entire column up
		and discarding the topmost tile.
		"""
		new = []
		for i, c in enumerate(s):
			if i % self.N != col:
				new.append(c)
			elif i >= self.N*(self.N-1):
				new.append(color)
			else:
				new.append(s[i+self.N])
		return tuple(new)
	
	def get_winners(self, s) -> typing.Set[int]:
		"""
		Check if the state is a terminal state and return the set of winning colors.
		If the state is not terminal, the set is empty.
		If there is exactly one winner, the set contains one element.
		If the state is a tie, the set contains two elements.
		"""
		winners = set()
		# Rows
		for row in range(self.N):
			v = s[row*self.N]
			if v == 0:
				continue
			for i in range(row*self.N+1, (row+1)*self.N):
				if s[i] != v:
					break
			else:
				winners.add(v)

		# Columns
		for col in range(self.N):
			v = s[col]
			if v == 0:
				continue
			for i in range(1, self.N):
				if s[col + i*self.N] != v:
					break
			else:
				winners.add(v)

		return winners
	
	def generate_possible_moves(
		self, 
		s, 
		colors=frozenset({1, 2}), 
		moves=frozenset({"p", "fr", "fc", "il", "ir", "it", "ib"}),
	) -> typing.Generator[typing.Tuple[typing.Tuple, typing.Tuple[int]]]:
		"""
		Iterate through all possible moves from a given state.
		"""
		for move in moves:
			# Place
			if move == "p":
				for col, row, color in itertools.product(range(self.N), range(self.N), colors):
					if s[self.N*row+col] != 0:
						# Not empty
						continue
					s_next = self.Moves[move](s, col, row, color)
					move_args = (move, col, row, color)
					yield (move_args, s_next)
			
			# Flip
			elif move in {"fr", "fc"}:
				for i in range(self.N):
					s_next = self.Moves[move](s, i)
					move_args = (move, i)
					yield (move_args, s_next)
			
			# Insert
			elif move in {"il", "ir", "it", "ib"}:
				for i, color in itertools.product(range(self.N), colors):
					s_next = self.Moves[move](s, i, color)
					move_args = (move, i, color)
					yield (move_args, s_next)

			else:
				raise ValueError(f"Unknown move: {move}")
			
	def exclude_forbidden_moves(
		self,
		state_generator, 
		forbidden_states=frozenset(),
	) -> typing.Generator[typing.Tuple[typing.Tuple, typing.Tuple[int]]]:
		for m, s in state_generator:
			if s in forbidden_states:
				continue
			yield (m, s)

	def describe_move(self, move, player):
		m, *args = move
		if m == "p":
			args = list(args)
			args[2] = self.viz_tile(args[2])
		elif m.startswith("i"):
			args = list(args)
			args[1] = self.viz_tile(args[1])
		return self.MoveDescription[m].format(*args, player=player)

	def play_game(self, players: typing.Sized, s=None):
		"""
		Two players take turns in making random moves until a terminal state is reached
		"""
		assert len(players) == 2
		if not s:
			s = self.empty_state()

		players = [PlayerRandom(self) for _ in range(2)]
		player_i = 2
		s_prev = s
		winners = set()
		print("New game.")
		self.viz(s)
		print()
		while not winners:
			player_i = (-player_i % 3)
			moves = [
				(move, s_next) 
				for (move, s_next) in self.exclude_forbidden_moves(
					self.generate_possible_moves(s, colors={player_i}), forbidden_states={s, s_prev}
				)
			]
			move, s_next = players[player_i-1].make_move(s, moves)
			print(self.describe_move(move, player_i))
			print(self.viz(s_next))
			print()

			s_prev = s
			s = s_next
			winners = self.get_winners(s)

		if len(winners) == 1:
			print("Player {} wins!".format(winners.pop()))
		else:
			print("It's a tie!")


class PlayerABC(abc.ABC):
	def __init__(self, board: Board):
		self.Board = board

	def make_move(self, s, moves):
		raise NotImplementedError()
	

class PlayerRandom(PlayerABC):
	def make_move(self, s, moves):
		return random.choice(moves)


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



def main():
	b = Board(4)
	b.play_game(players=[PlayerRandom(b), PlayerRandom(b)])


if __name__ == "__main__":
	main()
