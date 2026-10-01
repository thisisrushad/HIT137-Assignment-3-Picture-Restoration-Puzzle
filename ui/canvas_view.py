"""
Canvas View module for rendering the side-by-side puzzle canvases:
- Left Canvas: Original reference image (read-only)
- Right Canvas: Interactive scrambled puzzle image with faint grid lines,
  selection highlights, green completion ticks, and blue hint circles.
"""

import tkinter as tk
from typing import Optional, Tuple
import cv2
import numpy as np
from PIL import Image, ImageTk

from core.board import Board


class PuzzleCanvasView(tk.Frame):
    """
    Manages the visual presentation of both reference and interactive puzzle canvases.
    """

    def __init__(self, master, on_tile_left_click, on_tile_right_click, on_tile_shift_left_click):
        super().__init__(master, bg="#1e1e2e")
        self._on_tile_left_click = on_tile_left_click
        self._on_tile_right_click = on_tile_right_click
        self._on_tile_shift_left_click = on_tile_shift_left_click

        self._ref_photo: Optional[ImageTk.PhotoImage] = None
        self._puzzle_photo: Optional[ImageTk.PhotoImage] = None

        self._build_ui()

    def _build_ui(self):
        # Container for the two side-by-side panels
        self.canvas_container = tk.Frame(self, bg="#1e1e2e")
        self.canvas_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # 1. Left Frame: Reference Image
        self.left_frame = tk.LabelFrame(
            self.canvas_container,
            text=" Original Reference ",
            font=("Inter", 11, "bold"),
            fg="#89b4fa",
            bg="#181825",
            bd=2,
            relief=tk.GROOVE
        )
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.ref_canvas = tk.Canvas(self.left_frame, bg="#11111b", highlightthickness=0)
        self.ref_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 2. Right Frame: Interactive Puzzle Image
        self.right_frame = tk.LabelFrame(
            self.canvas_container,
            text=" Interactive Puzzle (Play Here) ",
            font=("Inter", 11, "bold"),
            fg="#a6e3a1",
            bg="#181825",
            bd=2,
            relief=tk.GROOVE
        )
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.puzzle_canvas = tk.Canvas(self.right_frame, bg="#11111b", highlightthickness=0, cursor="hand2")
        self.puzzle_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bindings for mouse interaction on the right canvas
        self.puzzle_canvas.bind("<Button-1>", self._handle_left_click)
        self.puzzle_canvas.bind("<Button-3>", self._handle_right_click)
        # Shift + Left Click
        self.puzzle_canvas.bind("<Shift-Button-1>", self._handle_shift_left_click)

    def _get_tile_indices_from_event(self, event, board: Board) -> Optional[Tuple[int, int]]:
        """Maps canvas (x, y) coordinates to (row, col) grid coordinates."""
        if not board or board.tile_w <= 0 or board.tile_h <= 0:
            return None

        # Center offset calculation if canvas is larger than image
        canvas_w = self.puzzle_canvas.winfo_width()
        canvas_h = self.puzzle_canvas.winfo_height()
        img_w = board.grid_size * board.tile_w
        img_h = board.grid_size * board.tile_h

        offset_x = max(0, (canvas_w - img_w) // 2)
        offset_y = max(0, (canvas_h - img_h) // 2)

        rel_x = event.x - offset_x
        rel_y = event.y - offset_y

        if 0 <= rel_x < img_w and 0 <= rel_y < img_h:
            col = int(rel_x // board.tile_w)
            row = int(rel_y // board.tile_h)
            if 0 <= col < board.grid_size and 0 <= row < board.grid_size:
                return row, col
        return None

    def _handle_left_click(self, event):
        self._on_tile_left_click(event)

    def _handle_right_click(self, event):
        self._on_tile_right_click(event)

    def _handle_shift_left_click(self, event):
        self._on_tile_shift_left_click(event)

    def render_reference(self, original_bgr: np.ndarray):
        """Displays original un-scrambled image on left canvas."""
        self.ref_canvas.delete("all")
        if original_bgr is None:
            return

        rgb = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        self._ref_photo = ImageTk.PhotoImage(pil_img)

        # Center in canvas
        cw = self.ref_canvas.winfo_width()
        ch = self.ref_canvas.winfo_height()
        cx = max(cw // 2, pil_img.width // 2)
        cy = max(ch // 2, pil_img.height // 2)

        self.ref_canvas.create_image(cx, cy, image=self._ref_photo, anchor=tk.CENTER)

    def render_puzzle(self, board: Board, reference_bgr: Optional[np.ndarray] = None):
        """
        Renders the active board state onto the puzzle canvas, including:
        - Assembled tile image
        - Faint grid overlay
        - Colored selection border
        - Small green checkmark ticks on solved tiles
        - Blue hint circles (on puzzle tile & target position on reference)
        """
        self.puzzle_canvas.delete("all")
        if not board:
            return

        # 1. Compose full transformed image
        full_bgr = board.compose_full_image()
        rgb = cv2.cvtColor(full_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        self._puzzle_photo = ImageTk.PhotoImage(pil_img)

        cw = self.puzzle_canvas.winfo_width()
        ch = self.puzzle_canvas.winfo_height()
        img_w = pil_img.width
        img_h = pil_img.height

        offset_x = max(0, (cw - img_w) // 2)
        offset_y = max(0, (ch - img_h) // 2)

        self.puzzle_canvas.create_image(offset_x, offset_y, image=self._puzzle_photo, anchor=tk.NW)

        # 2. Draw faint grid lines
        tw, th = board.tile_w, board.tile_h
        grid_n = board.grid_size

        for i in range(grid_n + 1):
            # Vertical lines
            vx = offset_x + i * tw
            self.puzzle_canvas.create_line(vx, offset_y, vx, offset_y + img_h, fill="#45475a", width=1, dash=(2, 2))
            # Horizontal lines
            hy = offset_y + i * th
            self.puzzle_canvas.create_line(offset_x, hy, offset_x + img_w, hy, fill="#45475a", width=1, dash=(2, 2))

        # 3. Draw green tick on solved tiles
        for r in range(grid_n):
            for c in range(grid_n):
                tile = board.get_tile(r, c)
                if tile.is_solved():
                    self._draw_green_tick(offset_x + c * tw, offset_y + r * th, tw, th)

        # 4. Draw highlight around selected tile
        if board.selected_tile_pos is not None:
            sr, sc = board.selected_tile_pos
            x1 = offset_x + sc * tw
            y1 = offset_y + sr * th
            x2 = x1 + tw
            y2 = y1 + th
            self.puzzle_canvas.create_rectangle(x1 + 2, y1 + 2, x2 - 2, y2 - 2, outline="#f9e2af", width=3)

        # 5. Draw active hint circles (if any)
        if board.active_hint is not None:
            cr, cc = board.active_hint['current_pos']
            # Blue circle on transformed image
            px = offset_x + cc * tw + tw // 2
            py = offset_y + cr * th + th // 2
            radius = min(tw, th) // 4
            self.puzzle_canvas.create_oval(
                px - radius, py - radius, px + radius, py + radius,
                outline="#89b4fa", width=4
            )

            # Draw blue circle on reference canvas
            self._draw_hint_on_reference(board, board.active_hint['target_pos'])

    def _draw_green_tick(self, x: int, y: int, tw: int, th: int):
        """Renders a small green checkmark in the bottom-right corner of the solved tile."""
        pad = 6
        size = 14
        bx = x + tw - pad - size
        by = y + th - pad - size

        # Semi-transparent/dark circular badge backdrop
        self.puzzle_canvas.create_oval(bx - 3, by - 3, bx + size + 3, by + size + 3, fill="#11111b", outline="#a6e3a1", width=1)

        # Checkmark polyline
        points = [
            bx + 2, by + 7,
            bx + 6, by + 12,
            bx + 13, by + 3
        ]
        self.puzzle_canvas.create_line(points, fill="#a6e3a1", width=2.5, capstyle=tk.ROUND, joinstyle=tk.ROUND)

    def _draw_hint_on_reference(self, board: Board, target_pos: Tuple[int, int]):
        """Renders blue circle on original reference canvas at target home position."""
        if not board:
            return

        cw = self.ref_canvas.winfo_width()
        ch = self.ref_canvas.winfo_height()
        img_w = board.grid_size * board.tile_w
        img_h = board.grid_size * board.tile_h

        offset_x = max(0, (cw - img_w) // 2)
        offset_y = max(0, (ch - img_h) // 2)

        tr, tc = target_pos
        tw, th = board.tile_w, board.tile_h
        tx = offset_x + tc * tw + tw // 2
        ty = offset_y + tr * th + th // 2
        radius = min(tw, th) // 4

        # Remove previous hint tags on reference canvas
        self.ref_canvas.delete("hint_marker")
        self.ref_canvas.create_oval(
            tx - radius, ty - radius, tx + radius, ty + radius,
            outline="#89b4fa", width=4, tags="hint_marker"
        )
