import numpy as np
import cv2
from models.image import Image

def apply_sobel(image: Image) -> Image:
    grayscale_image = cv2.cvtColor(image.image_data, cv2.COLOR_BGR2GRAY)

    sobel_x = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]))
    sobel_y = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]))

    sobel_edges = np.sqrt(sobel_x**2 + sobel_y**2)

    return Image(sobel_edges)

def apply_roberts(image: Image) -> Image:
    grayscale_image = cv2.cvtColor(image.image_data, cv2.COLOR_BGR2GRAY)

    roberts_x = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[1, 0], [0, -1]]))
    roberts_y = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[0, 1], [-1, 0]]))

    roberts_edges = np.sqrt(roberts_x**2 + roberts_y**2)

    return Image(roberts_edges)

def apply_prewitt(image: Image) -> Image:
    grayscale_image = cv2.cvtColor(image.image_data, cv2.COLOR_BGR2GRAY)

    prewitt_x = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]))
    prewitt_y = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]]))

    prewitt_edges = np.sqrt(prewitt_x**2 + prewitt_y**2)

    return Image(prewitt_edges)

def apply_canny(image: Image) -> Image:
    grayscale_image = cv2.cvtColor(image.image_data, cv2.COLOR_BGR2GRAY)

    canny_edges = cv2.Canny(grayscale_image, 50, 150)

    return Image(canny_edges)