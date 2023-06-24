from beyond.dimension import Dimension


class ChessDimension(Dimension):
    default_size = 8

    @classmethod
    def default_shape(cls, *, default_size: int | None = None) -> tuple["Dimension", ...]:
        return (
            ChessFiles(size=default_size),
            ChessRanks(size=default_size),
        )


class ChessRanks(ChessDimension):
    default_name = "ranks"

    def create_axis_name(self, idx: int) -> str:
        return str(idx)


class ChessFiles(ChessDimension):
    default_name = "files"
    files = "abcdefgh"

    def create_axis_name(self, idx: int) -> str:
        return self.files[idx]

    def get_axis_index(self, name: str | int) -> int:
        if isinstance(name, str):
            name = name.casefold()
        return super().get_axis_index(name)
