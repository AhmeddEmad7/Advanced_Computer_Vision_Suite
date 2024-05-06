import cv2
import numpy as np
from models.image import Image
from scipy.ndimage import convolve


class ActiveContourGreedy:
    def __init__(self, alpha=0.01, beta=0.01, max_num_iter=100):
        self.alpha = alpha
        self.beta = beta
        self.num_iters = max_num_iter

    
    def run(self, image: Image, initial_contour: np.ndarray) -> np.ndarray:

        canny_edges = cv2.Canny(image.image_data, 100, 150)
        final_snake = optimize_contour(initial_contour.copy(), canny_edges, self.alpha, self.beta, self.num_iters)

        return final_snake

    def compute_chain_code(self, final_contour) -> list:
        chain_code = []
        for i in range(len(final_contour) - 1):
            dx = final_contour[i + 1][0] - final_contour[i][0]
            dy = final_contour[i + 1][1] - final_contour[i][1]
            if dx > 0:
                if dy > 0:
                    chain_code.append(1)  # Northeast
                elif dy == 0:
                    chain_code.append(0)  # East
                else:
                    chain_code.append(7)  # Southeast
            elif dx == 0:
                if dy > 0:
                    chain_code.append(2)  # North
                elif dy == 0:
                    # No movement
                    pass
                else:
                    chain_code.append(6)  # South
            else:  # dx < 0
                if dy > 0:
                    chain_code.append(3)  # Northwest
                elif dy == 0:
                    chain_code.append(4)  # West
                else:
                    chain_code.append(5)  # Southwest

        return chain_code

    def compute_area_perimeter(self, chain_code: list) -> float:
        area = 0
        perimeter = len(chain_code) + 1

        # Shoelace formula
        for i in range(len(chain_code) - 1):
            area += (chain_code[i] + chain_code[i + 1]) / 2
        area += (chain_code[-1] + chain_code[0]) / 2
        area /= 2

        return area, perimeter
    
        
def calculate_gradient_magnitude(image: np.ndarray) -> np.ndarray:
        sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

        gradient_x = convolve(image, sobel_x)
        gradient_y = convolve(image, sobel_y)

        gradient_magnitude = - np.sqrt(gradient_x**2 + gradient_y**2)

        return gradient_magnitude


def internal_energy(contour, i, alpha, beta, image_shape):
    # Calculate internal energy based on the curvature of the contour
    x, y = contour[i]
    x_prev, y_prev = contour[i - 1]
    x_next, y_next = contour[(i + 1) % len(contour)]

    angle_prev = np.arctan2(y - y_prev, x - x_prev)
    angle_next = np.arctan2(y_next - y, x_next - x)

    curvature = angle_next - angle_prev

    # Internal energy is a combination of curvature and distance between consecutive points
    dist_prev = np.sqrt((x - x_prev) ** 2 + (y - y_prev) ** 2)
    dist_next = np.sqrt((x_next - x) ** 2 + (y_next - y) ** 2)

    internal_energy = alpha * (curvature ** 2) + beta * ((dist_prev + dist_next) / 2) ** 2

    return internal_energy


def move_contour_point(initial_contour, i, x, y, energy_total, external_energy, image_shape, alpha, beta, encouragement_factor):
    min_energy = energy_total
    new_x, new_y = x, y
    # Iterate over neighboring positions
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            # Skip the current position
            if dx == 0 and dy == 0:
                continue
            # Calculate energy change for moving to the neighboring position
            new_x_temp, new_y_temp = max(0, min(x + dx, image_shape[1] - 1)), max(0, min(y + dy, image_shape[0] - 1))
            energy_temp = internal_energy(initial_contour, i, alpha, beta, image_shape) + external_energy[new_x_temp, new_y_temp]

            # Add term to encourage moving away from the edges of the image
            distance_to_edge = min(new_x_temp, image_shape[0] - new_x_temp, new_y_temp, image_shape[1] - new_y_temp)
            energy_temp -= encouragement_factor * ((alpha * distance_to_edge) + (beta * distance_to_edge))

            # Update if energy reduced
            if energy_temp < min_energy:
                min_energy = energy_temp
                new_x, new_y = new_x_temp, new_y_temp
    
    return new_x, new_y


def optimize_contour(initial_contour: np.ndarray, image: np.ndarray, alpha, beta, max_iterations) -> np.ndarray:
    external_energy = calculate_gradient_magnitude(image)
    converged = False
    iteration = 0
    while not converged and iteration < max_iterations:
        converged = True
        for i, (x, y) in enumerate(initial_contour):
            energy_total = internal_energy(initial_contour, i, alpha, beta, image.shape) + external_energy[x, y]
            new_x, new_y = move_contour_point(initial_contour, i, x, y, energy_total, external_energy, image.shape, alpha, beta, encouragement_factor=1)
            
            if new_x != x or new_y != y:
                converged = False
                initial_contour[i] = (new_x, new_y)

        iteration += 1

    return initial_contour