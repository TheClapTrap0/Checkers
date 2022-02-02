# шашки -> бот ->графика питон? -> сервер для игры с ботом
# ▮▯♟♙
from tkinter import *

root = Tk()

xmouse = 0
ymouse = 0
sCell = 0
sCellX = 0
sCellY = 0
BRD_ROWS = BRD_COLS = 8
CellSize = 100

canvas = Canvas(root, width=CellSize * BRD_ROWS, height=CellSize * BRD_COLS)
im = PhotoImage(file="res\\1b.gif")
canvas.create_image(300, 300, anchor=NW, image=im, tag='ani')
print("1")
canvas.pack()

root.mainloop()
