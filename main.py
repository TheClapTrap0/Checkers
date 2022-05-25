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

Depth = 2


root = Tk()

WHITE = True
BLACK = False

xmouse = 0
ymouse = 0
sCell = 0
sCellX = 0
sCellY = 0
targetx = -1
targety = -1
boardSize = 8
CellSize = 100

PlayWithABot = False

selected = None

possibleTurns = []

canvas = Canvas(root, width=CellSize * boardSize, height=CellSize * boardSize)
Board = []

images = [PhotoImage(file="res\\1b.gif"), PhotoImage(file="res\\1h.gif"),
              PhotoImage(file="res\\1bk.gif"), PhotoImage(file="res\\1hk.gif")]


color = {
    "white": "#d6bea9",
    "black": "#5E544B",
    "whiteSelected": "#A08FBA",
    "blackSelected": "#5E546D"
}
cell_colors = [color["white"], color["black"]]


def SetTurns(white = False, black = False):
    for i in range(boardSize):
        for j in range(boardSize):
            if Board[i][j] != None:
                if Board[i][j].team == WHITE:
                    Board[i][j].turn = white
                else:
                    Board[i][j].turn = black


class Checker:
    def __init__(self, team, turn = None, king=False):
        self.team = team
        if turn != None:
            self.turn = turn
        else:
            self.turn = team
        self.king = king

cellsInit = False
def init():
    global cellsInit
    global canvas
    global root
    global PlayWithABot

    PlayWithABot = askyesno(message="Play with a bot?")
    if not cellsInit:
        for row in range(boardSize):
            for col in range(boardSize):
                x1, y1 = col * CellSize, row * CellSize
                x2, y2 = col * CellSize + CellSize, row * CellSize + CellSize
                canvas.create_rectangle((x1, y1), (x2, y2), fill=cell_colors[(col + row) % 2], width=0, tags='0')

    cellsInit = True
    # global matrix
    global Board

    """
    Board = [
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, Checker(WHITE), None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, Checker(BLACK), None, Checker(BLACK), None, None, None, None],
        [None, None, None, None, None, None, None, None]
    ]
    """
    Board = [
        [None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK)],
        [Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None],
        [None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK)],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None],
        [None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE)],
        [Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None]
    ]

    # deleting remaining checkers from the old game
    for i in range(boardSize):
        for j in range(boardSize):
            canvas.delete("t" + str(i) + str(j))
            root.update()
            if Board[i][j] != None and Board[i][j].team == WHITE:
                Board[i][j].image = canvas.create_image(j * CellSize, i * CellSize, anchor=NW, image=images[0], tags="t" + str(i) + str(j))
                Board[i][j].tag = "t" + str(i) + str(j)
            elif Board[i][j] != None and Board[i][j].team == BLACK:
                Board[i][j].image = canvas.create_image(j * CellSize, i * CellSize, anchor=NW, image=images[1], tags="t" + str(i) + str(j))
                Board[i][j].tag = "t" + str(i) + str(j)

    root.update()
    # SetTurns(WHITE, BLACK)
    # Bot()



def motion(event):
    global xmouse
    global ymouse
    xmouse, ymouse = event.x, event.y


def valid(checker, x, y):
    global Board
    arr = []
    if checker == None: return False
    for i in range(-1, 2, 2):
        for j in range(-1, 2, 2):
            if not checker.king and checker.team == BLACK:
                if i == -1: break
            elif not checker.king and checker.team == WHITE:
                if i == 1: break
            for k in range(1, boardSize if checker.king else 2):
                try:
                    t = Board[y + (k * i)][x + (k * j)]
                except IndexError:
                    break
                if t != None:
                    break
                else:
                    tx, ty = (x + (k * j)), (y + (k * i))
                    tt = tx + ty * boardSize + 1
                    if tx >= 0 and tx < boardSize and ty >= 0 and ty < boardSize:
                        arr.append(tt)
    return arr


def attack(checker, x, y):
    global Board
    arr = []
    if checker == None: return False
    for i in range(-1, 2, 2):
        for j in range(-1, 2, 2):
            checkerFound = False
            for k in range(1, boardSize if checker.king else 3):
                try:
                    t = Board[y + (k * i)][x + (k * j)]
                except IndexError:
                    break
                if t != None:
                    if t.team == checker.team: break
                    if checkerFound: break
                    checkerFound = True
                elif checkerFound:
                    tx, ty = (x + (k * j)), (y + (k * i))
                    tt = (x + (k * j)) + (y + (k * i)) * boardSize + 1
                    if tx >= 0 and tx < boardSize and ty >= 0 and ty < boardSize:
                        arr.append(tt)
    return arr


def returnPossibleTurns(checker, x, y):
    global boardSize
    global Board

    arr = []
    if (checker != None and checker.turn == False) or checker == None:
        return arr

    arr = attack(checker, x, y)

    AttacksInTeamPossible = False

    for i in range(boardSize):
        for j in range(boardSize):
            if Board[i][j] != None and Board[i][j].team == checker.team and len(attack(Board[i][j], j, i)) > 0:
                AttacksInTeamPossible = True

    if len(arr) == 0 and not AttacksInTeamPossible:
        arr = valid(checker, x, y)
    return arr


