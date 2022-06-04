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

visualizeSearch = False # Toggle to visualize the search algorithm of the bot
secondsAfterSync = .5 # the amount of seconds the game is paused for after each move

root = Tk() # root for tkinter
selectedCell = 0 # index of the selected cell in matrix
targetCell = -1 # index of the targeted cell in matrix
CellSize = 100 # the size of a cell in pixels
PlayWithABot = False # determines whether black is a bot or a second player
possibleMoves = [] # possible moves for the selected checker are stored here
depth = 5 # the amount of turns the bot plans ahead !!!!! ALWAYS HAS TO BE ODD, OR THE BOT WILL PLAY IN FAVOR OF PLAYER
queenWeight = 3 # the amount of pawns one queen is worth for the bot
movesHistory = [0] # previous turns are stored here. Up to [depth] elements
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
bestMove = [] # used in bot code

def SetTurns(n): # 0 none turn, 1 white turn, 2 black turn
    for i in range(64):
        if not Board[i] & 1: continue
        if Board[i] & 8:
            Board[i] -= 8 # equals: Board[i] &= 0b00111
        if (n == 2 and Board[i] & 2) or (n == 1 and not Board[i] & 2):
            Board[i] += 8 # equals: Board[i] &= 0b01111

cellsInit = False # used to make sure that the tiles are only initiated once
def Init():
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

    SyncVisuals()

    SetTurns(1)

def SyncVisuals():
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

    time.sleep(secondsAfterSync)

def GetDistInDir(x, dir):
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

def GetNonAttacks(x):
    arr = []
    for i in range(4):

        #restricting movement if the pawns
        if not Board[x] & 4 and Board[x] & 2: # black
            if i < 2: continue # restricting the moving direction to down
        elif not Board[x] & 4 and not Board[x] & 2: # white
            if i > 1: continue # restricting the moving direction to up

        for k in range(GetDistInDir(x, direction[i])):
            target = Board[x + k * direction[i]]

            if target == 0:
                arr.append(x + k * direction[i])
            elif k > 0:
                break # hit some checker, movement in this direction not possible, changing direction

            if(not Board[x] & 4 and k == 1): # exiting the loop if the checker is not a king
                break
    return arr

def GetAttacks(x):
    arr = []
    for i in range(4):
        checkerFound = False
        for k in range(GetDistInDir(x, direction[i])):
            target = Board[x + k * direction[i]]
            if target > 0 and k > 0:
                if ((target & 2) == (Board[x] & 2)) or checkerFound: break
                checkerFound = True
            elif checkerFound:
                arr.append(x + k * direction[i])

            if (not Board[x] & 4 and k == 2):  # exiting the loop if the checker is not a king
                break
    return arr

def GetMoves(x):

    arr = []
    if not Board[x] & 8: return arr

    arr = GetAttacks(x)

    AttacksInTeamPossible = False

    for i in range(64):
        if Board[i] & 1 and Board[i] & 2 == Board[x] & 2 and len(GetAttacks(i)) > 0:
            AttacksInTeamPossible = True

    if len(arr) == 0 and not AttacksInTeamPossible:
        arr = GetNonAttacks(x)
    return arr

