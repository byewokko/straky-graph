import typing
import abc
from ..board import Board


class PlayerABC(abc.ABC):
	def __init__(self, *, board = None, color = None, **kwargs):
		self.Board: typing.Optional[Board] = board
		self.Color: typing.Optional[int] = color

	def set_board(self, board: Board):
		self.Board = board

	def set_color(self, color: int):
		self.Color = color

	def make_move(self, s, moves: dict):
		raise NotImplementedError()
