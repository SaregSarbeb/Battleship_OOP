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
        if orien not in ('H', 'V'):
            raise ValueError("Orientation must be H or V")
        if row > self.size or col > self.size:
            raise ValueError("Ship coordinates are invalid")
        
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

class Ship:
    def __init__(self, size):
        self.size = size

s4 = Ship(5)
s3 = Ship(4)
s2 = Ship(3)
s1 = Ship(2)
s0 = Ship(2)
a = Board(10)
ships = [s4, s3, s2, s1, s0]

for i in range(5):
    while True:
        while True:
            coords = input("Input coordinates(A1-J10):")
            if len(coords) >= 2 and coords[0].isalpha() and coords[1:].isdigit():
                break
            else:
                print("Invalid coordinates")
        while True:
            orient = input("Input ship orientation(H or V):")
            if orient.upper() not in ('H', 'V'):
                print("Invalid orientation")
            else:
                break
        if a.place_ship(ships[i], coords, orient) == True:
            break
        else:
            print("Cannot place ship there - occupied, too close to another ship or out of bounds")
    a.display()