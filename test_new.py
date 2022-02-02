import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root)
canvas.pack()

shape_id = canvas.create_oval(0, 0, 100, 100, fill = "#614f42")

def move_oval(event):
    canvas.coords(shape_id, event.x - 50, event.y - 50, event.x + 50, event.y + 50)

canvas.bind('<1>', move_oval)

root.mainloop()