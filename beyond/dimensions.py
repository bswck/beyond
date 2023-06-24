from beyond.dimension import Dimension


def square_shape(size: int) -> tuple[Dimension, ...]:
    return (
        Rows(size=size),
        Columns(size=size),
    )


class Rows(Dimension):
    default_name = "rows"


class Columns(Dimension):
    default_name = "columns"
