"""
Board module managing grid layout, tiles matrix, move counters,
scrambling algorithms, hint logic, and solve detection.
"""

import random
from typing import List, Tuple, Optional
import cv2
import numpy as np

from core.tile import Tile
from core.transformations import (
    Transformation,
    SwapTransformation,
    RotateTransformation,
    FlipTransformation,
)


class Board:
    """
    Encapsulates the puzzle board state, moves counter, scrambling, and hint resolution.
    Demonstrates OOP principles and class interaction with Tile and Transformation.
    """

    TRANSFORMATION_COUNTS = {
        3: 6,
        4: 12,
        5: 20
    }

    def __init__(self, grid_size: int, tile_images: List[np.ndarray], tile_w: int, tile_h: int):
        """
        :param grid_size: 3, 4, or 5
        :param tile_images: Ordered list of N*N numpy tile images
        :param tile_w: Width of each tile
        :param tile_h: Height of each tile
        """
        self._grid_size = grid_size
        self._tile_w = tile_w
        self._tile_h = tile_h
        self._moves_count = 0
        self._selected_tile_pos: Optional[Tuple[int, int]] = None
        self._active_hint: Optional[dict] = None  # {'current_pos': (r, c), 'target_pos': (r, c)}
        self._hints_used = 0
        self._max_hints = 3

        # Initialize grid with tiles in solved positions
        self._tiles: List[List[Tile]] = []
        idx = 0
        for r in range(grid_size):
            row_tiles = []
            for c in range(grid_size):
                tile = Tile(tile_id=idx, original_image=tile_images[idx], original_row=r, original_col=c)
                row_tiles.append(tile)
                idx += 1
            self._tiles.append(row_tiles)

    @property
    def grid_size(self) -> int:
        return self._grid_size

    @property
    def tile_w(self) -> int:
        return self._tile_w

    @property
    def tile_h(self) -> int:
        return self._tile_h

    @property
    def moves_count(self) -> int:
        return self._moves_count

    @property
    def selected_tile_pos(self) -> Optional[Tuple[int, int]]:
        return self._selected_tile_pos

    @selected_tile_pos.setter
    def selected_tile_pos(self, pos: Optional[Tuple[int, int]]):
        self._selected_tile_pos = pos

    @property
    def active_hint(self) -> Optional[dict]:
        return self._active_hint

    @property
    def hints_used(self) -> int:
        return self._hints_used

    @property
    def max_hints(self) -> int:
        return self._max_hints

    def get_tile(self, row: int, col: int) -> Tile:
        return self._tiles[row][col]

    def clear_active_hint(self):
        """Clears active hint circle after a move is made."""
        self._active_hint = None

    def swap_tiles(self, r1: int, c1: int, r2: int, c2: int, record_move: bool = True):
        """Swap tiles at (r1, c1) and (r2, c2)."""
        tile1 = self._tiles[r1][c1]
        tile2 = self._tiles[r2][c2]

        self._tiles[r1][c1] = tile2
        self._tiles[r2][c2] = tile1

        tile2.current_row, tile2.current_col = r1, c1
        tile1.current_row, tile1.current_col = r2, c2

        if record_move:
            self._moves_count += 1
            self.clear_active_hint()

    def rotate_tile(self, r: int, c: int, times: int = 1, record_move: bool = True):
        """Rotate tile at (r, c) 90 deg clockwise 'times' times."""
        tile = self._tiles[r][c]
        tile.rotate_cw(times)
        if record_move:
            self._moves_count += 1
            self.clear_active_hint()

    def flip_tile(self, r: int, c: int, record_move: bool = True):
        """Flip tile at (r, c) horizontally."""
        tile = self._tiles[r][c]
        tile.flip_horizontal()
        if record_move:
            self._moves_count += 1
            self.clear_active_hint()

    def count_incorrect_tiles(self) -> int:
        """Returns number of tiles that are either in wrong place or wrong orientation."""
        incorrect = 0
        for r in range(self._grid_size):
            for c in range(self._grid_size):
                if not self._tiles[r][c].is_solved():
                    incorrect += 1
        return incorrect

    def is_solved(self) -> bool:
        """Puzzle is solved when all tiles are in correct position and orientation."""
        return self.count_incorrect_tiles() == 0

    def scramble(self):
        """
        Generate and apply scaled transformations randomly all at once:
        6 for 3x3, 12 for 4x4, 20 for 5x5.
        Uses polymorphic Transformation instances.
        """
        num_transforms = self.TRANSFORMATION_COUNTS.get(self._grid_size, self._grid_size * 4)
        transformations: List[Transformation] = []

        all_coords = [(r, c) for r in range(self._grid_size) for c in range(self._grid_size)]

        for _ in range(num_transforms):
            choice = random.choice(["swap", "rotate", "flip"])
            if choice == "swap":
                p1, p2 = random.sample(all_coords, 2)
                transformations.append(SwapTransformation(p1, p2))
            elif choice == "rotate":
                pos = random.choice(all_coords)
                angle = random.choice([90, 180, 270])
                transformations.append(RotateTransformation(pos, angle))
            elif choice == "flip":
                pos = random.choice(all_coords)
                horizontal = random.choice([True, False])
                transformations.append(FlipTransformation(pos, horizontal=horizontal))

        # Apply transformations polymorphically
        for t in transformations:
            t.apply(self)

        # In the unlikely event scrambling ended up solved, force a rotation
        if self.is_solved():
            self.rotate_tile(0, 0, times=1, record_move=False)

        # Reset move counters and selection
        self._moves_count = 0
        self._selected_tile_pos = None
        self._active_hint = None
        self._hints_used = 0

    def solve(self):
        """
        Instantly restores all tiles to original coordinates/rotations,
        clearing moves and score.
        """
        # Find all tiles and put them back in a solved matrix
        solved_matrix: List[List[Optional[Tile]]] = [
            [None for _ in range(self._grid_size)] for _ in range(self._grid_size)
        ]

        for r in range(self._grid_size):
            for c in range(self._grid_size):
                tile = self._tiles[r][c]
                tile.reset_to_solved()
                solved_matrix[tile.original_row][tile.original_col] = tile

        self._tiles = solved_matrix
        self._moves_count = 0
        self._selected_tile_pos = None
        self._active_hint = None

    def request_hint(self) -> Optional[dict]:
        """
        Provide a hint marking one incorrect tile and its home destination.
        Returns dict with current_pos and target_pos, or None if no hints left or solved.
        """
        if self._hints_used >= self._max_hints or self.is_solved():
            return None

        # Find all tiles not in correct position or orientation
        incorrect_coords = [
            (r, c) for r in range(self._grid_size) for c in range(self._grid_size)
            if not self._tiles[r][c].is_solved()
        ]

        if not incorrect_coords:
            return None

        chosen_r, chosen_c = random.choice(incorrect_coords)
        tile = self._tiles[chosen_r][chosen_c]

        self._hints_used += 1
        self._active_hint = {
            'current_pos': (chosen_r, chosen_c),
            'target_pos': (tile.original_row, tile.original_col)
        }
        return self._active_hint

    def compose_full_image(self) -> np.ndarray:
        """
        Reassemble the transformed tiles into a single BGR OpenCV image for display.
        """
        full_h = self._grid_size * self._tile_h
        full_w = self._grid_size * self._tile_w
        canvas = np.zeros((full_h, full_w, 3), dtype=np.uint8)

        for r in range(self._grid_size):
            for c in range(self._grid_size):
                tile_img = self._tiles[r][c].render()
                # Ensure dimensions match in case of weird rotation rounding
                if tile_img.shape[0] != self._tile_h or tile_img.shape[1] != self._tile_w:
                    tile_img = cv2.resize(tile_img, (self._tile_w, self._tile_h))

                y1 = r * self._tile_h
                y2 = y1 + self._tile_h
                x1 = c * self._tile_w
                x2 = x1 + self._tile_w
                canvas[y1:y2, x1:x2] = tile_img

        return canvas
