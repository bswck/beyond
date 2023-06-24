from __future__ import annotations
from collections import UserDict
from collections.abc import Sequence
from typing import ClassVar, TypeAlias, Generic, TypeVar, Any

from beyond.dimension import Dimension

T = TypeVar("T", str, int)
ShapeType = tuple[Dimension, ...]
InsightResolverT = dict[T, T | tuple[T, ...]]
BoardStateVT: TypeAlias = "BoardAxis | Any"


class BoardState(UserDict[tuple[T, ...], BoardStateVT]):
    dims: ShapeType

    def __init__(self, shape: ShapeType):
        super().__init__()
        self.dims = shape

    @property
    def ndim(self) -> int:
        return len(self.dims)

    def _validate_key_ndim(
        self,
        *,
        key: T | tuple[T, ...],
        verb: str = "access",
        allow_insights: bool = True
    ) -> tuple[tuple[T, ...], int]:
        if not isinstance(key, tuple):
            key = (key,)
        ndim = len(key)
        expected_shape = ", ".join("?" * self.ndim).join("()")
        if ndim > self.ndim:
            raise IndexError(
                f"Cannot {verb} a {ndim}-dimensional board entity "
                f"in a {self.ndim}-dimensional board (got key: {key}; expected a key like: {expected_shape})"
            )
        if not allow_insights:
            if ndim < self.ndim:
                raise NotImplementedError(
                    f"Cannot {verb} a {ndim}-dimensional board entity "
                    f"in a {self.ndim}-dimensional board (got key: {key}; expected a key like: {expected_shape})"
                )
        indices = []
        for size in range(ndim):
            dim = self.dims[size]
            index = dim.get_axis_index(key[size])
            if index < 0:
                index += dim.size
            if index >= dim.size:
                raise IndexError(
                    f"axe index {index} is out of bounds: "
                    f"dimension {dim.name!r} has only {dim.size} axes"
                )
            indices.append(index)
        return tuple(indices), ndim

    def __setitem__(self, key: T | tuple[T, ...], value):
        key, ndim = self._validate_key_ndim(key=key, verb="set")
        if ndim == self.ndim:
            self.data[key] = value
        else:
            path = key[:ndim]
            dim = self.dims[ndim]
            if not isinstance(value, Sequence):
                value = [value] * dim.size
            if len(value) != dim.size:
                raise ValueError(
                    f"Cannot set {ndim}-dimensional board entity "
                    f"with a value of size {len(value)} "
                    f"in a {self.ndim}-dimensional board "
                    f"with axes of length {dim.size}"
                    f"(raised for key: {key})"
                )
            for i in range(dim.size):
                self[(*path, i)] = value[i]

    def __getitem__(self, key: T | tuple[T, ...]):
        key, ndim = self._validate_key_ndim(key=key)
        if ndim == self.ndim:
            return self.data[key]
        else:
            return BoardAxis(
                state=self,
                path=key[:ndim],
                dim=self.dims[ndim],
            )


class BoardInsight(Generic[T]):
    def __init__(
        self,
        *,
        state: BoardState,
        resolver: InsightResolverT,
        read_only: bool = False,
    ):
        self.state = state
        self.resolver = resolver
        self.read_only = read_only

    def __getitem__(self, key: T) -> T:
        resolved_key = self.resolver[key]
        return self.state[resolved_key]

    def __setitem__(self, key: T, value: T):
        if self.read_only:
            raise TypeError("Cannot set a readonly insight")
        loc = self.resolver[key]
        self.state[loc] = value

class BoardAxis(Generic[T]):
    def __init__(
        self,
        *,
        state: BoardState,
        read_only: bool = False,
        path: tuple[T, ...],
        dim: Dimension,
    ):
        self.state = state
        self.path = path
        self.dim = dim
        self.read_only = read_only

    @property
    def size(self) -> T:
        return self.dim.size

    def _resolve_index(self, key: T) -> int:
        idx = key
        if isinstance(key, str):
            idx = self.dim.get_axis_index(key)
        return idx

    def __getitem__(self, key: T) -> T:
        idx = self._resolve_index(key)
        if idx < 0:
            idx += self.size
        return self.state[(*self.path, idx)]

    def __setitem__(self, key: T, value: T):
        if self.read_only:
            raise TypeError("Cannot set a readonly insight")
        idx = self._resolve_index(key)
        if idx < 0:
            idx += self.size
        self.state[(*self.path, idx)] = value

    def __repr__(self):
        path = self.path
        size = self.size
        return f"{type(self).__name__}({path=!r}, {size=!r})"

class Board(Generic[T]):
    DEFAULT_SHAPE: ClassVar[ShapeType]

    def __init__(
        self,
        *dims: int | Dimension,
    ):
        if not dims:
            dims = self.DEFAULT_SHAPE
        else:
            dims = tuple(
                dim_or_size
                if isinstance(dim_or_size, Dimension)
                else Dimension.with_size(dim_or_size)
                for dim_or_size in dims
            )
        self.state = BoardState[T](dims)

    @property
    def dimensions(self) -> tuple[Dimension, ...]:
        return self.dims

    @property
    def dims(self) -> tuple[Dimension, ...]:
        return self.state.dims

    def __getitem__(self, key):
        return self.state[key]

    def __setitem__(self, key, value):
        self.state[key] = value

    def __str__(self):
        return str(self.state)
