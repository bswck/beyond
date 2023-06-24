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
    shape: ShapeType

    def __init__(self, shape: ShapeType):
        super().__init__()
        self.shape = shape

    @property
    def ndim(self) -> int:
        return len(self.shape)

    def _validate_key_ndim(
        self,
        *,
        key: T | tuple[T, ...],
        action: str = "access",
        disallow_insights: bool = False
    ) -> tuple[tuple[T, ...], int]:
        if not isinstance(key, tuple):
            key = (key,)
        ndim = len(key)
        expected_shape = ", ".join("?" * self.ndim).join("()")
        if ndim > self.ndim:
            raise IndexError(
                f"Cannot {action} a {ndim}-dimensional board entity "
                f"in a {self.ndim}-dimensional board (got key: {key}; expected a key like: {expected_shape})"
            )
        if disallow_insights:
            if ndim < self.ndim:
                raise NotImplementedError(
                    f"Cannot {action} a {ndim}-dimensional board entity "
                    f"in a {self.ndim}-dimensional board (got key: {key}; expected a key like: {expected_shape})"
                )
        indices = []
        for size in range(ndim):
            dim = self.shape[size]
            indices.append(dim.get_axis_index(key[size]))
        return tuple(indices), ndim

    def __setitem__(self, key: T | tuple[T, ...], value):
        key, ndim = self._validate_key_ndim(key=key, action="set")
        if ndim == self.ndim:
            self.data[key] = value
        else:
            nest = key[:ndim]
            dim = self.shape[ndim]
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
                self.data[(*nest, i)] = value[i]

    def __getitem__(self, key: T | tuple[T, ...]):
        key, ndim = self._validate_key_ndim(key=key)
        if ndim == self.ndim:
            return self.data[key]
        else:
            return BoardAxis(
                state=self,
                path=key[:ndim],
                dim=self.shape[ndim],
            )


class BoardInsight(Generic[T]):
    def __init__(
        self,
        *,
        state: BoardState,
        resolver: InsightResolverT,
        readonly: bool = False,
    ):
        self.state = state
        self.resolver = resolver
        self.read_only = readonly

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
        return f"{type(self).__name__}(nest={self.path!r}, size={self.size!r})"


class Board(Generic[T]):
    DEFAULT_SHAPE: ClassVar[ShapeType]

    def __init__(
        self,
        *shape: int
    ):
        if not shape:
            shape = self.DEFAULT_SHAPE
        else:
            shape = tuple(
                argument if isinstance(argument, Dimension) else Dimension.with_size(argument)
                for argument in shape
            )
        self.state = BoardState[T](shape)

    def __getitem__(self, key):
        return self.state[key]

    def __setitem__(self, key, value):
        self.state[key] = value

    def __str__(self):
        return str(self.state)
