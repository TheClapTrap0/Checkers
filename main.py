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


class Checker:
    def __init__(self, team, king=False):
        self.team = team
        self.king = king


def init():
    for row in range(boardSize):
        for col in range(boardSize):
            x1, y1 = col * CellSize, row * CellSize
            x2, y2 = col * CellSize + CellSize, row * CellSize + CellSize
            canvas.create_rectangle((x1, y1), (x2, y2), fill=cell_colors[(col + row) % 2], width=0)
    # global matrix
    global Board
    Board = [
        [None, Checker(True), None, Checker(True), None, Checker(True), None, Checker(True)],
        [Checker(True), None, Checker(True), None, Checker(True), None, Checker(True), None],
        [None, Checker(True), None, Checker(True), None, Checker(True), None, Checker(True)],
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
        [Checker(False), None, Checker(False), None, Checker(False), None, Checker(False), None],
        [None, Checker(False), None, Checker(False), None, Checker(False), None, Checker(False)],
        [Checker(False), None, Checker(False), None, Checker(False), None, Checker(False), None]
    ]
    global Images # TODO: save created images somehow
    for i in range(boardSize):
        for j in range(boardSize):
            if Board[i][j] != None and Board[i][j].team == True:
                Board[i][j].image = canvas.create_image(j * CellSize, i * CellSize, anchor=NW, image=images[0])
            elif Board[i][j] != None and Board[i][j].team == False:
                Board[i][j].image = canvas.create_image(j * CellSize, i * CellSize, anchor=NW, image=images[1])

def motion(event):
    global xmouse
    global ymouse
    xmouse, ymouse = event.x, event.y


def valid(checker, x1, y1, x2, y2):
    if checker == None:
        return False
    # checking if the place is occupied
    if Board[y2][x2] != None:
        return False
    # checking if the coords are out of bounds
    if x2 < 0 or x2 >= boardSize or y2 < 0 or y2 >= boardSize:
        return False
    # checking if the movement is in diagonal lines
    if abs(x1 - x2) != abs(y1 - y2):
        return False
    # checking if the player's turn is longer than 1
    if abs(x2 - x1) > 1 and abs(y2 - y1) > 1:
        # case 1: the checker is a king and there are no checkers between it and its destination
        return False
    # else the move is valid
    return True


def returnPossibleTurns(checker, x, y):
    arr = []
    for i in range(boardSize):
        for j in range(boardSize):
            if valid(checker, x, y, j, i):
                # print(i, j)
                arr.append(j + i * boardSize + 1)
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
        canvas.itemconfig(i, fill = color["blackSelected"])


def rclick(event):
    global targetx
    global targety
    global xmouse
    global ymouse
    global sCellX
    global sCellY
    targetx = xmouse // CellSize
    targety = ymouse // CellSize
    if selected == None: return
    if valid(selected, sCellX, sCellY, targetx, targety):
        move(selected, sCellX, sCellY, targetx, targety)


def move(checker, startX, startY, endX, endY):
    global selected
    global Board
    selected = None
    for i in range(CellSize // 4):
        root.after(1)
        canvas.move(checker.image, (endX - startX) * 4, (endY - startY) * 4)
        root.update()
    Board[endY][endX] = Board[startY][startX]
    Board[startY][startX] = None


canvas.pack()
root.bind("<Motion>", motion)
root.bind("<Button-1>", lclick)
root.bind("<Button-3>", rclick)

# main
init()

root.mainloop()
