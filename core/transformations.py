"""
Transformations module demonstrating OOP Inheritance and Polymorphism.
Base abstract class Transformation defines the contract. Subclasses implement
specific transformation behavior (Swap, Rotate, Flip).
"""

from abc import ABC, abstractmethod
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.board import Board


class Transformation(ABC):
    """
    Abstract base class for all tile transformations.
    Demonstrates inheritance and polymorphic apply() method.
    """

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def apply(self, board: 'Board') -> None:
        """Apply transformation to the board."""
        pass


class SwapTransformation(Transformation):
    """Exchanges positions of two tiles on the board."""

    def __init__(self, pos1: Tuple[int, int], pos2: Tuple[int, int]):
        super().__init__("Swap")
        self._pos1 = pos1
        self._pos2 = pos2

    @property
    def pos1(self) -> Tuple[int, int]:
        return self._pos1

    @property
    def pos2(self) -> Tuple[int, int]:
        return self._pos2

    def apply(self, board: 'Board') -> None:
        r1, c1 = self._pos1
        r2, c2 = self._pos2
        board.swap_tiles(r1, c1, r2, c2, record_move=False)


class RotateTransformation(Transformation):
    """Rotates a tile at given position by 90, 180, or 270 degrees clockwise."""

    def __init__(self, pos: Tuple[int, int], angle: int):
        """
        :param pos: (row, col)
        :param angle: 90, 180, or 270 degrees
        """
        super().__init__("Rotate")
        self._pos = pos
        self._angle = angle

    @property
    def pos(self) -> Tuple[int, int]:
        return self._pos

    @property
    def angle(self) -> int:
        return self._angle

    def apply(self, board: 'Board') -> None:
        r, c = self._pos
        times = (self._angle // 90) % 4
        board.rotate_tile(r, c, times=times, record_move=False)


class FlipTransformation(Transformation):
    """Flips a tile horizontally or vertically."""

    def __init__(self, pos: Tuple[int, int], horizontal: bool = True):
        super().__init__("Flip")
        self._pos = pos
        self._horizontal = horizontal

    @property
    def pos(self) -> Tuple[int, int]:
        return self._pos

    @property
    def is_horizontal(self) -> bool:
        return self._horizontal

    def apply(self, board: 'Board') -> None:
        r, c = self._pos
        if self._horizontal:
            board.flip_tile(r, c, record_move=False)
        else:
            # Vertical flip is equivalent to 180 rotate + horizontal flip
            board.rotate_tile(r, c, times=2, record_move=False)
            board.flip_tile(r, c, record_move=False)
