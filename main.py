# шашки -> бот ->графика питон? -> сервер для игры с ботом
# ▮▯♟♙
from tkinter import *
import time

root = Tk()

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
board = []
checkers = []
images = [PhotoImage(file="res\\1b.gif"), PhotoImage(file="res\\1h.gif"), PhotoImage(file="res\\1bk.gif"),
          PhotoImage(file="res\\1hk.gif")]
color = {
    "white": "#d6bea9",
    "black": "#5E544B",
    "whiteSelected": "#A08FBA",
    "blackSelected": "#5E546D"
}
cell_colors = [color["black"], color["white"]]


class Checker:
    def __init__(self, x, y, team, king=False):
        self.x = x
        self.y = y
        self.team = team
        self.king = king
        if self.team == 0:
            self.image = canvas.create_image(x * CellSize, y * CellSize, anchor=NW, image=images[0])
        elif self.team == 1:
            self.image = canvas.create_image(x * CellSize, y * CellSize, anchor=NW, image=images[1])


def init():
    for row in range(boardSize):
        board.append([])
        for col in range(boardSize):
            x1, y1 = col * CellSize, row * CellSize
            x2, y2 = col * CellSize + CellSize, row * CellSize + CellSize
            board.append(canvas.create_rectangle((x1, y1), (x2, y2), fill=cell_colors[(col + row) % 2], width=0))
    # checkers
    global checkers
    checkers = [Checker(0, 0, False), Checker(2, 0, False), Checker(4, 0, False), Checker(6, 0, False),
                Checker(1, 1, False), Checker(3, 1, False), Checker(5, 1, False), Checker(7, 1, False),
                Checker(0, 2, False), Checker(2, 2, False), Checker(4, 2, False), Checker(6, 2, False),
                Checker(1, 5, True), Checker(3, 5, True), Checker(5, 5, True), Checker(7, 5, True), Checker(0, 6, True),
                Checker(2, 6, True), Checker(4, 6, True), Checker(6, 6, True), Checker(1, 7, True), Checker(3, 7, True),
                Checker(5, 7, True), Checker(7, 7, True)]


def motion(event):
    global xmouse
    global ymouse
    xmouse, ymouse = event.x, event.y


def valid(checker, x, y):
    if checker == None:
        return False
    # checking if the place is occupied
    for i in checkers:
        if i.x == x and i.y == y:
            return False
    # checking if the coords are out of bounds
    if x < 0 or x >= boardSize or y < 0 or y >= boardSize:
        return False
    # checking if the movement is in diagonal lines
    if abs(checker.x - x) != abs(checker.y - y):
        return False
    # checking if the checker has to attack
    for i in checkers:
        if abs(i.x - checker.x) != 1 or abs(i.y - checker.y) != 1 or checker.team == i.team:
            return False
    # else the move is valid
    return True


def returnPossibleTurns(checker):
    arr = []
    for i in range(boardSize):
        for j in range(boardSize):
            if abs(checker.x - i) and abs(checker.y - j) and valid(checker, i, j):
                print(i, j)
                arr.append(i + j * boardSize + 1)
    return arr


def lclick(event):
    global sCell
    global sCellX
    global sCellY
    global selected
    global possibleTurns
    n = (xmouse // CellSize) + 1 + (boardSize * (ymouse // CellSize))
    canvas.itemconfig(sCell,
                      fill=color["white"] if (sCellY // CellSize + sCellX // CellSize + 1) % 2 == 0 else color["black"])
    prevx, prevy = sCellX, sCellY
    sCell = n
    sCellX = xmouse
    sCellY = ymouse
    canvas.itemconfig(sCell,
                      fill=color["whiteSelected"] if (ymouse // CellSize + xmouse // CellSize + 1) % 2 == 0 else color[
                          "blackSelected"])
    selected = None
    for i in checkers:
        if i.x == sCellX // CellSize and i.y == sCellY // CellSize:
            selected = i
    # highlighting of all possible moves
    if selected == None:
        return
    for i in possibleTurns:
        canvas.itemconfig(i, fill=color["black"])
    possibleTurns = returnPossibleTurns(selected)
    for i in possibleTurns:
        canvas.itemconfig(i, fill = color["blackSelected"])


def rclick(event):
    global targetx
    global targety
    global xmouse
    global ymouse
    targetx = xmouse // CellSize
    targety = ymouse // CellSize
    if selected == None: return
    if valid(selected, targetx, targety):
        move(selected, targetx - selected.x, targety - selected.y)


def move(checker, deltax, deltay):
    global selected
    selected = None
    for i in range(CellSize // 4):
        root.after(1)
        canvas.move(checker.image, deltax * 4, deltay * 4)
        root.update()
    checker.x, checker.y = checker.x + deltax, checker.y + deltay


canvas.pack()
root.bind("<Motion>", motion)
root.bind("<Button-1>", lclick)
root.bind("<Button-3>", rclick)

# main
init()

root.mainloop()
