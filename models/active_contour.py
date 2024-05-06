# import matplotlib.pyplot as plt
from skimage import io, color, draw
import numpy as np
from models.image import Image
from scipy.interpolate import RectBivariateSpline
from skimage.filters import sobel
from skimage.util import img_as_float


class ActiveContour:
    def __init__(self, alpha=0.01, beta=0.01, w_line=0, w_edge=1, gamma=0.001, max_px_move=0.5,
                  max_num_iter=20000, convergence=0.1, convergence_order = 10):
        
        self.alpha = alpha
        self.beta = beta
        self.w_line = w_line
        self.w_edge = w_edge
        self.gamma = gamma
        self.max_px_move = max_px_move
        self.num_iters = max_num_iter
        self.convergence_threshold = convergence
        self.convergence_order = convergence_order

    def initialize_model(self, image, initial_contour):    
        img = img_as_float(image)
        float_dtype = img.dtype

        edge = find_edges(img, self.w_edge)
        img = superimpose_images(img, edge, self.w_line, self.w_edge)

        intp = interpolate_image(img)

        snake_xy = initial_contour[:, ::-1] # Reverse x and y coordinates of the snake to match the image representation
        snake_x_points = snake_xy[:, 0].astype(float_dtype) # Height
        snake_y_points = snake_xy[:, 1].astype(float_dtype) # Width
        n = len(snake_x_points) # Number of contour points sepcified

        A = build_snake_matrix(n, self.alpha, self.beta)
        inv_A = compute_inverse_matrix(A, self.gamma)

        return snake_x_points, snake_y_points, inv_A, intp
    
    def run(self, image: Image, initial_contour: np.ndarray) -> np.ndarray:
        snake_x_points, snake_y_points, inv_A, intp = self.initialize_model(image.image_data, initial_contour)

        final_snake_x, final_snake_y = run_active_contour(snake_x_points, snake_y_points, inv_A, intp, self.gamma,
                                                    self.max_px_move, self.convergence_order,
                                                      self.convergence_threshold, self.num_iters)

        final_snake = np.stack([final_snake_x, final_snake_y], axis=1)
        return final_snake[:, ::-1] # Reversing x and y coordinates again for plotting

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
    
        
def find_edges(image: np.ndarray, w_edge) -> np.ndarray:
    if w_edge != 0:
        if image.ndim == 3:
            edge = [sobel(image[:, :, 0]), sobel(image[:, :, 1]),
                    sobel(image[:, :, 2])]
        else:
            edge = [sobel(image)]
    else:
        edge = [0]
    return edge

def superimpose_images(image: np.ndarray, edge, w_line, w_edge) -> np.ndarray: # combine the intensity image and the edge image(s)
                                                                               # to create a single image that guides the snake's movement during
                                                                               # the optimization process
    if image.ndim == 3:
        image = w_line * np.sum(image, axis=2) + w_edge * sum(edge)
    else:
        image = w_line * image + w_edge * edge[0]

    return image

def interpolate_image(image: np.ndarray):
    intp = RectBivariateSpline(np.arange(image.shape[1]),
                                np.arange(image.shape[0]),
                                image.T, kx=2, ky=2, s=0) # kx and ky = 2 indicating bi-quadratic interpolation                                                        # s = 0 indicates no smoothing
    return intp

def build_snake_matrix(n, alpha, beta):
    eye_n = np.eye(n, dtype=float)

    a = (np.roll(eye_n, -1, axis=0)
         + np.roll(eye_n, -1, axis=1)
         - 2 * eye_n)  # second order derivative, central difference
    
    b = (np.roll(eye_n, -2, axis=0)
         + np.roll(eye_n, -2, axis=1)
         - 4 * np.roll(eye_n, -1, axis=0)
         - 4 * np.roll(eye_n, -1, axis=1)
         + 6 * eye_n)  # fourth order derivative, central difference
    
    A = -alpha * a + beta * b
    return A # Generated an energy matrix A used in the active contour model to guide the movement of the snake

def compute_inverse_matrix(A, gamma):
    eye_n = np.eye(A.shape[0], dtype=float)
    inv = np.linalg.inv(A + gamma * eye_n)
    return inv

def run_active_contour(snake_x, snake_y, inv, intp, gamma,
                           max_px_move, convergence_order, convergence, max_num_iter):

    xsave = np.empty((convergence_order, len(snake_x)), dtype=float)
    ysave = np.empty((convergence_order, len(snake_y)), dtype=float)
    for i in range(max_num_iter):
        
        fx = intp(snake_x,snake_y, dx=1, grid=False).astype(float, copy=False)
        fy = intp(snake_x, snake_y, dy=1, grid=False).astype(float, copy=False)

        # Movements are capped to max_px_move per iteration:
        dx = max_px_move * np.tanh(inv @ (gamma*snake_x + fx) - snake_x)
        dy = max_px_move * np.tanh(inv @ (gamma*snake_y + fy) - snake_y)
        
        snake_x += dx
        snake_y += dy

        # Convergence criteria needs to compare to a number of previous
        # configurations since oscillations can occur.
        j = i % (convergence_order + 1)
        if j < convergence_order:
            xsave[j, :] = snake_x
            ysave[j, :] = snake_y
        else:
            dist = np.min(np.max(np.abs(xsave - snake_x[None, :])
                                 + np.abs(ysave - snake_y[None, :]), 1))
            if dist < convergence:
                break

    return snake_x, snake_y