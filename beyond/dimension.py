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
        self.index: dict[str, int] = {}
        self.setup()

    def setup(self):
        for idx in range(self.size):
            self.get_axis_name(idx)

    @classmethod
    def default_shape(cls, *, default_size: int | None = None) -> tuple["Dimension", ...]:
        return cls("rows", default_size), cls("columns", default_size)

    def get_axis_name(self, idx: int) -> str:
        name = self.create_axis_name(idx)
        self.index.setdefault(name, idx)
        return name

    def get_axis_index(self, name: str | int) -> int:
        if isinstance(name, int):
            # This is not a name, but the desired index
            return name
        try:
            return self.index[name]
        except KeyError:
            raise ValueError(f"Unknown name in {self.name}: {name!r}")

    def create_axis_name(self, size: int) -> str:
        return f"{self.name}_{size}"

    @classmethod
    def with_size(cls, size: int):
        return cls("dim", size)

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r}, size={self.size!r})"
