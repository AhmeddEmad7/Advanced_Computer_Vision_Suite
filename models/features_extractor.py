import cv2
import numpy as np
from scipy import signal
from scipy.ndimage import convolve
from time import time
from models.image import Image


def rgb2gray(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)


def applyHarris(image, threshold) -> Image:
    window_size = 3
    k = 0.04
    start_time = time()
    # Convert image to grayscale if it's not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = np.copy(image)

    # Compute image gradients using Sobel filters
    Ix = convolve(gray, np.array([[-1, 0, 1]]))
    Iy = convolve(gray, np.array([[-1], [0], [1]]))

    # Compute elements of the structure tensor
    Ix2 = Ix**2
    Iy2 = Iy**2
    Ixy = Ix * Iy

    # Compute sums of the structure tensor elements over the window
    Sxx = convolve(Ix2, np.ones((window_size, window_size)))
    Syy = convolve(Iy2, np.ones((window_size, window_size)))
    Sxy = convolve(Ixy, np.ones((window_size, window_size)))

    # Compute the determinant and trace of the structure tensor at each pixel
    det = Sxx * Syy - Sxy**2
    trace = Sxx + Syy

    # Compute Harris response
    harris_response = det - k * (trace**2)

    # Apply thresholding to the response image
    corners = np.zeros_like(harris_response)
    corners[harris_response > threshold * harris_response.max()] = 1

    # Find corner coordinates
    corners = np.argwhere(corners)

    image_copy = image.copy()

    # add corners to the image and return it
    for corner in corners:
        image_copy[corner[0], corner[1]] = [255, 0, 0]

    exec_time = time() - start_time

    return Image(image_copy), exec_time


def applyLambdaMinus(image, threshold) -> Image:
    start_time = time()
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = np.copy(image)

    Ix = convolve(gray, np.array([[-1, 0, 1]]))
    Iy = convolve(gray, np.array([[-1], [0], [1]]))

    Ix2 = Ix**2
    Iy2 = Iy**2
    Ixy = Ix * Iy

    # Compute eigenvalues and eigenvectors
    cov_matrix = np.stack((Ix2, Ixy, Ixy, Iy2), axis=-1).reshape((-1, 2, 2))
    eigen_values, _ = np.linalg.eig(cov_matrix)
    eigen_values = eigen_values.reshape(gray.shape[0], gray.shape[1], 2)

    # Compute lambda minus (minimum eigenvalue image)
    λ_minus = np.minimum(eigen_values[:, :, 0], eigen_values[:, :, 1])

    # Thresholding the minimum eigenvalue image
    corners = np.zeros_like(λ_minus)
    corners[λ_minus > threshold * λ_minus.max()] = 1

    corners = np.argwhere(corners)
    image_copy = image.copy()
    for corner in corners:
        cv2.circle(image_copy, (corner[1], corner[0]), 5, (255, 0, 0), 1)

    exec_time = time() - start_time

    return Image(image_copy), exec_time


# Testing
if __name__ == "__main__":
    # image = cv2.imread("images/tri.png")
    # applyHarris(image, 0.05, 0.04)
    ...
