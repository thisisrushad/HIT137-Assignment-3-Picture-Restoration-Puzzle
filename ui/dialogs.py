"""
Dialogs and message helpers for win alerts and notifications.
"""

import tkinter as tk
from tkinter import messagebox


def show_win_dialog(master, moves_count: int):
    """Displays a clean victory modal dialog when the puzzle is restored."""
    dialog = tk.Toplevel(master)
    dialog.title("🎉 Congratulations!")
    dialog.geometry("380x220")
    dialog.resizable(False, False)
    dialog.configure(bg="#181825")
    dialog.transient(master)
    dialog.grab_set()

    # Center dialog on screen
    dialog.update_idletasks()
    x = master.winfo_x() + (master.winfo_width() // 2) - 190
    y = master.winfo_y() + (master.winfo_height() // 2) - 110
    dialog.geometry(f"+{x}+{y}")

    # Content
    lbl_title = tk.Label(
        dialog,
        text="🌟 Puzzle Solved!",
        font=("Inter", 16, "bold"),
        fg="#a6e3a1",
        bg="#181825"
    )
    lbl_title.pack(pady=(25, 10))

    lbl_msg = tk.Label(
        dialog,
        text=f"Splendid job! You fully restored the picture in\n{moves_count} moves.\n\nLoad another image to play again!",
        font=("Inter", 11),
        fg="#cdd6f4",
        bg="#181825",
        justify=tk.CENTER
    )
    lbl_msg.pack(pady=(0, 20))

    btn_ok = tk.Button(
        dialog,
        text="Awesome!",
        font=("Inter", 10, "bold"),
        bg="#89b4fa",
        fg="#11111b",
        activebackground="#b4befe",
        relief=tk.FLAT,
        padx=20,
        pady=5,
        cursor="hand2",
        command=dialog.destroy
    )
    btn_ok.pack()


def show_error(title: str, message: str):
    messagebox.showerror(title, message)
