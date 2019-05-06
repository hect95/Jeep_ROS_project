#!/usr/bin/env python

import numpy as np
import cv2
from math import hypot
import socket
import time
from functions.utils import *

#libreria ros
import rospy
from std_msgs.msg import String

#convertidor entre ros y opencv
from cv_bridge import CvBridge, CvBridgeError

from sensor_msgs.msg import Image

avgValue=[]

#lineas dominantes de carril


#ROI para recortes
pts= np.array([[100, 320], [240, 220], [420, 220], [560, 320]])
pts= np.array([[0, 0], [0, 720], [1280, 720], [1280, 0]])
puntos= np.array([[0, 0], [0, 720], [1280, 720], [1280, 0]])#sin recorte

#rango de valores de rojo en HSV
rojo_bajos1 = np.array([0, 50, 50])
rojo_altos1 = np.array([12, 255, 255])
rojo_bajos2 = np.array([160, 50, 50])
rojo_altos2 = np.array([188, 255, 255])

#rango de valores de amarillo en HSV
amarillo_bajos1 = np.array([13, 50, 50])
amarillo_altos1 = np.array([60, 255, 255])
amarillo_bajos2 = np.array([189, 50, 50])
amarillo_altos2 = np.array([215, 255, 255])

camara = "carriles7.mp4"

output_image_pub = rospy.Publisher('/lane_detector/out_image', Image, queue_size=2)

