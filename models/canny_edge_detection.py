import cv2
import numpy as np
from models.image import Image

class CannyEdgeDetector:
    def __init__(self, sigma=1, low_threshold_ratio=0.09, high_threshold_ratio=0.2):
        self.sigma = sigma
        self.low_threshold_ratio = low_threshold_ratio
        self.high_threshold_ratio = high_threshold_ratio

    def apply_gaussian_filter(self, image: Image):
        kernel_size = 3*3
        sigma = self.sigma
        kernel = np.fromfunction(
            lambda x, y: (1/ (2 * np.pi * sigma**2)) * 
                         np.exp(-((x - (kernel_size-1)/2)**2 + (y - (kernel_size-1)/2)**2) / (2 * sigma**2)),
            (kernel_size, kernel_size)
        )

        kernel = kernel / np.sum(kernel)
        filtered_image = cv2.filter2D(image.image_data, -1, kernel)

        return Image(filtered_image)

    def apply_sobel(self, image: Image):
        grayscale_image = cv2.cvtColor(image.image_data, cv2.COLOR_BGR2GRAY)

        sobel_x = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]))
        sobel_y = cv2.filter2D(grayscale_image, cv2.CV_64F, np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]))

        gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        gradient_direction = np.arctan2(sobel_y, sobel_x) * (180 / np.pi)  # Convert radians to degrees

        return gradient_magnitude, gradient_direction

    def non_max_suppression(self, magnitude, direction):
        rows, cols = magnitude.shape
        suppressed = np.zeros_like(magnitude)

        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                # Compute the direction perpendicular to the gradient direction
                perp_dir = direction[i, j] + 90 if direction[i, j] < 0 else direction[i, j] - 90

                # Determine the neighboring pixels in the gradient direction
                if (0 <= perp_dir < 45) or (135 <= perp_dir < 180) or (-45 <= perp_dir < 0) or (-180 <= perp_dir < -135):
                    neighbors = [magnitude[i-1, j], magnitude[i+1, j]]
                elif (45 <= perp_dir < 90) or (180 <= perp_dir < 225) or (-135 <= perp_dir < -90):
                    neighbors = [magnitude[i-1, j-1], magnitude[i+1, j+1]]
                elif (90 <= perp_dir < 135) or (-90 <= perp_dir < -45):
                    neighbors = [magnitude[i, j-1], magnitude[i, j+1]]

                # Perform non-maximum suppression
                if magnitude[i, j] >= max(neighbors):
                    suppressed[i, j] = magnitude[i, j]
                else:
                    suppressed[i, j] = 0

        return suppressed

    def apply_thresholds(self, gradient_magnitude):
        high_threshold = np.max(gradient_magnitude) * self.high_threshold_ratio
        low_threshold = high_threshold * self.low_threshold_ratio

        strong_edges = gradient_magnitude >= high_threshold
        weak_edges = (gradient_magnitude < high_threshold) & (gradient_magnitude >= low_threshold)

        strong_edges_binary = strong_edges.astype(np.uint8) * 255
        weak_edges_binary = weak_edges.astype(np.uint8) * 255

        return strong_edges_binary, weak_edges_binary

    def apply_hysteresis(self, strong_edges, weak_edges):
        h, w = strong_edges.shape
        visited = np.zeros((h, w), dtype=bool)

        def dfs(i, j):
            visited[i, j] = True
            for ni in range(max(0, i - 1), min(h, i + 2)):
                for nj in range(max(0, j - 1), min(w, j + 2)):
                    if not visited[ni, nj] and weak_edges[ni, nj]:
                        strong_edges[ni, nj] = True
                        dfs(ni, nj)

        for i in range(h):
            for j in range(w):
                if weak_edges[i, j]:
                    dfs(i, j)

        return Image(strong_edges)

def apply_canny_edge_detection(image: Image,sigma=1,low_threshold=1,high_threshold=3):
    canny =CannyEdgeDetector(sigma,(low_threshold/10),(high_threshold/10))
    image_smoothed = canny.apply_gaussian_filter(image)
    Mag, dir = canny.apply_sobel(image_smoothed)
    supp = canny.non_max_suppression(Mag, dir)
    strong, weak = canny.apply_thresholds(supp)
    fin = canny.apply_hysteresis(strong, weak)
    return fin
