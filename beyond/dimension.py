from typing import ClassVar


class Dimension:
    default_name: ClassVar[str]
    default_size: ClassVar[int | None] = None

    def __init__(
        self,
        name: str | None = None,
        size: int | None = None,
    ):
        if name is None:
            name = self.default_name
        if size is None:
            size = self.default_size

        if name is None:
            raise ValueError("Name must be specified")
        self.name = name
        if size is None:
            raise ValueError("Size must be specified")
        self.size = size

    @classmethod
    def default_shape(cls, *, default_size: int | None = None) -> tuple["Dimension", ...]:
        return cls("rows", default_size), cls("columns", default_size)

    def get_axis_name(self, size: int) -> str:
        return f"{self.name}_{size}"

    @classmethod
    def with_size(cls, size: int):
        return cls("dim", size)

    def __repr__(self):
        return f"Dimension(name={self.name!r}, size={self.size!r})"


class TicTacToeDimension(Dimension):
    default_size = 3


class ChessDimension(Dimension):
    default_size = 8


class ChessRankDimension(ChessDimension):
    default_name = "ranks"

    def get_axis_name(self, idx: int) -> str:
        return str(idx)


class ChessFileDimension(ChessDimension):
    default_name = "files"
    files = "abcdefgh"

    def get_axis_name(self, idx: int) -> str:
        return self.files[idx]


CHESS_SHAPE = (
    ChessRankDimension(),
    ChessFileDimension(),
)
