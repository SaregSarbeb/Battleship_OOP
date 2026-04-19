import random

class Board:
    def __init__(self, size):
        self.size = size
        self.board = [['~'] * size for _ in range(size)]

    def display(self):
        # print column labels with correct offset for row numbers
        label_width = len(str(self.size))
        header = ' ' * label_width + ' ' + ' '.join(chr(ord('A') + i) for i in range(self.size))
        print(header)

        # print each row with its number on the left, aligned to width
        for row_index, row in enumerate(self.board, start=1):
            print(f"{row_index:>{label_width}} {' '.join(row)}")

    def place_ship(self, ship, coords, orien):
        orien = orien.upper()
        letter = coords[0].upper()
        number = int(coords[1:])
        col = ord(letter) - ord('A')
        row = int(number) - 1
        if orien == 'H':
            if col + ship.size > self.size:
                return False
            ship_cells = [(row, col + i) for i in range(ship.size)]
        else:
            if row + ship.size > self.size:
                return False
            ship_cells = [(row + i, col) for i in range(ship.size)]
        #check adjacent and ship cells
        for r, c in ship_cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr = r + dr
                    nc =  c + dc
                    if 0 <= nr < self.size and 0 <= nc < self.size:
                        if self.board[nr][nc] != '~':
                            return False
        #place ship
        for r, c in ship_cells:
            self.board[r][c] = 'S'

        return True

    def shoot(self, coords):
        letter = coords[0].upper()
        number = int(coords[1:])
        col = ord(letter) - ord('A')
        row = int(number) - 1
        cell = self.board[row][col]
        if cell == '~':
            self.board[row][col] = 'O'
            return 'miss'
        elif cell == 'S':
            self.board[row][col] = 'X'
            return 'hit'
        else:
            return 'alr_shot'
        
class AIBoard(Board):
    def __init__(self, size):
        super().__init__(size)

    def display(self):
        # Hide ships (show ~ instead of S)
        label_width = len(str(self.size))
        header = ' ' * label_width + ' ' + ' '.join(chr(ord('A') + i) for i in range(self.size))
        print(header)
        for row_index, row in enumerate(self.board, start=1):
            hidden_row = ['~' if cell == 'S' else cell for cell in row]
            print(f"{row_index:>{label_width}} {' '.join(hidden_row)}")

    def place_ship_random(self, ship):
        while True:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            orien = random.choice(['H', 'V'])
            coords = chr(ord('A') + col) + str(row + 1)
            if self.place_ship(ship, coords, orien):
                return True

class Ship:
    def __init__(self, size):
        self.size = size

s4 = Ship(5)
s3 = Ship(4)
s2 = Ship(3)
s1 = Ship(2)
s0 = Ship(2)
ships = [s4, s3, s2, s1, s0]
player_board = Board(10)
ai_board = AIBoard(10)

for i in range(5):
    while True:
        while True:
            coords = input("Input coordinates(A1-J10):")
            if len(coords) >= 2 and coords[0].isalpha() and coords[1:].isdigit():
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
        if player_board.place_ship(ships[i], coords, orient) == True:
            break
        else:
            print("Cannot place ship there - occupied, too close to another ship or out of bounds")
player_board.display()
ai_board.display()
for i in range(5):
    while True:
       if ai_board.place_ship_random(ships[i]):
            break
print("Shooting phase")
player_shots_fired = 0
player_hits = 0
ai_shots_fired = 0
ai_hits = 0
total_ship_hp = sum(ship.size for ship in ships)
while player_hits < total_ship_hp and ai_hits < total_ship_hp:
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
            if len(coords) >= 2 and coords[0].isalpha() and coords[1:].isdigit():
                col = ord(coords[0].upper()) - ord('A')
                row = int(coords[1:])
                if 0 <= col < 10 and 1 <= row <= 10:
                    result = ai_board.shoot(coords)
                    break
            else:
                print("invalid coords")
        
        if result == 'hit':
            player_shots_fired += 1
            player_hits += 1
            print("HIT")
        elif result == 'miss':
            player_shots_fired += 1
            player_turn = False
            print("MISS")
        elif result == "alr_shot":
            print("ALREADY SHOT THERE")

    if player_hits >= total_ship_hp:
        print("you win")
        break
    
    print("AI turn")
    ai_turn = True
    while ai_turn:
        ai_coords = chr(ord('A') + random.randint(0, 9)) + str(random.randint(1, 10))
        result = player_board.shoot(ai_coords)
        print(f'AI shoots: {ai_coords}')
        player_board.display()
        
        if result == 'hit':
            ai_shots_fired += 1
            ai_hits += 1
            print("HIT")
        elif result == 'miss':
            ai_shots_fired += 1
            ai_turn = False
            print("MISS")
        elif result == "alr_shot":
            print("ALREADY SHOT THERE")

    if ai_hits >= total_ship_hp:
        print("you lose")
        break