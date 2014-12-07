import numpy as np
import cv2
import cv2.cv as cv

from PIL import Image
import sys

import pyocr
import pyocr.builders

import pyperclip

cap = cv2.VideoCapture(1)
ret, frame = cap.read()
cv2.imshow('frame',img)
