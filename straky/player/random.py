import random
from .abc import PlayerABC


class PlayerRandom(PlayerABC):
	def make_move(self, s, moves):
		return random.choice(list(moves))
