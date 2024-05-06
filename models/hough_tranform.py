import numpy as np
import cv2

from models.image import Image

class HoughTransform:
    def __init__(self, img):
        self.img = img

    def detect_lines(self, rho_resolution=1, theta_resolution=np.pi/180, threshold=130):
        height, width = self.img.shape[:2]
        diagonal_length = np.ceil(np.sqrt(height ** 2 + width ** 2))
        rho_max = int(diagonal_length / rho_resolution)
        theta_max = int(np.pi / theta_resolution)
        accumulator = np.zeros((rho_max, theta_max), dtype=np.uint8)

        edge_points = np.argwhere(self.img != 0)

        cos_theta = np.cos(np.arange(0, np.pi, theta_resolution))
        sin_theta = np.sin(np.arange(0, np.pi, theta_resolution))

        for y, x in edge_points:
            rho = np.round(x * cos_theta + y * sin_theta)
            accumulator[rho.astype(int), np.arange(theta_max)] += 1

        lines = []
        rho_indices, theta_indices = np.where(accumulator > threshold)
        for rho_index, theta_index in zip(rho_indices, theta_indices):
            rho = rho_index * rho_resolution
            theta = theta_index * theta_resolution
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            lines.append(((x1, y1), (x2, y2)))
        
        return lines

    def detect_circles(self, radius_resolution=2, threshold=170):
        height, width = self.img.shape[:2]
        max_radius = min(height, width) // 11
        accumulator = np.zeros((height, width, max_radius), dtype=np.uint8)
        edge_points = np.argwhere(self.img != 0)
        angles = np.deg2rad(np.arange(0, 360))

        for radius in range(1, max_radius + 1, radius_resolution):
            for angle_index, angle in enumerate(angles):
                center_x = (edge_points[:, 1] + radius * np.cos(angle)).astype(int)
                center_y = (edge_points[:, 0] + radius * np.sin(angle)).astype(int)
                valid_points = (center_x >= 0) & (center_x < width) & (center_y >= 0) & (center_y < height)
                center_x = center_x[valid_points]
                center_y = center_y[valid_points]
                accumulator[center_y, center_x, radius - 1] += 1

        circles = np.argwhere(accumulator > threshold)
        return circles

    def detect_ellipses(self, threshold=140):
        height, width = self.img.shape[:2]
        max_a = min(height, width) // 12
        max_b = min(height, width) // 12
        accumulator = np.zeros((height, width, max_a, max_b), dtype=np.uint8)
        edge_points = np.argwhere(self.img != 0)
        angles = np.deg2rad(np.arange(0, 360, 360 / 360))

        for a in range(1, max_a + 1, 2):
            for b in range(1, max_b + 1, 2):
                for angle_index, angle in enumerate(angles):
                    center_x = (edge_points[:, 1] + a * np.cos(angle)).astype(int)
                    center_y = (edge_points[:, 0] + b * np.sin(angle)).astype(int)
                    valid_points = (center_x >= 0) & (center_x < width) & (center_y >= 0) & (center_y < height)
                    center_x = center_x[valid_points]
                    center_y = center_y[valid_points]
                    accumulator[center_y, center_x, a - 1, b - 1] += 1

        ellipses = np.argwhere(accumulator > threshold)
        return ellipses

def detect_and_draw(image: Image, shape='lines', threshold=130):
    img = image.image_data
    resized_img = cv2.resize(img, (img.shape[1] * 3 // 4, img.shape[0] * 3 // 4))  # Adjust the resize factor as needed
    edges = cv2.Canny(resized_img, 50, 120, apertureSize=3)

    hough_transform = HoughTransform(edges)

    if shape == 'lines':
        detected_shapes = hough_transform.detect_lines(threshold=threshold)
        output_img = resized_img.copy()
        for line in detected_shapes:
            cv2.line(output_img, line[0], line[1], (0, 0, 255), 2)
        return Image(output_img)

    elif shape == 'circles':
        detected_shapes = hough_transform.detect_circles(threshold=threshold)
        output_img = resized_img.copy()
        for circle in detected_shapes:
            cv2.circle(output_img, (circle[1], circle[0]), circle[2] + 1, (255, 0, 0), 1)
        return Image(output_img)

    elif shape == 'ellipses':
        detected_shapes = hough_transform.detect_ellipses(threshold=threshold)
        output_img = resized_img.copy()
        for ellipse in detected_shapes:
            cv2.ellipse(output_img, (ellipse[1], ellipse[0]), (ellipse[2] + 1, ellipse[3] + 1), 0, 0, 360, (255, 0, 0), 1)
        return Image(output_img)

# Example usage:
# detect_and_draw('images/sudoku.jpeg', shape='lines', threshold=130)
# detect_and_draw('images/sudoku.jpeg', shape='circles', threshold=160)
# detect_and_draw('images/sudoku.jpeg', shape='ellipses', threshold=140)
