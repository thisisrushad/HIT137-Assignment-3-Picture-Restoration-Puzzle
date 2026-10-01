#!/usr/bin/env python3
"""
HIT137 - Software Now
Group Assignment 3: Interactive Picture Restoration Puzzle
Main entry point.
"""

from ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
