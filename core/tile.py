"""
Tile module representing an individual puzzle piece.
Encapsulates original image, original coordinates, current coordinates,
and orientation transformations (rotation, horizontal flip).
"""

import cv2
import numpy as np


class Tile:
    """
    Encapsulates state and operations of a single puzzle tile.
    Demonstrates OOP encapsulation, getters, and state manipulation methods.
    """

    def __init__(self, tile_id: int, original_image: np.ndarray, original_row: int, original_col: int):
        """
        :param tile_id: Unique integer index for the tile (0 to N*N - 1).
        :param original_image: OpenCV BGR image slice representing the base tile.
        :param original_row: Row in the solved grid.
        :param original_col: Col in the solved grid.
        """
        self._tile_id = tile_id
        self._original_image = original_image
        self._original_row = original_row
        self._original_col = original_col

        # Dynamic state
        self._current_row = original_row
        self._current_col = original_col
        self._rotation_angle = 0  # 0, 90, 180, 270 (degrees clockwise)
        self._flipped_horizontal = False

    @property
    def tile_id(self) -> int:
        return self._tile_id

    @property
    def original_row(self) -> int:
        return self._original_row

    @property
    def original_col(self) -> int:
        return self._original_col

    @property
    def current_row(self) -> int:
        return self._current_row

    @current_row.setter
    def current_row(self, row: int):
        self._current_row = row

    @property
    def current_col(self) -> int:
        return self._current_col

    @current_col.setter
    def current_col(self, col: int):
        self._current_col = col

    @property
    def rotation_angle(self) -> int:
        return self._rotation_angle

    @property
    def flipped_horizontal(self) -> bool:
        return self._flipped_horizontal

    def rotate_cw(self, times: int = 1):
        """Rotate tile 90 degrees clockwise 'times' times."""
        self._rotation_angle = (self._rotation_angle + (times * 90)) % 360

    def flip_horizontal(self):
        """Toggle horizontal flip state."""
        self._flipped_horizontal = not self._flipped_horizontal

    def is_correct_position(self) -> bool:
        """Check if the tile is placed at its home grid coordinates."""
        return (self._current_row == self._original_row) and (self._current_col == self._original_col)

    def is_correct_orientation(self) -> bool:
        """Check if the tile has original orientation (0 deg, not flipped)."""
        return (self._rotation_angle == 0) and (not self._flipped_horizontal)

    def is_solved(self) -> bool:
        """Tile is solved if both position and orientation are restored."""
        return self.is_correct_position() and self.is_correct_orientation()

    def reset_to_solved(self):
        """Instantly restores position and orientation to solved state."""
        self._current_row = self._original_row
        self._current_col = self._original_col
        self._rotation_angle = 0
        self._flipped_horizontal = False

    def render(self) -> np.ndarray:
        """
        Produce transformed numpy image according to rotation and flip state.
        :return: Transformed BGR image.
        """
        img = self._original_image.copy()

        # Apply horizontal flip first if toggled
        if self._flipped_horizontal:
            img = cv2.flip(img, 1)  # 1 means flipping horizontally

        # Apply rotation (clockwise)
        if self._rotation_angle == 90:
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif self._rotation_angle == 180:
            img = cv2.rotate(img, cv2.ROTATE_180)
        elif self._rotation_angle == 270:
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return img
