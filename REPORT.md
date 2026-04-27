# Battleship Game Coursework Report

---

## 1. Introduction

### What is the application?

This project is a turn-based Battleship style game made with Python using OOP Programming rules. The player places a fleet of five ships on a 10×10 grid and then takes turns shooting at the AI opponent's fleet. The AI responds with random shots on the player's board. The game ends when all ships of either side are sunk, and the outcome is saved to a text file.

### How to run the program

**Requirements:** Python 3.8 or later.

input "python Battleship.py" in a command line to run the program

### How to use the program

**Ship placement phase:**

1. The program prompts you to place each of the 5 ships one by one.
2. Enter coordinates A1–J10 (letter = column, number = row).
3. Enter orientation: H for horizontal or V for vertical.
4. Ships cannot overlap or be near each other. If placement is invalid, you are prompted again.
5. After each successful placement, the player board is displayed.

**Shooting phase:**

1. On your turn, enter coordinates to fire at the AI's board.
2. The result is printed: "HIT", "HIT – SHIP SUNK", "MISS" or "ALREADY SHOT THERE".
3. A miss ends your turn and passes it to the AI.
4. On a hit you may shoot again.
5. The AI shoots randomly.
6. When all ships on either side are sunk, the winner is announced and the result is written to txt file.

---

## 2. Body / Analysis

### 2.1 The Four OOP Pillars

#### Encapsulation

Encapsulation is the principle of bundling data and the methods that operate on it inside a class, and restricting direct access to internal state from outside. In this project all instance attributes are prefixed with _ to mark them as private, and access is provided through Python @property descriptors.

```python
class Ship:
    def __init__(self, size):
        self._size = size
        self._cells = []
        self._hits = 0

    @property
    def size(self):
        return self._size

    @property
    def is_sunk(self):
        return self._hits >= self._size

    def hit(self):
        self._hits += 1
```

The _hits counter can only be incremented through the public hit() method; external code cannot set it to an arbitrary value. The same pattern applies to Board._board, board._ship_map, fleet._ships, and Game's four fields.

---

#### Inheritance

Inheritance allows a child class to reuse and extend the behaviour of a parent class. AIBoard inherits from Board and gains all of its grid management logic while adding AI-specific behaviour.

```python
class AIBoard(Board):
    def __init__(self, size):
        super().__init__(size)

    def display(self):
        # Hides ships (shows ~ instead of S)
        label_width = len(str(self._size))
        header = (
            ' ' * label_width
            + ' '
            + ' '.join(chr(ord('A') + i) for i in range(self._size))
        )
        print(header)
        for row_index, row in enumerate(self._board, start=1):
            hidden_row = ['~' if cell == 'S' else cell for cell in row]
            print(f"{row_index:>{label_width}} {' '.join(hidden_row)}")

    def place_ship_random(self, ship):
        while True:
            row = random.randint(0, self._size - 1)
            col = random.randint(0, self._size - 1)
            orien = random.choice(['H', 'V'])
            coords = chr(ord('A') + col) + str(row + 1)
            if self.place_ship(ship, coords, orien):
                return True
```

AIBoard calls super().__init__(size) to reuse the parent constructor, then adds place_ship_random() on top of the inherited place_ship() logic.

---

#### Polymorphism

Polymorphism means that different classes can share the same interface but provide different implementations. Here, both Board and AIBoard implement display(), but with different output: Board.display() shows ship positions (S), while AIBoard.display() hides them (replaces S with ~), so the player cannot see the AI's fleet.

```python
def display(self):
        # Hides ships (shows ~ instead of S)
        label_width = len(str(self._size))
        header = (
            ' ' * label_width
            + ' '
            + ' '.join(chr(ord('A') + i) for i in range(self._size))
        )
        print(header)
        for row_index, row in enumerate(self._board, start=1):
            hidden_row = ['~' if cell == 'S' else cell for cell in row]
            print(f"{row_index:>{label_width}} {' '.join(hidden_row)}")
```

---

#### Abstraction

Abstraction means exposing only the essential interface of an object and hiding internal complexity. External code can never change the raw _board grid directly, instead it interacts through methods such as place_ship(), shoot(), and display().

The caller receives one of four simple string results (hit, sunk, miss, alr_shot). All internal logic, cell updates, ship lookup, sinking detection, and adjacent-cell masking is hidden inside Board.shoot() and Board._mark_adjacent_sunk().

The leading underscore signals that _mark_adjacent_sunk is an internal helper; it is never called from outside the class.

---

### 2.2 Composition and Aggregation

**Composition** is a "has-a" relationship where the existence of the contained object is tied to the container. **Aggregation** is also a "has-a" relationship, but the contained object can exist independently.

Composition – Fleet and Ship:

Fleet creates its Ship objects internally; they have no meaning or identity outside the fleet they belong to.

```python
class Fleet:
    def __init__(self, sizes):
        self._ships = [Ship(s) for s in sizes]
```

The Ship instances are constructed inside Fleet.__init__ and are owned entirely by the fleet. This is composition.

Aggregation – Board and Ship:

Board holds references to Ship objects in _ship_map, but the ships are created outside Board and passed in via place_ship(). The board does not own the ships, it only associates grid cells with existing ship objects.

```python
def place_ship(self, ship, coords, orien):
    self._ship_map[(r, c)] = ship
```

Composition – Game and its systems:

```python
game = Game(player_board, ai_board, player_fleet, ai_fleet)
```

Game composes all four core objects into one logical unit representing the full game state.

---

### 2.3 Writing to File

At the end of every game session the result is persisted to file.txt using Python's file I/O:

```python
with open("file.txt", "w", encoding="utf-8") as f:
    if game.ai_fleet.all_sunk:
        f.write(
            f'Player won with {player_hits} hits '
            f'and {player_shots_fired} total shots'
        )
    elif game.player_fleet.all_sunk:
        f.write(
            f'AI won with {ai_hits} hits '
            f'and {ai_shots_fired} total shots'
        )
```

---

## 3. Results and Summary

### Results

- The game correctly implements all core Battleship game rules: ship placement with adjacency enforcement, turn-based shooting, hit/miss/sunk detection, and automatic masking of cells around a sunk ship.
- Implementing the adjacency constraint in place_ship() and _mark_adjacent_sunk() required careful iteration over all eight neighbouring cells, which was a complexity challenge.
- Separating the AI's board into a dedicated AIBoard subclass kept the display logic clean without modifying the base Board class.
- The Fleet.all_sunk property provided and reusable end-condition check, avoiding duplicated logic across the game loop.

### Conclusions

This coursework produced a fully playable command-line Battleship game that demonstrates all four OOP pillars, composition and aggregation, and basic file persistence.

**Possible Future Updates:**

- **Smarter AI:** Replace random targeting with algorithm that focuses fire around a hit cell.
- **Save and load:** Serialise the full board state to JSON or CSV so a game can be paused and resumed.
- **GUI:** Add a graphical interface, reusing all existing logic.