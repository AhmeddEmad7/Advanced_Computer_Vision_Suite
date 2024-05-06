import numpy as np
from models.image import Image

def resize_to_square(image):
    # Get the dimensions of the original image
    height, width = image.shape[:2]

    # Calculate the center of the original image
    center_x, center_y = width // 2, height // 2

    # Determine the size of the square crop
    square_size = min(width, height)

    # Calculate the cropping region
    crop_x1 = center_x - square_size // 2
    crop_y1 = center_y - square_size // 2
    crop_x2 = crop_x1 + square_size
    crop_y2 = crop_y1 + square_size

    # Crop the image to the square shape
    cropped_image = image[crop_y1:crop_y2, crop_x1:crop_x2]

    return cropped_image

def pad_image(image):
    padded_image = np.pad(array=image.image_data, pad_width=((1, 1), (1, 1), (0, 0)))
    return Image(padded_image)