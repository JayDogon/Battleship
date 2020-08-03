import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


def board_printer(board):
    #prints out a board in ascii
    horizontal = '   A  B  C  D  E  F  G  H'
    print()
    c = 8
    for row in board[::-1]:
        print(c, row)
        c -= 1
    print(horizontal)


def empty_board(rows, columns):
    #returns an empty board
    out = []
    for i in range(rows):
        row = []
        for j in range(columns):
            row.append(0)
        out.append(row)
    return out


Empty = empty_board(8,8)


def fact(n):
    #factorial
    product = 1
    for i in range(1,n+1):
        product *= i
    return product


def list_sum(A):
    #self explanatory
    sum = 0
    for entry in A:
        sum += entry
    return sum


def dictionary_product(A):
    #product over the entries of a dictionary. The empty product is understood to be 1.
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
    #places a ship on a board given its size, orientation as in integer in {0,1} and the coordinate of its tail.
    for i in range(ship):
        board[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] = 1


def ship_remover(board, ship, orientation, tail):
    #self explanatory.
    for i in range(ship):
        board[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] = 0

def ship_check(board, ship, orientation, tail):
    #checks if a ship placement is legal.
    for i in range(ship):
        if board[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] > 0:
            return False
    return True



def heatmap_addition(A, B):
    #adds two matrices.
    out = []
    for row in range(len(A)):
        out.append([])
        for column in range(len(A[row])):
            out[row].append(A[row][column] + B[row][column])
    return out


def heatmap_sum(H):
    #returns the sum of a matrix for normalisation.
    sum = 0
    for row in H:
        sum += list_sum(row)
    return sum


def heatmap_adder(H, ship, orientation, tail, count):
    #adds a ship to a heatmap weighted for the number of configurations in which the placement is possible.
    for i in range(ship):
        H[tail[0] + i*orientation[0]][tail[1] + i*orientation[1]] += count


def heatmap_normalise(H):
    #normalises heatmaps to display data better
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
    #mark certain squares as already checked. Configs including ships in blotted positions are discarded.
    for coordinates in blot:
        board[coordinates[0]][coordinates[1]] = -1


def satisfies(board, check):
    #checks that registered hits are satisfied by a configuration.
    for coordinates in check:
        if board[coordinates[0]][coordinates[1]] != 1:
            return False
    return True


def battleships_work(board, ships, check, heatmap):
    if len(ships) == 0:
        #no ships left to place, configuration is checked before being counted.
        if satisfies(board, check):
            #check that the final configuration satisfies all known locations.
            return board, 1
        return Empty, 0
    rows = len(board)
    columns = len(board[0])
    boards = 0
    ship = ships[0]
    for row in range(rows):
        #check horizontal placement
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
    #takes a heatmap and returns the coordinates with the highest probability/heat
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
    #generates a random board configuration
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


dims = input("board dimensions: ")
dims = dims.split(" ")
Ships = input("ships: ")
Ships = Ships.split(" ")
for i in range(len(Ships)):
    Ships[i] = int(Ships[i])
Board = empty_board(int(dims[0]), int(dims[1]))

Empty = empty_board(int(dims[0]), int(dims[1]))

Heatmap, Board = battleships(Board, Ships, [])

print(Board)
print()

plt.rcParams['figure.facecolor'] = '#fdfdfd'

fig, ax = plt.subplots(figsize = (9,7))
fig.patch.set_facecolor('#fdfdfd')
ax.set_xticks([])
ax.set_yticks([])
ax.axis("off")
ax.set_fc('#fdfdfd')


img = sns.heatmap(Heatmap, cmap='Blues', square=True, cbar=False, linewidths=0.3, ax=ax)
img.patch.set_fc('#fdfdfd')


plt.show()


