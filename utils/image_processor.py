"""
Image Processor module using OpenCV.
Handles loading images, resizing, padding/cropping to divide evenly into grids,
and splitting into tiles.
"""

import os
from typing import Tuple, List
import cv2
import numpy as np


class ImageProcessor:
    """Handles image manipulation using OpenCV for the puzzle game."""

    SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')

    def __init__(self, target_max_dim: int = 480):
        """
        Initialize the ImageProcessor.
        :param target_max_dim: Maximum width or height of the image to display on screen.
        """
        self._target_max_dim = target_max_dim

    @property
    def target_max_dim(self) -> int:
        return self._target_max_dim

    def load_image(self, file_path: str) -> np.ndarray:
        """
        Load an image from disk using OpenCV.
        :param file_path: Absolute or relative path to the image file.
        :return: Loaded image as a BGR numpy array.
        :raises FileNotFoundError: If the image path does not exist.
        :raises ValueError: If the format is unsupported or cv2 fails to decode.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Image not found at path: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported image format '{ext}'. Supported formats: {self.SUPPORTED_EXTENSIONS}"
            )

        # cv2.imread loads image in BGR format
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError(f"OpenCV failed to read the image at: {file_path}")

        return image

    def prepare_for_grid(self, image: np.ndarray, grid_size: int) -> Tuple[np.ndarray, int, int]:
        """
        Resize image to fit screen dimensions, then crop/pad so it divides evenly by grid_size.
        Returns the processed image, tile_width, and tile_height.
        :param image: Input image (numpy array).
        :param grid_size: Number of tiles per row/col (e.g., 3, 4, 5).
        :return: (processed_image, tile_width, tile_height)
        """
        h, w = image.shape[:2]

        # 1. Resize proportionally to fit within target_max_dim
        scale = min(self._target_max_dim / w, self._target_max_dim / h)
        new_w = max(int(round(w * scale)), grid_size)
        new_h = max(int(round(h * scale)), grid_size)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # 2. Adjust dimensions so they divide evenly into grid_size
        rem_w = new_w % grid_size
        rem_h = new_h % grid_size

        pad_w = (grid_size - rem_w) if rem_w != 0 else 0
        pad_h = (grid_size - rem_h) if rem_h != 0 else 0

        # We pad border with reflection or constant black for clean edges
        if pad_w > 0 or pad_h > 0:
            padded = cv2.copyMakeBorder(
                resized,
                0, pad_h,  # top, bottom
                0, pad_w,  # left, right
                cv2.BORDER_REFLECT
            )
        else:
            padded = resized

        final_h, final_w = padded.shape[:2]
        tile_w = final_w // grid_size
        tile_h = final_h // grid_size

        return padded, tile_w, tile_h

    def slice_into_tiles(self, image: np.ndarray, grid_size: int) -> List[np.ndarray]:
        """
        Slices the prepared image into a list of row-major tile images.
        :param image: Evenly divisible image.
        :param grid_size: Grid dimension N.
        :return: List of N*N numpy array slices.
        """
        h, w = image.shape[:2]
        tile_w = w // grid_size
        tile_h = h // grid_size

        tiles = []
        for r in range(grid_size):
            for c in range(grid_size):
                y1 = r * tile_h
                y2 = (r + 1) * tile_h
                x1 = c * tile_w
                x2 = (c + 1) * tile_w
                tile = image[y1:y2, x1:x2].copy()
                tiles.append(tile)

        return tiles
