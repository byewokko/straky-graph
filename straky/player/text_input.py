import re
from .abc import PlayerABC


class PlayerTextInput(PlayerABC):
	def make_move(self, s, moves):
		move = self.parse_user_input(input("> "))
		return move
	
	def parse_user_input(self, user_input):
		command = user_input.strip().split(" ")

		if command[0] == "flip":
			assert len(command) == 2
			what = command[1]
			if what.isalpha():
				assert len(what) == 1
				move = "fc"
				col = ord(what.upper()) - ord("A")
				return (move, col)
			elif what.isdigit():
				move = "fr"
				row = int(what) - 1
				return (move, row)
			else:
				raise ValueError(f"Unknown command: {user_input}")
			
		elif command[0] == "push":
			assert len(command) == 3
			what = command[1]
			where = command[2]
			if what.isalpha():
				assert len(what) == 1
				col = ord(what.upper()) - ord("A")
				if where == "up":
					move = "ib"
				elif where == "down":
					move = "it"
				else:
					raise ValueError(f"Unknown command: {user_input}")
				return (move, col, self.Color)
			elif what.isdigit():
				row = int(what) - 1
				if where == "left":
					move = "ir"
				elif where == "right":
					move = "il"
				else:
					raise ValueError(f"Unknown command: {user_input}")
				return (move, row, self.Color)
			else:
				raise ValueError(f"Unknown command: {user_input}")
			
		elif len(command) == 1:
			match = re.match("([a-zA-Z])([0-9]+)", command[0])
			if not match:
				raise ValueError(f"Unknown command: {user_input}")
			col, row = match.groups()
			col = ord(col.upper()) - ord("A")
			row = int(row) - 1
			move = "p"
			return (move, col, row, self.Color)
		
		else:
			raise ValueError(f"Unknown command: {user_input}")
