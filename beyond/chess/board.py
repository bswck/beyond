from beyond.board import Board
from beyond.chess.dimensions import ChessDimension


class ChessBoard(Board):
    DEFAULT_SHAPE = ChessDimension.default_shape()
