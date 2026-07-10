from time import sleep
import tkinter

import cv2
from PIL import Image, ImageTk
from pyzbar import pyzbar

root = tkinter.Tk()
root.title('QR reader')
root.geometry('640x488')

CANVAS_X = 640
CANVAS_Y = 480

canvas = tkinter.Canvas(root, width=CANVAS_X, height=CANVAS_Y)
canvas.pack()

cap = cv2.VideoCapture(0)

def capture_code():
	global CANVAS_X, CANVAS_Y

	ret, frame = cap.read()
	if ret == False:
		print("Not Image")
	else:
		image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
		image_pil = Image.fromarray(image_rgb)
		image_tk = ImageTk.PhotoImage(image_pil)
		canvas.image_tk = image_tk
		canvas.create_image(CANVAS_X / 2, CANVAS_Y / 2, image=image_tk)

		decoded_objs = pyzbar.decode(frame)

		if decoded_objs != []:
			for obj in decoded_objs:
				print('Type: ', obj)
			
				str_dec_obj = obj.data.decode('utf-8', 'ignore')
				print('QR coed: {}'.format(str_dec_obj))
				left, top, width, height = obj.rect
				
				canvas.create_rectangle(left, top, left + width, top + height, outline='green', width=5)
				canvas.create_text(left + (width / 2), top - 30, text=str_dec_obj, font=('Helvetica', 20, 'bold'), fill='firebrick1')
		
		
	canvas.after(10, capture_code)
capture_code()
root.mainloop()