def image2_callback (msg):
	frame = CvBridge().imgmsg_to_cv2(msg, "bgr8")
	
	start_time = time.time()
	
	max_right_line = None
	max_left_line = None
	maxsizeL=0
	maxsizeR=0
	X=0
	
    #copia de frame 
	recorte=frame.copy()
	mask = np.zeros(recorte.shape[:2], np.uint8)

	#suavizado de imagen para evitar ruido
	rect_image=cv2.GaussianBlur(recorte,(11, 11), 0)
	
	#cambio a escala degrises
	rect_image= cv2.cvtColor(rect_image, cv2.COLOR_BGR2GRAY)

	rect_warped = perspective_warp(rect_image, dst_size=(rect_image.shape[1], rect_image.shape[0]))

	#detector de bordes
	edges= cv2.Canny(rect_warped, 1 , 50, apertureSize=3)

	#recorte de zona de interes
	dst = image_roi(edges, puntos)
	roi_rojo = image_roi(frame, puntos)
	
	# lines = cv2.HoughLinesP(dst,1,np.pi/180,10, maxLineGap=50)
	
	#cambio a HSV
	hsv = cv2.cvtColor(roi_rojo, cv2.COLOR_BGR2HSV)
	
	hsv_warped = perspective_warp(hsv, dst_size=(hsv.shape[1], hsv.shape[0]))
	cv2.imshow("hsv_warped", hsv_warped)
	#definir kernel para operaciones morfologicas
	kernel_m = np.ones((1,1),np.uint8)
	
	#definir kernel para mascara de rojos
	kernel_r = np.ones((5,5),np.uint8)
	
	#mascara de rojos
	mask1 = cv2.inRange(hsv, rojo_bajos1, rojo_altos1)
	mask2 = cv2.inRange(hsv, rojo_bajos2, rojo_altos2)
	
	#mask1 = cv2.erode(mask1,kernel_r, iterations = 1)
	#mask2 = cv2.erode(mask2,kernel_r, iterations = 1)
	
	#mascara de amarillos
	mask5 = cv2.inRange(hsv, amarillo_bajos1, amarillo_altos1)
	mask6 = cv2.inRange(hsv, amarillo_bajos2, amarillo_altos2)
	
	#or mascaras de rojos
	rojos = cv2.add(mask1, mask2)
	
	#or mascaras de rojos
	amarillos = cv2.add(mask5, mask6)
	amarillos = cv2.morphologyEx(amarillos, cv2.MORPH_CLOSE, kernel_r)
	amarillos = cv2.dilate(amarillos, kernel_r, iterations = 3)
	amarillos = cv2.bitwise_not(amarillos)
	
	final = cv2.bitwise_and(rojos, amarillos)
	
	#final = cv2.erode(final, kernel_r, iterations = 1)
	
	#blured=cv2.medianBlur(frame, 7)
	
	#sobel = pipeline(blured)
	
	#roi_sobel = image_roi(final, pts)
	
	warped = perspective_warp(final, dst_size=(frame.shape[1], frame.shape[0]))
	out_img, curves, lanes, ploty = sliding_window(warped, margin=int(frame.shape[1]*.045))
	curverad=get_curve(frame, curves[0],curves[1])
	img_ = draw_lanes(frame, curves[0], curves[1])

	lines = cv2.HoughLinesP(final,1,np.pi/180,50, maxLineGap=10)
	
	height, width = frame.shape[:2]
	if lines is not None:
		for line in lines:
			x1, y1, x2, y2 = line[0]
			size = hypot(x2-x1, y2-y1)
			if x1 < width/2:#izquierda
				cv2.line(frame, (x1, y1),(x2, y2), (255, 255, 0),4)
				if size>maxsizeL:
					max_left_line=(x1, y1, x2, y2)
					maxsizeL=size
			else:#derecha
				cv2.line(frame, (x1, y1),(x2, y2), (100, 0, 255),4)
				if size>maxsizeR:
					max_right_line=(x1, y1, x2, y2)
					maxsizeR=size

	#dibujar linea derecha e izquierda
	if max_right_line is not None and max_left_line is not None:
		cv2.line(frame,(max_right_line[0], max_right_line[1]), (max_right_line[2], max_right_line[3]),(244, 133, 63), 8)
		cv2.line(frame,(max_left_line[0], max_left_line[1]), (max_left_line[2], max_left_line[3]),(83, 168, 52), 8)
		avgX= (max_right_line[2]+max_left_line[0])/2
		avgValue.append(avgX)
		if len(avgValue)>5:
			avgValue.pop(0)
			X = int(np.mean(avgValue))
	#print "length array", len(avgValue), "value", avgValue
	if X is not None and X is not 0 :
		cv2.line(frame, (X, height-100), (X, height-100), (0, 255, 255), 8)
	height, width = frame.shape[:2]
	cv2.line(recorte, (width/2, height-100),(width/2, height-100), (0, 0, 255),8)
	
	
	#numpy_vertical_1 = np.vstack((rojos, amarillos))
	#umpy_vertical_2 = np.hstack((frame, final))


	numpy_horizontal_concat = np.concatenate((out_img, frame, img_), axis = 1)

	cv2.imshow("Filtros", numpy_horizontal_concat)
	#cv2.imshow("Resultados", frame)
	#cv2.imshow("Result", frame)
	#cv2.imshow("rojos", rojos)
	#cv2.imshow("amarillos", amarillos)
	cv2.imshow("fdsaj", final)
	cv2.imshow("dst", dst)
	
	#cv2.imshow("out", out_img)
	#cv2.imshow("hola",dst)
	#cv2.imshow("image", img_)
	
	print("-----%s segundo de ejecuccion    ----" % (time.time()-start_time))	
	
	cv2.waitKey(1)
	


def image_roi(img, roi_pts):
	
	img_copy = img.copy()
	mask = np.zeros(img_copy.shape[:2], np.uint8)
	cv2.drawContours(mask, [roi_pts], -1, (255, 255, 255), -1, cv2.LINE_AA)
	roi=cv2.bitwise_and(img_copy, img_copy, mask=mask)
	
	return roi

	
if __name__ == '__main__':

	rospy.init_node('lane_testing', anonymous=True)

	
	rospy.Subscriber(rospy.get_param("~subscriber_topic_2"), Image, image2_callback,queue_size=2,buff_size=52428800)	

	
	try:
		rospy.spin()
	except KeyboardInterrupt:
		print("Shutting down")	
		cv2.destroyAllWindows()


