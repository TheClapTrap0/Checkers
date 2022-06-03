# шашки -> бот ->графика питон? -> сервер для игры с ботом
# ▮▯♟♙
"""
Правила игры

Игра ведётся на доске 8х8 клеток, только на черных ячейках
Шашки в начале игры занимают первые три ряда с каждый стороны
Бить можно произвольное количество шашек в любых направлениях
Простые шашки ходят только вперёд
Простая шашка может срубить назад
Дамка ходит на любое число полей в любую сторону
Проигрывает тот, у кого не остается фигур, либо ходов
Шашка снимается с поля после боя (можно перефразировать так: одну шашки нельзя срубить дважды за один ход)
Бить обязательно
Шашка превращается в дамку, достигнув восьмой (для белых) или первой (для черных) линии доски
Если шашка во время боя проходит через дамочное поле, то она превращается в дамку и следующие бои (если они возможны) совершает уже как дамка
"""
from tkinter import *
import time
from tkinter.messagebox import askyesno
import random

root = Tk() # root for tkinter

selectedCell = 0 # index of the selected cell in matrix
targetCell = -1 # index of the targeted cell in matrix
CellSize = 100 # the size of a cell in pixels

PlayWithABot = False # determines whether black is a bot or a second player

possibleMoves = [] # possible moves for the selected checker are stored here

depth = 3 # the amount of turns the bot plans ahead
movesHistory = [] # previous turns are stored here. Up to [depth] elements

canvas = Canvas(root, width=CellSize * 8, height=CellSize * 8) # the canvas from tkinter
Board = [] # the main board matrix
checkers = {} # references to the images of the checkers are stored here

images = [PhotoImage(file="res\\1b.gif"), PhotoImage(file="res\\1h.gif"),
              PhotoImage(file="res\\1bk.gif"), PhotoImage(file="res\\1hk.gif")] # array with the 4 images used for checkers

direction = [-9, -7, 7, 9] # the 4 directions: up right, up left, down right, down left

color = {
    "white": "#d6bea9",
    "black": "#5E544B",
    "whiteSelected": "#A08FBA",  # the white selected color is actually useless
    "blackSelected": "#5E546D"
} # 4 colors used for tiles are stored here
cell_colors = [color["white"], color["black"]] # only used in board init

def SetTurns(n): # 0 none turn, 1 white turn, 2 black turn
    for i in range(64):
        if not Board[i] & 1: continue
        if Board[i] & 8:
            Board[i] -= 8 # equals: Board[i] &= 0b00111
        if (n == 2 and Board[i] & 2) or (n == 1 and not Board[i] & 2):
            Board[i] += 8 # equals: Board[i] &= 0b01111

cellsInit = False # used to make sure that the tiles are only initiated once
def init():
    global cellsInit
    global canvas
    global root
    global PlayWithABot

    if not cellsInit:
        for row in range(8):
            for col in range(8):
                x1, y1 = col * CellSize, row * CellSize
                x2, y2 = col * CellSize + CellSize, row * CellSize + CellSize
                canvas.create_rectangle((x1, y1), (x2, y2), fill=cell_colors[(col + row) % 2], width=0, tags='0')
        cellsInit = True

    PlayWithABot = askyesno(message="Play with a bot?")


    # global matrix
    global Board
    # several bits in following order from right to left: existence status, team, king status, turn status
    # 15 = black king active, 13 = white king active, 11 = black pawn active, 9 = white pawn active,
    # 7 = black king passive, 5 = white king passive, 3 = black pawn passive, 1 = white pawn passive, 0 = none
    # 1 = checker, 2 = black team, 4 = king, 8 = active
    # left up = -9, right up = -7, left down = +7, right down = +9;
    # numbers can also be multiplied to increase travel distance
    Board = [0, 3, 0, 3, 0, 3, 0, 3,
             3, 0, 3, 0, 3, 0, 3, 0,
             0, 3, 0, 3, 0, 3, 0, 3,
             0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0,
             1, 0, 1, 0, 1, 0, 1, 0,
             0, 1, 0, 1, 0, 1, 0, 1,
             1, 0, 1, 0, 1, 0, 1, 0]

    syncVisuals()

    SetTurns(1)

