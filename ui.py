import os, sys, time
import tkinter as tk
import cv2
from PIL import Image, ImageTk

root = tk.Tk()
root.title("My Application")

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 480

canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT)  
canvas.pack()

cap = cv2.VideoCapture(0)

root.mainloop()