def lclick(event):
    if(GetTurn() == False and PlayWithABot): return
    global sCell
    global sCellX
    global sCellY
    global selected
    global possibleTurns
    global Board
    n = (xmouse // CellSize) + 1 + (boardSize * (ymouse // CellSize))
    canvas.itemconfig(sCell,
                      fill=color["black"] if (sCellY + sCellX + 1) % 2 == 0 else color["white"])
    prevx, prevy = sCellX, sCellY
    sCell = n
    sCellX = xmouse // CellSize
    sCellY = ymouse // CellSize
    canvas.itemconfig(sCell,
                      fill=color["blackSelected"] if (ymouse // CellSize + xmouse // CellSize + 1) % 2 == 0 else color[
                          "whiteSelected"])
    selected = Board[sCellY][sCellX]
    # highlighting of all possible moves
    for i in possibleTurns:
        canvas.itemconfig(i, fill=color["black"])
    possibleTurns = returnPossibleTurns(selected, sCellX, sCellY)
    for i in possibleTurns:
        canvas.itemconfig(i, fill=color["blackSelected"])


def rclick(event):
    if(GetTurn() == False and PlayWithABot): return
    global possibleTurns
    global targetx
    global targety
    global xmouse
    global ymouse
    global sCellX
    global sCellY
    targetx = xmouse // CellSize
    targety = ymouse // CellSize
    if selected == None: return
    if (targetx + targety * boardSize + 1) in possibleTurns:
        move(selected, sCellX, sCellY, targetx, targety)


def GetTurn():
    for i in range(boardSize):
        for j in range(boardSize):
            checker = Board[i][j]
            if checker != None:
                if checker.team == WHITE and checker.turn:
                    return True
                elif checker.team == BLACK and checker.turn:
                    return False
    return None


def CountCheckers():
    global Board
    blackCount = 0
    whiteCount = 0
    for i in range(boardSize):
        for j in range(boardSize):
            c = Board[i][j]
            if c != None and c.team == WHITE:
                whiteCount += 1
            elif c != None and c.team == BLACK:
                blackCount += 1
    return whiteCount, blackCount


def CountQueens():
    global Board
    blackCount = 0
    whiteCount = 0
    for i in range(boardSize):
        for j in range(boardSize):
            c = Board[i][j]
            if c != None and c.team == WHITE and c.king:
                whiteCount += 1
            elif c != None and c.team == BLACK and c.king:
                blackCount += 1
    return whiteCount, blackCount

def move(checker, startX, startY, endX, endY):
    global selected
    global Board
    global possibleTurns
    selected = None
    for i in range(CellSize // 4):
        root.after(1)
        canvas.move(checker.image, (endX - startX) * 4, (endY - startY) * 4)
        root.update()
    Board[endY][endX] = Board[startY][startX]
    Board[startY][startX] = None
    for i in possibleTurns:
        canvas.itemconfig(i, fill=color["black"])

    # switching all the turn values
    SetTurns(checker.team == BLACK, checker.team == WHITE)

    dy, dx = (endY - startY) // abs(endY - startY), (endX - startX) // abs(endX - startX)
    i = 1
    t1, t2 = startY + dy * i, startX + dx * i
    while t1 != endY or t2 != endX:
        t1, t2 = startY + dy * i, startX + dx * i
        t = Board[t1][t2]
        # print(t1,t2)
        if t != None and t1 != endY and t2 != endX:
            canvas.delete(t.tag)
            Board[t1][t2] = None
            root.update()
            arr = attack(checker, endX, endY)
            if(len(arr) > 0):
                SetTurns()
                checker.turn = True
            break
        i += 1

    # checking if the move was to the 0th or the 7th row
    if ((endY == 0 and checker.team == WHITE) or (endY == 7 and checker.team == BLACK)) and checker.king == False:
        Board[endY][endX].king = True
        t1 = Board[endY][endX].tag # fix this !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        canvas.delete(Board[endY][endX].tag)
        Board[endY][endX].image = canvas.create_image(endX * CellSize, endY * CellSize, anchor=NW,
                                                      image=images[2] if Board[endY][endX].team == WHITE else images[3]
                                                      , tags = t1)
        root.update()

    blackCount, whiteCount = CountCheckers()

    if (blackCount == 0 and askyesno(message="White has won. Restart?")) or (whiteCount == 0 and askyesno(message="Black has won. Restart?")):
        init()
    elif blackCount == 0 or whiteCount == 0:
        exit(0)

    if(PlayWithABot):
        Bot()


def Bot():
    global Board
    if(GetTurn()): return
    BestTurn = [None, None, None]
    MaxScore = 0
    # creating the array with all possible turns tt = (x + (k * j)) + (y + (k * i)) * boardSize + 1
    for i in range(boardSize):
        for j in range(boardSize):
            checker = Board[i][j]
            turns = returnPossibleTurns(checker, j, i)
            if len(turns) > 0:
                for k in turns:
                    bufferBoard = Board
                    whiteCount, blackCount = CountCheckers()
                    whiteQueens, blackQueens = CountQueens()
                    whiteCount += whiteQueens
                    blackCount += blackQueens
                    score = blackCount - whiteCount
                    x, y = ((k - 1) % boardSize), ((k - 1) // boardSize)



    """
    item = random.choice(tuple(arr))
    turn = random.choice(tuple(returnPossibleTurns(item[0], item[1], item[2])))
    move(item[0], item[1], item[2], ((turn - 1) % boardSize), ((turn - 1) // boardSize))
    """




# main

canvas.pack()
root.bind("<Motion>", motion)
root.bind("<Button-1>", lclick)
root.bind("<Button-3>", rclick)

init()

root.mainloop()
