from beyond.dimension import Dimension


class ChessDimension(Dimension):
    default_size = 8

    @classmethod
    def default_shape(cls, *, default_size: int | None = None) -> tuple["Dimension", ...]:
        return (
            ChessFileDimension(size=default_size),
            ChessRankDimension(size=default_size),
        )


class ChessRankDimension(ChessDimension):
    default_name = "ranks"

    def create_axis_name(self, idx: int) -> str:
        return str(idx)


class ChessFileDimension(ChessDimension):
    default_name = "files"
    files = "abcdefgh"

    def create_axis_name(self, idx: int) -> str:
        return self.files[idx]
