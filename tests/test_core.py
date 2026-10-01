"""
Unit tests for Tile, Transformations, Board, and ImageProcessor.
"""

import unittest
import numpy as np
from core.tile import Tile
from core.transformations import SwapTransformation, RotateTransformation, FlipTransformation
from core.board import Board
from utils.image_processor import ImageProcessor


class TestCoreMechanics(unittest.TestCase):

    def setUp(self):
        # Create a dummy 300x300 BGR image
        self.img = np.zeros((300, 300, 3), dtype=np.uint8)
        # Give distinctive patterns to verify transformations
        self.img[0:50, 0:50] = (255, 0, 0)
        self.processor = ImageProcessor(target_max_dim=300)

    def test_image_processor_grid_division(self):
        padded, tw, th = self.processor.prepare_for_grid(self.img, grid_size=3)
        self.assertEqual(padded.shape[0] % 3, 0)
        self.assertEqual(padded.shape[1] % 3, 0)
        tiles = self.processor.slice_into_tiles(padded, grid_size=3)
        self.assertEqual(len(tiles), 9)

    def test_tile_rotation_and_flip(self):
        slice_img = np.zeros((50, 50, 3), dtype=np.uint8)
        tile = Tile(0, slice_img, 0, 0)
        self.assertTrue(tile.is_solved())

        tile.rotate_cw(1)
        self.assertEqual(tile.rotation_angle, 90)
        self.assertFalse(tile.is_correct_orientation())
        self.assertFalse(tile.is_solved())

        tile.rotate_cw(3)
        self.assertEqual(tile.rotation_angle, 0)
        self.assertTrue(tile.is_correct_orientation())

        tile.flip_horizontal()
        self.assertTrue(tile.flipped_horizontal)
        self.assertFalse(tile.is_solved())

        tile.flip_horizontal()
        self.assertTrue(tile.is_solved())

    def test_board_scramble_and_solve(self):
        padded, tw, th = self.processor.prepare_for_grid(self.img, grid_size=3)
        tiles = self.processor.slice_into_tiles(padded, grid_size=3)
        board = Board(grid_size=3, tile_images=tiles, tile_w=tw, tile_h=th)

        self.assertTrue(board.is_solved())
        board.scramble()
        self.assertFalse(board.is_solved())

        # Test solve method
        board.solve()
        self.assertTrue(board.is_solved())
        self.assertEqual(board.moves_count, 0)
        self.assertEqual(board.count_incorrect_tiles(), 0)

    def test_polymorphic_transformations(self):
        padded, tw, th = self.processor.prepare_for_grid(self.img, grid_size=3)
        tiles = self.processor.slice_into_tiles(padded, grid_size=3)
        board = Board(grid_size=3, tile_images=tiles, tile_w=tw, tile_h=th)

        swap = SwapTransformation((0, 0), (1, 1))
        rot = RotateTransformation((0, 0), 90)
        flip = FlipTransformation((0, 0), horizontal=True)

        for t in [swap, rot, flip]:
            t.apply(board)

        self.assertFalse(board.is_solved())


if __name__ == '__main__':
    unittest.main()
