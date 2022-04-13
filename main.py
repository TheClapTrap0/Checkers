# шашки -> бот ->графика питон? -> сервер для игры с ботом
# ▮▯♟♙
from tkinter import *
import time

root = Tk()

WHITE = True;
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

selected = None

possibleTurns = []

canvas = Canvas(root, width=CellSize * boardSize, height=CellSize * boardSize)
Board = []

images = [PhotoImage(file="res\\1b.gif"), PhotoImage(file="res\\1h.gif"), PhotoImage(file="res\\1bk.gif"),
          PhotoImage(file="res\\1hk.gif")]
color = {
    "white": "#d6bea9",
    "black": "#5E544B",
    "whiteSelected": "#A08FBA",
    "blackSelected": "#5E546D"
}
cell_colors = [color["white"], color["black"]]


def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)


class Checker:
    def __init__(self, team, king=False):
        self.team = team
        self.king = king


def init():
    for row in range(boardSize):
        for col in range(boardSize):
            x1, y1 = col * CellSize, row * CellSize
            x2, y2 = col * CellSize + CellSize, row * CellSize + CellSize
            canvas.create_rectangle((x1, y1), (x2, y2), fill=cell_colors[(col + row) % 2], width=0, tags='0')
    # global matrix
    global Board
    """
    Board = [
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, Checker(BLACK), None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [None, Checker(WHITE), None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None]
    ]
    """
    Board = [
        [None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE)],
        [Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None],
        [None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE), None, Checker(WHITE)],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None],
        [None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK)],
        [Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None, Checker(BLACK), None]
    ]
    global Images
    for i in range(boardSize):
        for j in range(boardSize):
            if Board[i][j] != None and Board[i][j].team == WHITE:
                Board[i][j].image = canvas.create_image(j * CellSize, i * CellSize, anchor=NW, image=images[0],
                                                        tags="t" + str(i) + str(j))
                Board[i][j].tag = "t" + str(i) + str(j)
            elif Board[i][j] != None and Board[i][j].team == BLACK:
                Board[i][j].image = canvas.create_image(j * CellSize, i * CellSize, anchor=NW, image=images[1],
                                                        tags="t" + str(i) + str(j))
                Board[i][j].tag = "t" + str(i) + str(j)


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
            if not checker.king and checker.team == WHITE:
                if i == -1: break
            elif not checker.king and checker.team == BLACK:
                if i == 1: break
            for k in range(1, boardSize if checker.king else 2):
                try:
                    t = Board[y + (k * i)][x + (k * j)]
                except IndexError:
                    break
                if t != None:
                    break
                else:
                    tt = (x + (k * j)) + (y + (k * i)) * boardSize + 1
                    if (x + (k * j)) >= 0 and (x + (k * j)) < boardSize and (y + (k * i)) >= 0 and (y + (k * i)) < boardSize:
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
                    tt = (x + (k * j)) + (y + (k * i)) * boardSize + 1
                    if (x + (k * j)) >= 0 and (x + (k * j)) < boardSize and (y + (k * i)) >= 0 and (y + (k * i)) < boardSize:
                        arr.append(tt)
    return arr


def returnPossibleTurns(checker, x, y):
    arr = []
    arr = attack(checker, x, y)
    if len(arr) == 0:
        arr = valid(checker, x, y)
    return arr


def lclick(event):
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

    # dy, dx = clamp(endY - startY, -1, 1), clamp(endX - startX, -1, 1)
    dy, dx = (endY - startY) // abs(endY - startY), (endX - startX) // abs(endX - startX)
    i = 1
    t1, t2 = startY + dy * i, startX + dx * i
    while t1 != endY or t2 != endX:
        t1, t2 = startY + dy * i, startX + dx * i
        t = Board[t1][t2]
        if t != None and t1 != endY and t2 != endX:
            canvas.delete(t.tag)
            Board[t1][t2] = None
            root.update()
            break
        i += 1

    # checking if the move was to the 0th or the 7th row
    if ((endY == 0 and checker.team == BLACK) or (endY == 7 and checker.team == WHITE)) and checker.king == False:
        Board[endY][endX].king = True
        canvas.delete(Board[endY][endX].tag)
        Board[endY][endX].image = canvas.create_image(endX * CellSize, endY * CellSize, anchor=NW,
                                                      image=images[2] if Board[endY][endX].team == WHITE else images[3])


canvas.pack()
root.bind("<Motion>", motion)
root.bind("<Button-1>", lclick)
root.bind("<Button-3>", rclick)

# main
init()

root.mainloop()
