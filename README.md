# Minesweeper (console, Python)

Implementation of the exercise statement [`demineur.md`](demineur.md) (written in French): a console minesweeper,
without object-oriented programming. This README only covers what was added
compared to the statement — the game rules, the list of required functions
and the constraints are described in `demineur.md`.

## Running the game

```bash
python demineur.py
```

A small menu lets you choose the difficulty (Easy / Medium / Hard), then the
game starts in the console. The in-game interface is in French.

## Controls: cursor navigation (instead of text commands)

The statement suggests commands typed on the keyboard (`o row column`,
`f row column`). This implementation replaces them with a cursor that can be
moved around the grid, which is faster to play:

| Key                          | Effect                                                    |
|------------------------------|-----------------------------------------------------------|
| Arrows or `Z`/`Q`/`S`/`D`     | Move the cursor (up/left/down/right — AZERTY layout)      |
| `Enter`                     | Open the cell under the cursor                            |
| `Space`                     | Place or remove a flag on the cell under the cursor       |
| `Esc`                       | Quit the game                                             |

The cursor cell is displayed between brackets `[ ]`. This mode requires
Windows: it uses the standard `msvcrt` module to read keys without waiting
for the Enter key after each move.

## Functions added beyond the statement

- `lire_touche()` — reads a key press (arrows, Z/Q/S/D, Enter, Space, Esc)
  and returns a normalized action.
- `deplacer_curseur(r, c, direction, rows, cols)` — computes the new cursor
  position while staying inside the grid.
- `afficher_defaite()` / `afficher_victoire()` — colored ASCII art end-of-game
  screens (see below).
- `choisir_difficulte()` — small level selection menu.

## Implemented bonuses (among those listed in demineur.md)

- Impossible to place a flag on an already revealed cell.
- Improved display (row/column numbers, `.` for cells with 0, framed cursor).
- Move counter.
- Play time displayed at the end of the game.
- Several difficulty levels (Easy 9x9, Medium 16x16, Hard 16x30).

### Advanced bonuses not implemented

- Preventing mines from being generated *around* the first cell (and not only
  on it): this would require changing `generate_mines` to accept a forbidden
  zone instead of a single cell.
- Graphical interface (optional in the statement).

## End-of-game screens

In addition to the text message, the game ends with a colored ASCII art screen
(ANSI codes, no external dependency):

- **Defeat**: "BOOM" framed by two bombs, in red.
- **Victory**: a mine-clearing expert in gear, thumbs up, in green.

## Project structure

```
demineur-python/
├── demineur.py           # The game
├── demineur.md           # Exercise statement
├── tests/
│   └── test_demineur.py  # Unit tests (pytest)
├── requirements.txt
├── .gitignore
└── README.md
```

## Tests

The pure functions of the game (everything except `minesweeper`, which reads
the keyboard) are tested with `pytest`:

```bash
pip install -r requirements.txt
pytest -v
```

If `pytest` is not recognized after installation (Python's `Scripts` folder
missing from the PATH), use `python -m pytest -v` instead.