def Lclick(event):
    if(GetTurn() == True and PlayWithABot): return
    global selectedCell
    global possibleMoves
    selectedCell = (event.x // CellSize) + (8 * (event.y // CellSize))
    # highlighting of all possible moves
    possibleMoves = GetMoves(selectedCell)
    for i in possibleMoves:
        canvas.itemconfig(i + 1, fill=color["blackSelected"])

def LclickRelease(event):
    if(GetTurn() == True and PlayWithABot): return
    global possibleMoves
    global targetCell
    for i in possibleMoves:
        canvas.itemconfig(i + 1, fill=color["black"])
    targetCell = (event.x // CellSize) + (8 * (event.y // CellSize))
    if targetCell in possibleMoves:
        MakeMove(selectedCell, targetCell)
        SyncVisuals()
        EndTurn()

def EndTurn():
    # counting the checkers, checking if the game is over and passing the turn if necessary

    # one of the teams has run out of checkers
    blackCount, whiteCount = CountCheckers()
    if (blackCount == 0 and askyesno(message="White has won. Restart?")) or (
            whiteCount == 0 and askyesno(message="Black has won. Restart?")):
        Init()
    elif blackCount == 0 or whiteCount == 0:
        exit(0)

    # the team who's turn it has no available turns
    if len(GetAllMoves()) == 0 and ((GetTurn() == False and askyesno(message="Black has won. Restart?")) or
                                    (GetTurn() == True and askyesno(message="White has won. Restart?"))):
        Init()
    elif len(GetAllMoves()) == 0 and ((GetTurn() == False) or
                                    (GetTurn() == True)):
        exit(0)

    # passes the turn to bot if the bot is enabled
    if (PlayWithABot and GetTurn() == True):
        Bot()

def GetTurn(): # returns true if it's blacks turn, and false if it's whites turn
    for i in range(64):
        if Board[i] & 1:
            if Board[i] & 2 and Board[i] & 8:
                return True
            elif not Board[i] & 2 and Board[i] & 8:
                return False
    return None

def CountPawns():
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

def CountQueens():
    global Board
    blackCount = 0
    whiteCount = 0
    for i in range(64):
        if Board[i] & 1 and Board[i] & 4:
            if Board[i] & 2:
                whiteCount += 1
            else:
                blackCount += 1
    return whiteCount, blackCount

def CountCheckers():
    cpw, cpb = CountPawns()
    cqw, cqb = CountQueens()
    wc = cpw + cqw
    bc = cpb + cqb
    return wc, bc

def MakeMove(x1, x2):
    # saving the current board to the history to potentially unmake moves
    # After 1.5 hours of pain: append takes the reference of the object, it doesn't create a copy like it would do in a normal programming language wtf
    movesHistory.append(Board.copy()) # the .copy() is VERY important due to: see upper comment
    if len(movesHistory) > depth: del movesHistory[0]

    # applying the actual changes to the board
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
            for j in range(1, GetDistInDir(x1, direction[i])):
                cell = x1 + direction[i] * j
                if Board[cell] & 1 and Board[cell] & 2 != Board[x2] & 2 and firstChecker == None: firstChecker = cell
                if cell == x2 and firstChecker != None:
                    Board[firstChecker] = 0
                    if len(GetAttacks(x2)) > 0:
                        SetTurns(0)
                        Board[x2] += 8
                    break

    # used for bot search visualization
    if PlayWithABot and GetTurn() == True and visualizeSearch:
        SyncVisuals()
        time.sleep(.05)  # in seconds

def UnmakeMove():
    global Board
    Board = movesHistory.pop()

    # used for bot search visualization
    if PlayWithABot and GetTurn() == True and visualizeSearch:
        SyncVisuals()
        time.sleep(.005)  # in seconds

def Bot():
    t = RecursiveSearch(depth)
    MakeMove(bestMove[0], bestMove[1])
    SyncVisuals()
    EndTurn()

def GetAllMoves(): # returns an array of all possible moves
    arr = []
    for i in range(64):
        if Board[i] & 1:
            t = GetMoves(i)
            if len(t) > 0:
                for j in t:
                    arr.append([i, j])
    return arr

def RecursiveSearch(d): # the moves that are made after killing a checker shouldn't be counted
    global bestMove
    if d == 0:
        return Evaluate()

    moves = GetAllMoves()
    if len(moves) == 0: return 0

    bestEvaluation = float("-inf")

    for move in moves:
        MakeMove(move[0], move[1])
        t = -RecursiveSearch(d - 1) # minus sign here because each time the turn is passed to the opponent, and what's good for the opponent is bad for its opponent
        if t > bestEvaluation:
            bestEvaluation = t
            if d == depth:
                bestMove = move
        UnmakeMove()

    return bestEvaluation

def Evaluate():
    whites, blacks = CountPawns()
    wq, bq = CountQueens()
    wq *= queenWeight; bq *= queenWeight
    whites += wq; blacks += bq
    return blacks - whites

# main

canvas.pack()

root.bind("<Button-1>", Lclick)
root.bind("<ButtonRelease-1>", LclickRelease)



Init()
root.mainloop()
