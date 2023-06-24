from __future__ import annotations
from collections import UserDict
from collections.abc import Sequence
from typing import ClassVar, TypeAlias, Generic, TypeVar

from beyond.dimension import Dimension, TicTacToeDimension

InsightValueT = TypeVar("InsightValueT")
ShapeType: TypeAlias = tuple[Dimension, ...]
InsightResolverT: TypeAlias = dict[int, int | tuple[int, ...]]


class BoardState(UserDict):
    def __init__(self, shape: ShapeType):
        super().__init__()
        self.shape = shape

    @property
    def ndim(self) -> int:
        return len(self.shape)

    def _validate_key_ndim(
        self,
        *,
        key: int | tuple[int, ...],
        action: str = "access",
        disallow_insights: bool = False
    ) -> tuple[tuple[int, ...], int]:
        if isinstance(key, int):
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
        return key, ndim

    def __setitem__(self, key, value):
        key, ndim = self._validate_key_ndim(key=key, action="set")
        if ndim == self.ndim:
            self.data[key] = value
        else:
            nest = key[:ndim]
            if not isinstance(value, Sequence):
                value = [value] * self.shape[ndim].size
            if len(value) != self.shape[ndim].size:
                raise ValueError(
                    f"Cannot set {ndim}-dimensional board entity "
                    f"with a value of size {len(value)} "
                    f"in a {self.ndim}-dimensional board "
                    f"with axes of length {self.shape[ndim].size}"
                    f"(raised for key: {key})"
                )
            for i in range(self.shape[ndim].size):
                self[(*nest, i)] = value[i]

    def __getitem__(self, key: int | tuple[int, ...]):
        key, ndim = self._validate_key_ndim(key=key)
        if ndim == self.ndim:
            return self.data[key]
        else:
            nest = key[:ndim]
            resolver = {
                resolved_key[-1]: resolved_key
                for resolved_key in self
                if resolved_key[:-1] == nest
            }
            return BoardAxis(
                state=self,
                resolver=resolver,
                nest=nest,
                size=self.shape[ndim].size,
            )


class BoardInsight(Generic[InsightValueT]):
    def __init__(
        self,
        *,
        state: BoardState,
        resolver: InsightResolverT,
        readonly: bool = False,
    ):
        self.state = state
        self.resolver = resolver
        self.readonly = readonly

    def __getitem__(self, key: int) -> InsightValueT:
        resolved_key = self.resolver[key]
        return self.state[resolved_key]

    def __setitem__(self, key: int, value: InsightValueT):
        if self.readonly:
            raise TypeError("Cannot set a readonly insight")
        loc = self.resolver[key]
        self.state[loc] = value


class BoardAxis(BoardInsight[InsightValueT]):
    def __init__(
        self,
        *,
        state: BoardState,
        resolver: InsightResolverT,
        readonly: bool = False,
        nest: tuple[int, ...],
        size: int,
    ):
        super().__init__(
            state=state,
            resolver=resolver,
            readonly=readonly
        )
        self.nest = nest
        self.size = size

    def __getitem__(self, key: int) -> InsightValueT:
        if key < 0:
            key += self.size
        resolved_key = self.resolver.get(key)
        if resolved_key is None:
            if key >= self.size:
                raise IndexError(f"Index {key} is out of bounds for axis at {self.nest}")
            resolved_key = (*self.nest, key)
        return self.state[resolved_key]

    def __setitem__(self, key: int, value: InsightValueT):
        if self.readonly:
            raise TypeError("Cannot set a readonly insight")
        if key < 0:
            key += self.size
        loc = self.resolver.get(key)
        if loc is None:
            if key >= self.size:
                raise IndexError(f"Index {key} is out of bounds for axis at {self.nest}")
            loc = (*self.nest, key)
        self.state[loc] = value

    def __repr__(self):
        return f"{type(self).__name__}(nest={self.nest!r}, size={self.size!r})"


class Board:
    DEFAULT_SHAPE: ClassVar[ShapeType] = TicTacToeDimension.default_shape()

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
        self.state = BoardState(shape)

    def __getitem__(self, key):
        return self.state[key]

    def __setitem__(self, key, value):
        self.state[key] = value

    def __str__(self):
        return str(self.state)
