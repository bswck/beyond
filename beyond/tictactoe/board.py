from beyond.board import Board
from beyond.dimensions import square_shape


class TicTacToeBoard(Board):
    DEFAULT_SHAPE = square_shape(3)
