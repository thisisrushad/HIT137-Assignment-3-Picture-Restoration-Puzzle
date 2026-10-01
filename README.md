# HIT137 Group Assignment 3 - Picture Restoration Puzzle

A desktop puzzle restoration game developed in Python using **Tkinter**, **OpenCV**, and strict **Object-Oriented Programming (OOP)** principles.

## Features
- **OpenCV Image Processing:** Loads JPG, PNG, and BMP images, automatically scales to fit screen dimensions, and crops/pads so they divide evenly into selected grid dimensions.
- **Configurable Grid Sizes:** Supports $3\times3$, $4\times4$, and $5\times5$ grids selectable before loading.
- **Procedural Scrambler:** Scaled transformation count (6 for $3\times3$, 12 for $4\times4$, 20 for $5\times5$) incorporating:
  - **Tile Swapping** (exchange positions)
  - **Tile Rotation** ($90^\circ, 180^\circ, 270^\circ$)
  - **Tile Flipping** (horizontal and vertical)
- **Interactive Dual-Canvas Interface:**
  - **Left canvas:** Reference original image.
  - **Right canvas:** Interactive scrambled puzzle with faint tile grid overlay.
- **Intuitive Player Controls:**
  - **Left-Click:** Select a tile (highlighted border). Left-clicking a second tile swaps them. Left-clicking the selected tile deselects it.
  - **Right-Click:** Rotate tile $90^\circ$ clockwise.
  - **Shift + Left-Click:** Flip tile horizontally.
- **Real-Time Visual Indicators & Scoring:**
  - **Green checkmarks** in tile corners indicate correct position AND orientation.
  - Live **move counter** and **incorrect tiles remaining** display.
- **Hints & Solver:**
  - **Hint System:** Highlights one incorrect tile on the puzzle canvas and its target destination on the reference canvas with blue circles. Disappears on next move. Limited to **3 hints per game**.
  - **Instant Solver:** Restores the puzzle to its solved state and clears moves and score.
- **Win Detection:** Automatically disables input when fully solved and presents a congratulatory victory dialog.

---

## Architecture & OOP Design
- `core/tile.py`: `Tile` class encapsulating original/current coordinates, rotation angles, flip state, and individual tile rendering.
- `core/transformations.py`: Demonstrates **Inheritance & Polymorphism** via abstract base class `Transformation` and concrete subclasses:
  - `SwapTransformation`
  - `RotateTransformation`
  - `FlipTransformation`
- `core/board.py`: `Board` class orchestrating grid state, scrambling algorithm, move counter, hint logic, and win evaluation.
- `utils/image_processor.py`: `ImageProcessor` handling OpenCV image loading, scaling, padding/cropping, and grid slicing.
- `ui/main_window.py`: Tkinter GUI coordinator managing layout, toolbar, status bar, and dispatching user actions.
- `ui/canvas_view.py`: Custom widget managing dual canvases, faint grid overlays, badges, and hint rings.
- `ui/dialogs.py`: Victory modal dialog and error handlers.

---

## Setup & Running

### Requirements
- Python 3.8+
- System packages: `python3-tk`
- Python dependencies: `opencv-python`, `pillow`, `numpy`

### Installation
```bash
# 1. Install system Tkinter (if not already installed)
sudo apt update && sudo apt install -y python3-tk

# 2. Create virtual environment and install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Application
```bash
python3 app.py
```

### Running Unit Tests
```bash
python3 -m unittest discover tests/
```