def syncVisuals():
    for i in range(64):
        if i in checkers:
            canvas.delete(checkers[i])
            del checkers[i]
        if Board[i] > 0:
            if Board[i] & 2:
                if Board[i] & 4: imageIndex = 3
                else: imageIndex = 1
            else:
                if Board[i] & 4: imageIndex = 2
                else: imageIndex = 0
            checkers[i] = canvas.create_image((i % 8) * CellSize, (i // 8) * CellSize, anchor=NW, image=images[imageIndex])

    root.update()

def getDistInDir(x, dir):
    count = 1
    # only going on if the current tile is not on a border
    left, up, right, down = x % 8 != 0, x > 7, (x + 1) % 8 != 0, x < 56
    if dir == -9:
        while left and up:
            count += 1
            x += dir
            left, up, right, down = x % 8 != 0, x > 7, (x + 1) % 8 != 0, x < 56
    elif dir == -7:
        while right and up:
            count += 1
            x += dir
            left, up, right, down = x % 8 != 0, x > 7, (x + 1) % 8 != 0, x < 56
    elif dir == 7:
        while left and down:
            count += 1
            x += dir
            left, up, right, down = x % 8 != 0, x > 7, (x + 1) % 8 != 0, x < 56
    elif dir == 9:
        while right and down:
            count += 1
            x += dir
            left, up, right, down = x % 8 != 0, x > 7, (x + 1) % 8 != 0, x < 56
    return count

def getNonAttacks(x):
    arr = []
    for i in range(4):

        #restricting movement if the pawns
        if not Board[x] & 4 and Board[x] & 2: # black
            if i < 2: continue # restricting the moving direction to down
        elif not Board[x] & 4 and not Board[x] & 2: # white
            if i > 1: continue # restricting the moving direction to up

        for k in range(getDistInDir(x, direction[i])):
            target = Board[x + k * direction[i]]

            if target == 0:
                arr.append(x + k * direction[i])
            elif k > 0:
                break # hit some checker, movement in this direction not possible, changing direction

            if(not Board[x] & 4 and k == 1): # exiting the loop if the checker is not a king
                break
    return arr

def getAttacks(x):
    arr = []
    for i in range(4):
        checkerFound = False
        for k in range(getDistInDir(x, direction[i])):
            target = Board[x + k * direction[i]]
            if target > 0 and k > 0:
                if ((target & 2) == (Board[x] & 2)) or checkerFound: break
                checkerFound = True
            elif checkerFound:
                arr.append(x + k * direction[i])

            if (not Board[x] & 4 and k == 2):  # exiting the loop if the checker is not a king
                break
    return arr

def getMoves(x):

    arr = []
    if not Board[x] & 8: return arr

    arr = getAttacks(x)

    AttacksInTeamPossible = False

    for i in range(64):
        if Board[i] & 1 and Board[i] & 2 == Board[x] & 2 and len(getAttacks(i)) > 0:
            AttacksInTeamPossible = True

    if len(arr) == 0 and not AttacksInTeamPossible:
        arr = getNonAttacks(x)
    return arr

def lclick(event):
    if(GetTurn() == False and PlayWithABot): return
    global selectedCell
    global possibleMoves
    selectedCell = (event.x // CellSize) + (8 * (event.y // CellSize))
    # highlighting of all possible moves
    possibleMoves = getMoves(selectedCell)
    for i in possibleMoves:
        canvas.itemconfig(i + 1, fill=color["blackSelected"])

def lclickRelease(event):
    if(GetTurn() == False and PlayWithABot): return
    global possibleMoves
    global targetCell
    for i in possibleMoves:
        canvas.itemconfig(i + 1, fill=color["black"])
    targetCell = (event.x // CellSize) + (8 * (event.y // CellSize))
    if targetCell in possibleMoves:
        makeMove(selectedCell, targetCell)
        syncVisuals()

        # passes the turn to bot if the bot is enabled
        if (PlayWithABot):
            Bot()

def GetTurn(): # returns true if it's whites turn, and false if it's blacks turn
    for i in range(64):
        if Board[i] & 1:
            if Board[i] & 2 and Board[i] & 8:
                return True
            elif not Board[i] & 2 and Board[i] & 8:
                return False
    return None

def CountCheckers():
    global Board
    blackCount = 0
    whiteCount = 0
    for i in range(64):
        if Board[i] & 1:
            if Board[i] & 2:
                whiteCount += 1
            else:
                blackCount += 1
    return whiteCount, blackCount

def makeMove(x1, x2):
    movesHistory.append(Board)
    if len(movesHistory) > depth: del movesHistory[0]
    Board[x2] = Board[x1]
    Board[x1] = 0

    # queen conversion
    if ((not Board[x2] & 2 and x2 < 8) or (Board[x2] & 2 and x2 > 55)) and not Board[x2] & 4:
        Board[x2] += 4

    # switching the turns
    SetTurns(1 if Board[x2] & 2 else 2)

    # killing a checker if there is one and keeping the turn only for the killer, if other kills are available
    if abs(x2 - x1) > 9:
        for i in range(4):
            firstChecker = None
            for j in range(1, getDistInDir(x1, direction[i])):
                cell = x1 + direction[i] * j
                if Board[cell] & 1 and Board[cell] & 2 != Board[x2] & 2 and firstChecker == None: firstChecker = cell
                if cell == x2 and firstChecker != None:
                    Board[firstChecker] = 0
                    if len(getAttacks(x2)) > 0:
                        SetTurns(0)
                        Board[x2] += 8
                    break

    # counting the checkers and checking if the game is over
    blackCount, whiteCount = CountCheckers()
    if (blackCount == 0 and askyesno(message="White has won. Restart?")) or (
            whiteCount == 0 and askyesno(message="Black has won. Restart?")):
        init()
    elif blackCount == 0 or whiteCount == 0:
        exit(0)

def unmakeMove():
    pass

def Bot():
    global Board
    if(GetTurn()): return
    BestTurn = [None, None]
    MaxScore = 0
    # creating the array with all possible turns tt = (x + (k * j)) + (y + (k * i)) * 8 + 1
    for i in range(64):
        if Board[i] == 0 or not Board[i] & 2: continue
        turns = getMoves(i)
        if len(turns) > 0:
            for k in turns:
                bufferBoard = Board
                whiteCount, blackCount = CountCheckers()
                score = blackCount - whiteCount
                x, y = ((k - 1) % 8), ((k - 1) // 8)

def Evaluate():
    whites, blacks = CountCheckers()
    return blacks - whites

# main

canvas.pack()
root.bind("<Button-1>", lclick)
root.bind("<ButtonRelease-1>", lclickRelease)

init()
root.mainloop()
