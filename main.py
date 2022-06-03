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

root = Tk()

xmouse = 0
ymouse = 0
selectedCell = 0
targetCell = -1
CellSize = 100

PlayWithABot = False

possibleTurns = []

canvas = Canvas(root, width=CellSize * 8, height=CellSize * 8)
Board = []
checkers = {}

images = [PhotoImage(file="res\\1b.gif"), PhotoImage(file="res\\1h.gif"),
              PhotoImage(file="res\\1bk.gif"), PhotoImage(file="res\\1hk.gif")]

direction = [-9, -7, 7, 9]

color = {
    "white": "#d6bea9",
    "black": "#5E544B",
    "whiteSelected": "#A08FBA",  # the white selected color is actually useless
    "blackSelected": "#5E546D"
}
cell_colors = [color["white"], color["black"]]

def SetTurns(n): # 0 none turn, 1 white turn, 2 black turn
    global Board
    for i in range(64):
        if not Board[i] & 1: continue
        if Board[i] & 8:
            Board[i] -= 8 # equals: Board[i] &= 0b00111
        if (n == 2 and Board[i] & 2) or (n == 1 and not Board[i] & 2):
            Board[i] += 8 # equals: Board[i] &= 0b01111

cellsInit = False
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

    # deleting remaining checkers from the old game
    for i in range(64):
        canvas.delete("t" + str(i))
        if Board[i] > 0:
            checkers[i] = canvas.create_image((i % 8 + .5) * CellSize, (i // 8 + .5) * CellSize, anchor=CENTER, image=images[0 if Board[i] == 1 else 1], tag="t" + str(i))

    root.update()
    SetTurns(1)



def motion(event):
    global xmouse
    global ymouse
    xmouse, ymouse = event.x, event.y


def getDistInDir(x, dir):
    count = 0
    # only going on if the current tile is not on a border
    while x > 7 and x < 56 and x != (x // 8) and x != (x // 8) - 1 and x != 63:
        count += 1
        x += dir
    return count


def getNonAttacks(x):
    global Board
    arr = []
    if not Board[x] & 8: return arr
    for i in range(4):

        #restricting movement if the pawns
        if not Board[x] & 4 and Board[x] & 2: # black
            if i < 2: break # restricting the moving direction to down
        elif not Board[x] & 4 and not Board[x] & 2: # white
            if i > 1: break # restricting the moving direction to up

        for k in range(getDistInDir(x, direction[i])):
            target = Board[x + k * direction[i]]

            if target == 0:
                arr.append(x + k * direction[i] + 1)
            elif k > 0:
                break # hit some checker, movement in this direction not possible, changing direction

            if(not Board[x] & 4 and k == 1): # exiting the loop if the checker is not a king
                break
    return arr


def getAttacks(x):
    global Board
    arr = []
    if not Board[x] & 8: return arr
    for i in range(4):
        checkerFound = False
        for k in range(getDistInDir(x, direction[i])):
            target = Board[x + k * direction[i]]
            if target > 0 and k > 0:
                if ((target & 2) == (Board[x] & 2)) or checkerFound: break
                checkerFound = True
            elif checkerFound:
                arr.append(x + k * direction[i] + 1)

            if (not Board[x] & 4 and k == 2):  # exiting the loop if the checker is not a king
                break
    return arr


def getMoves(x):
    global Board

    arr = []
    if not Board[x] & 8:
        return arr

    arr = getAttacks(x)

    AttacksInTeamPossible = False

    for i in range(64):
        if Board[i] & 1 and Board[i] & 2 and Board[x] & 2 and len(getAttacks(i)) > 0:
            AttacksInTeamPossible = True

    if len(arr) == 0 and not AttacksInTeamPossible:
        arr = getNonAttacks(x)
    return arr


def lclick(event):
    if(GetTurn() == False and PlayWithABot): return
    global selectedCell
    global possibleTurns
    global Board
    selectedCell = (xmouse // CellSize) + (8 * (ymouse // CellSize))
    # highlighting of all possible moves
    possibleTurns = getMoves(selectedCell)
    for i in possibleTurns:
        canvas.itemconfig(i, fill=color["blackSelected"])

    # updating checkers position so that it follows the mouse
    canvas.coords(checkers[selectedCell], xmouse, ymouse)


def mouseDrag(event):
    # updating checkers position so that it follows the mouse
    # canvas.coords(checkers[selectedCell], xmouse, ymouse)
    canvas.coords(checkers[selectedCell], event.x, event.y)


def lclickRelease(event):
    if(GetTurn() == False and PlayWithABot): return
    global possibleTurns
    global targetCell
    global xmouse
    global ymouse
    for i in possibleTurns:
        canvas.itemconfig(i, fill=color["black"])
    targetCell = (xmouse // CellSize) + (8 * (ymouse // CellSize))
    if targetCell in possibleTurns:
        moveChecker(selectedCell, targetCell)
    else:
        moveChecker(selectedCell, selectedCell)


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


def CountQueens():
    global Board
    blackCount = 0
    whiteCount = 0
    for i in range(64):
        if Board[i] & 1:
            if Board[i] & 2 and Board[i] & 4:
                whiteCount += 1
            elif not Board[i] & 2 and Board[i] & 4:
                blackCount += 1
    return whiteCount, blackCount

def moveChecker(x1, x2):
    canvas.move(checkers[x1], x2 % 8 * CellSize, x2 // 8 * CellSize)
    checkers[x2] = checkers[x1]
    del checkers[x1]


"""def move(x1, x2):
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
""" # legacy move function


def Bot():
    global Board
    if(GetTurn()): return
    BestTurn = [None, None, None]
    MaxScore = 0
    # creating the array with all possible turns tt = (x + (k * j)) + (y + (k * i)) * 8 + 1
    for i in range(8):
        for j in range(8):
            checker = Board[i][j]
            turns = getMoves(checker, j, i)
            if len(turns) > 0:
                for k in turns:
                    bufferBoard = Board
                    whiteCount, blackCount = CountCheckers()
                    whiteQueens, blackQueens = CountQueens()
                    whiteCount += whiteQueens
                    blackCount += blackQueens
                    score = blackCount - whiteCount
                    x, y = ((k - 1) % 8), ((k - 1) // 8)



    """
    item = random.choice(tuple(arr))
    turn = random.choice(tuple(returnPossibleTurns(item[0], item[1], item[2])))
    move(item[0], item[1], item[2], ((turn - 1) % 8), ((turn - 1) // 8))
    """




# main

canvas.pack()
root.bind("<Motion>", motion)
root.bind("<Button-1>", lclick)
root.bind("<ButtonRelease-1>", lclickRelease)
root.bind("<B1-Motion>", mouseDrag)

init()
print(GetTurn())
root.mainloop()
