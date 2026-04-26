import random


class Board:
    def __init__(self, size):
        self._size = size
        self._board = [['~'] * size for _ in range(size)]
        self._ship_map = {}  # (row, col) to Ship

    @property
    def size(self):
        return self._size

    @property
    def board(self):
        return self._board

    def display(self):
        # Print column labels with correct offset for row numbers
        label_width = len(str(self._size))
        header = (
            ' ' * label_width
            + ' '
            + ' '.join(chr(ord('A') + i) for i in range(self._size))
        )
        print(header)
        # Print each row with its number on the left, aligned to width
        for row_index, row in enumerate(self._board, start=1):
            print(f"{row_index:>{label_width}} {' '.join(row)}")

    def place_ship(self, ship, coords, orien):
        orien = orien.upper()
        letter = coords[0].upper()
        number = int(coords[1:])
        col = ord(letter) - ord('A')
        row = int(number) - 1
        if orien == 'H':
            if col + ship.size > self._size:
                return False
            ship_cells = [(row, col + i) for i in range(ship.size)]
        else:
            if row + ship.size > self._size:
                return False
            ship_cells = [(row + i, col) for i in range(ship.size)]
        # Check adjacent and ship cells
        for r, c in ship_cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr = r + dr
                    nc = c + dc
                    if 0 <= nr < self._size and 0 <= nc < self._size:
                        if self._board[nr][nc] != '~':
                            return False
        # Place ship and register its cells
        for r, c in ship_cells:
            self._board[r][c] = 'S'
            ship.register_cell(r, c)
            self._ship_map[(r, c)] = ship
        return True

    def _mark_adjacent_sunk(self, ship):
        # After a ship sinks, mark all empty neighbours as misses
        for r, c in ship.cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self._size and 0 <= nc < self._size:
                        if self._board[nr][nc] == '~':
                            self._board[nr][nc] = 'O'

    def shoot(self, coords):
        letter = coords[0].upper()
        number = int(coords[1:])
        col = ord(letter) - ord('A')
        row = int(number) - 1
        cell = self._board[row][col]
        if cell == '~':
            self._board[row][col] = 'O'
            return 'miss'
        elif cell == 'S':
            self._board[row][col] = 'X'
            ship = self._ship_map.get((row, col))
            if ship:
                ship.hit()
                if ship.is_sunk:
                    self._mark_adjacent_sunk(ship)
                    return 'sunk'
            return 'hit'
        else:
            return 'alr_shot'


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


class Ship:
    def __init__(self, size):
        self._size = size
        self._cells = []  # (row, col) pairs occupied by this ship
        self._hits = 0

    @property
    def size(self):
        return self._size

    @property
    def cells(self):
        return self._cells

    @property
    def is_sunk(self):
        return self._hits >= self._size

    def register_cell(self, r, c):
        self._cells.append((r, c))

    def hit(self):
        self._hits += 1


class Fleet:
    def __init__(self, sizes):
        self._ships = [Ship(s) for s in sizes]

    @property
    def ships(self):
        return self._ships

    @property
    def total_hp(self):
        return sum(s.size for s in self._ships)

    @property
    def all_sunk(self):
        return all(s.is_sunk for s in self._ships)


class Game:
    def __init__(self, player_board, ai_board, player_fleet, ai_fleet):
        self.player_board = player_board
        self.ai_board = ai_board
        self.player_fleet = player_fleet
        self.ai_fleet = ai_fleet


# ---- GAME SETUP ----

SHIP_SIZES = [5, 4, 3, 2, 2]

# Each fleet composes its own independent Ship objects
player_fleet = Fleet(SHIP_SIZES)
ai_fleet = Fleet(SHIP_SIZES)
player_board = Board(10)
ai_board = AIBoard(10)
game = Game(player_board, ai_board, player_fleet, ai_fleet)

# Player ship placement
for i in range(len(SHIP_SIZES)):
    while True:
        while True:
            coords = input("Input coordinates(A1-J10):")
            if (
                len(coords) >= 2
                and coords[0].isalpha()
                and coords[1:].isdigit()
            ):
                col = ord(coords[0].upper()) - ord('A')
                row = int(coords[1:])
                if 0 <= col < 10 and 1 <= row <= 10:
                    break
            else:
                print("Invalid coordinates")
        while True:
            orient = input("Input ship orientation(H or V):")
            if orient.upper() not in ('H', 'V'):
                print("Invalid orientation")
            else:
                break
        if player_board.place_ship(game.player_fleet.ships[i], coords, orient):
            player_board.display()
            break
        else:
            print(
                "Cannot place ship there - occupied, "
                "too close to another ship or out of bounds"
            )

player_board.display()
ai_board.display()

# AI ship placement (random)
for i in range(len(SHIP_SIZES)):
    while True:
        if ai_board.place_ship_random(game.ai_fleet.ships[i]):
            break

print("Shooting phase")
player_shots_fired = 0
player_hits = 0
ai_shots_fired = 0
ai_hits = 0

while not game.player_fleet.all_sunk and not game.ai_fleet.all_sunk:
    print("Player turn")
    player_turn = True
    while player_turn:
        player_board.display()
        print()
        ai_board.display()
        print(f'Player shots fired: {player_shots_fired}')
        print(f'Player hits: {player_hits}')
        while True:
            coords = input("Enter coordinates to shoot(A1-J10): ")
            if (
                len(coords) >= 2
                and coords[0].isalpha()
                and coords[1:].isdigit()
            ):
                col = ord(coords[0].upper()) - ord('A')
                row = int(coords[1:])
                if 0 <= col < 10 and 1 <= row <= 10:
                    result = ai_board.shoot(coords)
                    break
            else:
                print("invalid coords")

        if result == 'sunk':
            player_shots_fired += 1
            player_hits += 1
            print("HIT - SHIP SUNK")
        elif result == 'hit':
            player_shots_fired += 1
            player_hits += 1
            print("HIT")
        elif result == 'miss':
            player_shots_fired += 1
            player_turn = False
            print("MISS")
        elif result == "alr_shot":
            print("ALREADY SHOT THERE")

    if game.ai_fleet.all_sunk:
        print("you win")
        break

    print("AI turn")
    ai_turn = True
    while ai_turn:
        ai_coords = (
            chr(ord('A') + random.randint(0, 9)) + str(random.randint(1, 10))
        )
        result = player_board.shoot(ai_coords)
        print(f'AI shoots: {ai_coords}')
        player_board.display()

        if result == 'sunk':
            ai_shots_fired += 1
            ai_hits += 1
            print("HIT - SHIP SUNK")
        elif result == 'hit':
            ai_shots_fired += 1
            ai_hits += 1
            print("HIT")
        elif result == 'miss':
            ai_shots_fired += 1
            ai_turn = False
            print("MISS")
        elif result == "alr_shot":
            print("ALREADY SHOT THERE")

    if game.player_fleet.all_sunk:
        print("you lose")
        break

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