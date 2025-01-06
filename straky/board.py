import typing
import random
import itertools


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
		out.append("  ")
		for i in range(self.N):
			out.append("{} ".format(col_letter(i)))
		for i, f in enumerate(s):
			if not i % self.N:
				out.append("\n{:<2}".format(row_number(i // self.N)))
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
			return "Player {} places tile {} at {}{}.".format(
				player, 
				self.viz_tile(args[2]), 
				col_letter(args[0]), 
				row_number(args[1]),
			)
		elif m == "fc":
			return "Player {} flips column {}.".format(
				player, 
				col_letter(args[0]), 
			)
		elif m == "fr":
			return "Player {} flips row {}.".format(
				player, 
				row_number(args[0]),
			)
		elif m == "it":
			return "Player {} pushes column {} down with tile {}.".format(
				player, 
				col_letter(args[0]), 
				self.viz_tile(args[1]), 
			)
		elif m == "ib":
			return "Player {} pushes column {} up with tile {}.".format(
				player, 
				col_letter(args[0]), 
				self.viz_tile(args[1]), 
			)
		elif m == "il":
			return "Player {} pushes row {} right with tile {}.".format(
				player, 
				row_number(args[0]), 
				self.viz_tile(args[1]), 
			)
		elif m == "ir":
			return "Player {} pushes row {} left with tile {}.".format(
				player, 
				row_number(args[0]), 
				self.viz_tile(args[1]), 
			)
		else:
			raise ValueError(f"Unknown move: {m}")

	def play_game(self, players: typing.Sized, s=None):
		"""
		Two players take turns in making moves until a terminal state is reached
		"""
		assert len(players) == 2
		for i, p in enumerate(players):
			p.set_board(self)
			if not p.Color:
				p.set_color(i + 1)

		if not s:
			s = self.empty_state()

		player_i = 2
		s_prev = s
		winners = set()
		print("New game.")
		self.viz(s)
		print()
		while not winners:
			player_i = (-player_i % 3)
			valid_moves = {
				move: s_next
				for (move, s_next) in self.exclude_forbidden_moves(
					self.generate_possible_moves(s, colors={player_i}), forbidden_states={s, s_prev}
				)
			}
			move = players[player_i-1].make_move(s, valid_moves)
			while move not in valid_moves:
				print("Invalid move.")
				move = players[player_i-1].make_move(s, valid_moves)
			
			s_next = valid_moves[move]
			
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


def col_letter(i):
	return chr(ord("A") + i)


def row_number(i):
	return i + 1
