"""
Main Application Window using Tkinter.
Coordinates controls, event dispatching, board state, hints, and displays.
"""

import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional
import numpy as np

from core.board import Board
from utils.image_processor import ImageProcessor
from ui.canvas_view import PuzzleCanvasView
from ui.dialogs import show_win_dialog, show_error


class MainWindow(tk.Tk):
    """
    Main Tkinter application window for the puzzle game.
    Demonstrates OOP integration, responsive event binding, and GUI layout.
    """

    def __init__(self):
        super().__init__()
        self.title("HIT137 - Interactive Tile Puzzle Game")
        self.geometry("1100x750")
        self.minsize(950, 650)
        self.configure(bg="#1e1e2e")

        self._image_processor = ImageProcessor(target_max_dim=450)
        self._current_image_path: Optional[str] = None
        self._raw_image_bgr: Optional[np.ndarray] = None
        self._prepared_image_bgr: Optional[np.ndarray] = None
        self._board: Optional[Board] = None
        self._is_game_active: bool = False

        self._grid_size_var = tk.IntVar(value=3)

        self._build_header()
        self._build_controls()
        self._build_canvas_view()
        self._build_status_bar()

    def _build_header(self):
        header_frame = tk.Frame(self, bg="#181825", pady=12)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="HIT137 Picture Restoration Puzzle",
            font=("Inter", 16, "bold"),
            fg="#cdd6f4",
            bg="#181825"
        )
        title_lbl.pack()

        subtitle_lbl = tk.Label(
            header_frame,
            text="Restore scrambled pieces by swapping, rotating (right click), and flipping (Shift + left click).",
            font=("Inter", 9),
            fg="#a6adc8",
            bg="#181825"
        )
        subtitle_lbl.pack(pady=(2, 0))

    def _build_controls(self):
        toolbar = tk.Frame(self, bg="#1e1e2e", pady=10)
        toolbar.pack(fill=tk.X, padx=20)

        # 1. Grid Size Selector
        grid_frame = tk.LabelFrame(
            toolbar,
            text=" Grid Size ",
            font=("Inter", 9, "bold"),
            fg="#cdd6f4",
            bg="#1e1e2e",
            padx=10,
            pady=4
        )
        grid_frame.pack(side=tk.LEFT, padx=(0, 15))

        for size in [3, 4, 5]:
            rb = tk.Radiobutton(
                grid_frame,
                text=f"{size} × {size}",
                value=size,
                variable=self._grid_size_var,
                font=("Inter", 9),
                fg="#cdd6f4",
                bg="#1e1e2e",
                selectcolor="#313244",
                activebackground="#1e1e2e",
                activeforeground="#cdd6f4"
            )
            rb.pack(side=tk.LEFT, padx=5)

        # 2. Action Buttons Frame
        btn_frame = tk.Frame(toolbar, bg="#1e1e2e")
        btn_frame.pack(side=tk.LEFT, padx=5)

        self.btn_load = tk.Button(
            btn_frame,
            text="📁 Choose Image",
            font=("Inter", 9, "bold"),
            bg="#89b4fa",
            fg="#11111b",
            activebackground="#b4befe",
            padx=12,
            pady=4,
            relief=tk.FLAT,
            cursor="hand2",
            command=self._on_choose_image
        )
        self.btn_load.pack(side=tk.LEFT, padx=6)

        self.btn_hint = tk.Button(
            btn_frame,
            text="💡 Hint (3 left)",
            font=("Inter", 9, "bold"),
            bg="#fab387",
            fg="#11111b",
            activebackground="#f9e2af",
            padx=12,
            pady=4,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._on_hint_clicked
        )
        self.btn_hint.pack(side=tk.LEFT, padx=6)

        self.btn_solve = tk.Button(
            btn_frame,
            text="⚡ Solve",
            font=("Inter", 9, "bold"),
            bg="#f38ba8",
            fg="#11111b",
            activebackground="#eba0ac",
            padx=12,
            pady=4,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED,
            command=self._on_solve_clicked
        )
        self.btn_solve.pack(side=tk.LEFT, padx=6)

        # 3. Instruction guide summary pill
        pill = tk.Label(
            toolbar,
            text="Controls: Left-Click: Select/Swap | Right-Click: Rotate 90° CW | Shift + Left-Click: Flip H",
            font=("Inter", 9),
            fg="#94e2d5",
            bg="#313244",
            padx=10,
            pady=5
        )
        pill.pack(side=tk.RIGHT, padx=5)

    def _build_canvas_view(self):
        self.canvas_view = PuzzleCanvasView(
            self,
            on_tile_left_click=self._handle_tile_left_click,
            on_tile_right_click=self._handle_tile_right_click,
            on_tile_shift_left_click=self._handle_tile_shift_left_click
        )
        self.canvas_view.pack(fill=tk.BOTH, expand=True)

    def _build_status_bar(self):
        status_frame = tk.Frame(self, bg="#11111b", pady=8, padx=20)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_moves = tk.Label(
            status_frame,
            text="Moves: 0",
            font=("Inter", 10, "bold"),
            fg="#cdd6f4",
            bg="#11111b"
        )
        self.lbl_moves.pack(side=tk.LEFT, padx=(0, 20))

        self.lbl_incorrect = tk.Label(
            status_frame,
            text="Tiles Incorrect: 0",
            font=("Inter", 10, "bold"),
            fg="#f38ba8",
            bg="#11111b"
        )
        self.lbl_incorrect.pack(side=tk.LEFT, padx=10)

        self.lbl_status_msg = tk.Label(
            status_frame,
            text="Ready. Select grid size and click 'Choose Image' to begin.",
            font=("Inter", 9),
            fg="#a6adc8",
            bg="#11111b"
        )
        self.lbl_status_msg.pack(side=tk.RIGHT)

    def _on_choose_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Puzzle Image",
            filetypes=[
                ("Supported Images", "*.jpg *.jpeg *.png *.bmp"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("Bitmap files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        if not file_path:
            return

        try:
            self._load_and_start_puzzle(file_path)
        except Exception as e:
            show_error("Error Loading Image", str(e))

    def _load_and_start_puzzle(self, file_path: str):
        grid_n = self._grid_size_var.get()

        # OpenCV loading and preprocessing
        raw_bgr = self._image_processor.load_image(file_path)
        prep_bgr, tile_w, tile_h = self._image_processor.prepare_for_grid(raw_bgr, grid_n)
        tile_slices = self._image_processor.slice_into_tiles(prep_bgr, grid_n)

        # Store references
        self._current_image_path = file_path
        self._raw_image_bgr = raw_bgr
        self._prepared_image_bgr = prep_bgr

        # Initialize Board and scramble
        self._board = Board(grid_size=grid_n, tile_images=tile_slices, tile_w=tile_w, tile_h=tile_h)
        self._board.scramble()
        self._is_game_active = True

        # Update button states
        self.btn_hint.config(state=tk.NORMAL, text=f"💡 Hint ({self._board.max_hints} left)")
        self.btn_solve.config(state=tk.NORMAL)

        # Refresh Canvas views
        self.update_idletasks()
        self.canvas_view.render_reference(self._prepared_image_bgr)
        self._refresh_game_display()

        self.lbl_status_msg.config(text=f"Loaded image at {grid_n}x{grid_n} grid. Good luck!")

    def _refresh_game_display(self):
        if not self._board:
            return

        self.canvas_view.render_puzzle(self._board, self._prepared_image_bgr)

        # Update status labels
        self.lbl_moves.config(text=f"Moves: {self._board.moves_count}")
        incorrect = self._board.count_incorrect_tiles()
        self.lbl_incorrect.config(
            text=f"Tiles Incorrect: {incorrect}",
            fg="#a6e3a1" if incorrect == 0 else "#f38ba8"
        )

        hints_left = self._board.max_hints - self._board.hints_used
        self.btn_hint.config(
            text=f"💡 Hint ({hints_left} left)",
            state=tk.NORMAL if (hints_left > 0 and self._is_game_active) else tk.DISABLED
        )

        # Check win condition
        if self._is_game_active and self._board.is_solved():
            self._handle_win_condition()

    def _handle_win_condition(self):
        self._is_game_active = False
        self.btn_hint.config(state=tk.DISABLED)
        self.btn_solve.config(state=tk.DISABLED)
        self.lbl_status_msg.config(text="🏆 Complete! You restored the picture.")
        show_win_dialog(self, self._board.moves_count)

    def _handle_tile_left_click(self, event):
        if not self._is_game_active or not self._board:
            return

        coords = self.canvas_view._get_tile_indices_from_event(event, self._board)
        if not coords:
            return

        row, col = coords
        selected = self._board.selected_tile_pos

        if selected is None:
            # First tile selected
            self._board.selected_tile_pos = (row, col)
        elif selected == (row, col):
            # Clicked same tile again -> deselect
            self._board.selected_tile_pos = None
        else:
            # Second tile clicked -> swap
            sr, sc = selected
            self._board.swap_tiles(sr, sc, row, col, record_move=True)
            self._board.selected_tile_pos = None

        self._refresh_game_display()

    def _handle_tile_right_click(self, event):
        if not self._is_game_active or not self._board:
            return

        coords = self.canvas_view._get_tile_indices_from_event(event, self._board)
        if not coords:
            return

        row, col = coords
        self._board.rotate_tile(row, col, times=1, record_move=True)
        self._refresh_game_display()

    def _handle_tile_shift_left_click(self, event):
        if not self._is_game_active or not self._board:
            return

        coords = self.canvas_view._get_tile_indices_from_event(event, self._board)
        if not coords:
            return

        row, col = coords
        self._board.flip_tile(row, col, record_move=True)
        self._refresh_game_display()

    def _on_hint_clicked(self):
        if not self._is_game_active or not self._board:
            return

        hint_data = self._board.request_hint()
        if hint_data:
            self._refresh_game_display()
            self.lbl_status_msg.config(text="Blue circle on puzzle matches blue circle on original reference!")

    def _on_solve_clicked(self):
        if not self._board:
            return

        self._board.solve()
        self._is_game_active = False
        self.btn_hint.config(state=tk.DISABLED)
        self.btn_solve.config(state=tk.DISABLED)
        self._refresh_game_display()
        self.lbl_status_msg.config(text="Puzzle solved instantly. Moves & score cleared.")
