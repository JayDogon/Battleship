import numpy as np
import time


def board_printer(board):
    horizontal = '   A  B  C  D  E  F  G  H'
    print()
    c = 8
    for row in board[::-1]:
        print(c, row)
        c -= 1
    print(horizontal)


def empty_board(rows, columns):
    out = []
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append(0)
        out.append(row)
    return out


Empty = empty_board(8,8)


def fact(n):
    product = 1
    for i in range(1,n+1):
        product *= i
    return product


def list_sum(A):
    sum = 0
    for entry in A:
        sum += entry
    return sum


def dictionary_product(A):
    product = 1
    for entry in A:
        product *= A[entry]
    return product


def redundancy_adjust(A):
    redundant = {}
    for i in A:
        if i in redundant:
            redundant[i] += 1
        else:
            redundant[i] = 1
    return dictionary_product(redundant)


def ship_adder(board, ship, orientation, tail):
    for i in range(ship):
        board[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] = 1


def ship_remover(board, ship, orientation, tail):
    for i in range(ship):
        board[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] = 0

def ship_check(board, ship, orientation, tail):
    for i in range(ship):
        if board[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] > 0:
            return False
    return True



def heatmap_addition(A, B):
    out = []
    for row in range(len(A)):
        out.append([])
        for column in range(len(A[row])):
            out[row].append(A[row][column] + B[row][column])
    return out


def heatmap_sum(H):
    sum = 0
    for row in H:
        sum += list_sum(row)
    return sum


def heatmap_adder(H, ship, orientation, tail, count):
    for i in range(ship):
        H[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] += count


def heatmap_normalise(H):
    rows = len(H)
    columns = len(H[0])
    out = []
    sum = heatmap_sum(H)
    for row in range(rows):
        temp_row = []
        for column in range(columns):
            temp_row.append(round(H[row][column]/sum, 4))
        out.append(temp_row)
    return out


def blotter(blot, board):
    for coordinates in blot:
        board[coordinates[0]][coordinates[1]] = -1


def satisfies(board, check):
    for coordinates in check:
        if board[coordinates[0]][coordinates[1]] != 1:
            return False
    return True


def battleships_work(board, ships, check, heatmap):
    if len(ships) == 0:
        if satisfies(board, check):
            #check that the final configuration satisfies all known locations
            return board, 1
        return Empty, 0
    rows = len(board)
    columns = len(board[0])
    boards = 0
    ship = ships[0]
    for row in range(rows):
        c = 0
        while c + ship <= columns:
            if ship_check(board, ship, (0, 1), (row, c)):
                ship_adder(board, ship, (0, 1), (row, c))
                new_heatmap, new_boards = battleships_work(board, ships[1:], check, heatmap)
                heatmap_adder(heatmap, ship, (0, 1), (row, c), new_boards)
                boards += new_boards
                ship_remover(board, ship, (0, 1), (row, c))
            c += 1
    for column in range(columns):
        r = 0
        while r + ship <= rows:
            if ship_check(board, ship, (1, 0), (r, column)):
                ship_adder(board, ship, (1, 0), (r, column))
                new_heatmap, new_boards = battleships_work(board, ships[1:], check, heatmap)
                heatmap_adder(heatmap, ship, (1, 0), (r, column), new_boards)
                ship_remover(board, ship, (1, 0), (r, column))
                boards += new_boards
            r += 1
    return heatmap, boards


def battleships(board, ships, hits, misses):
    size = len(board)
    ships.sort(reverse=True)
    heatmap = empty_board(size, size)
    heatmap, boards = battleships_work(board, ships, hits, heatmap)
    blotter(misses, heatmap)
    for coordinates in hits:
        heatmap[coordinates[0]][coordinates[1]] = -1
    #heatmap = heatmap_normalise(heatmap)
    boards = boards // redundancy_adjust(ships)
    return heatmap, boards


def target_select(heatmap):
    rows = len(heatmap)
    columns = len(heatmap[0])
    max_heat = -1
    max_coords = (0,0)
    for row in range(rows):
        for column in range(columns):
            if heatmap[row][column] > max_heat:
                max_heat = heatmap[row][column]
                max_coords = (row, column)
    return max_coords


def random_config(rows, columns, ships):
    board = empty_board(rows, columns)
    orientations = [(0,1), (1,0)]
    for i in ships:
        while True:
            orientation = np.random.randint(0, 2)
            if orientation == 0:
                row = np.random.randint(0, rows)
                column = np.random.randint(0, columns - i)
            else:
                row = np.random.randint(0, rows - i)
                column = np.random.randint(0, columns)
            if ship_check(board, i, orientations[orientation], (row, column)):
                ship_adder(board, i, orientations[orientation], (row, column))
                break
    return board


def game_auto(size):
    ships = [5, 4, 4, 3]
    board = empty_board(size, size)
    hits = []
    misses = []
    target = random_config(size, size, ships)
    board_printer(target)
    shots = 0
    while len(hits) < 16:
        map = battleships(board, ships, hits, misses)[0]
        move = target_select(map)
        if target[move[0]][move[1]] == 1:
            hits.append((move[0], move[1]))
        else:
            board[move[0]][move[1]] = 2
            misses.append(move)
        shots += 1
        print(hits)
    return shots

sum = 0
n = 1
for i in range(n):
    sum += game_auto(8)

print("average shots: ", sum/n)

def game_human(size):
    coords_letters = 'ABCDEFGH'
    board = empty_board(size, size)
    target = empty_board(size, size)
    hits = []
    misses = []
    print("Please place your ships")
    ships = [5, 4, 3]
    shots = 0
    for i in ships:
        board_printer(target)
        msg = "Would you like to place the ship of length " + str(i) + " 'H'orizontally or 'V'ertically? [H/V]: "
        orientation = input(msg)
        while True:
            if orientation == "H":
                orientation = (0, 1)
                break
            elif orientation == "V":
                orientation = (1, 0)
                break
            else:
                orientation = input("Invalid input. Please enter 'H' or 'V': ")
        tail = input("Where would you like to place the ship (enter the top leftmost coordinate like so 'A 2')?: ")
        while True:
            try:
                tail = tail.split(" ")
                print(tail)
                tail = (coords_letters.index(tail[0]), int(tail[1])-1)
                print(tail)
                print(orientation)
                if ship_check(target, i, orientation, tail):
                    ship_adder(target, i, orientation, tail)
                else:
                    tail = input("Invalid input. Please enter your coordinates as a space separated tuple.")
            except:
                tail = input("Invalid input. Please enter your coordinates as a space separated tuple.")
    while len(hits) < 12:
        map = battleships(board, ships, hits, misses)[0]
        move = target_select(map)
        print(move)
        result = input("'H'it or 'M'iss [H/M]: ")
        while True:
            if result == 'H':
                hits.append(move)
                break
            elif result == 'M':
                board[move[0]][move[1]] = 2
                misses.append(move)
                break
            else:
                result = input("Invalid response. Please enter 'H' or 'M'.: ")
        shots += 1
    return shots


#shots = game_human(8)
#input(shots, "shots.")

