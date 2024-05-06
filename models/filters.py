import numpy as np
import cv2

from models.image import Image
from utils.image_utils import pad_image

class Filter:
    def __init__(self, kernel_size):
        self.kernel_size = kernel_size

    def apply_average_filter(self, image: Image) -> Image:
        kernel = np.ones((self.kernel_size, self.kernel_size), np.float32) / (self.kernel_size**2)
        filtered_image = cv2.filter2D(image.image_data, -1, kernel)
        
        return Image(filtered_image)

    def apply_median_filter(self, image: Image) -> Image:
        padded_image = pad_image(image)

        filtered_image = np.zeros_like(image.image_data)

        n, m, k = padded_image.image_data.shape

        for ch in range(k):
            for i in range(1, n-1):
                for j in range(1, m-1):
                    kernel = padded_image.image_data[i:i+3, j:j+3, ch]
                    _median = np.median(kernel)
                    filtered_image[i-1, j-1, ch] = _median
        filtered_image = cv2.medianBlur(image.image_data, self.kernel_size)

        return Image(filtered_image)
    

    def apply_gaussian_filter(self, image: Image, sigma) -> Image:
        kernel = np.fromfunction(
            lambda x, y: (1/ (2 * np.pi * sigma**2)) * 
                         np.exp(-((x - (self.kernel_size-1)/2)**2 + (y - (self.kernel_size-1)/2)**2) / (2 * sigma**2)),
            (self.kernel_size, self.kernel_size)
        )

        kernel = kernel / np.sum(kernel)
        filtered_image = cv2.filter2D(image.image_data, -1, kernel)

        return Image(filtered_image)

    
class FrequencyFilter:
    def __init__(self, cutoff_frequency):
        self.cutoff_frequency = cutoff_frequency

    def apply_low_pass_filter(self, image: Image) -> Image:
        grayscale_image = np.mean(image.image_data, axis=2)

        f_transform = np.fft.fft2(grayscale_image)
        f_transform_shifted = np.fft.fftshift(f_transform)

        rows, cols = grayscale_image.shape
        crow, ccol = rows // 2, cols // 2

        mask = np.zeros((rows, cols), np.uint8)
        mask[crow - self.cutoff_frequency:crow + self.cutoff_frequency, ccol - self.cutoff_frequency:ccol + self.cutoff_frequency] = 1

        f_transform_shifted = f_transform_shifted * mask

        f_transform_inverse = np.fft.ifftshift(f_transform_shifted)
        image_filtered = np.fft.ifft2(f_transform_inverse)
        image_filtered = np.abs(image_filtered)


        return Image(image_filtered)
    
    def apply_high_pass_filter(self, image: Image) -> Image:
        grayscale_image = np.mean(image.image_data, axis=2)

        f_transform = np.fft.fft2(grayscale_image)
        f_transform_shifted = np.fft.fftshift(f_transform)

        rows, cols = grayscale_image.shape
        crow, ccol = rows // 2, cols // 2

        mask = np.ones((rows, cols), np.uint8)
        mask[crow - self.cutoff_frequency:crow + self.cutoff_frequency, ccol - self.cutoff_frequency:ccol + self.cutoff_frequency] = 0

        f_transform_shifted = f_transform_shifted * mask

        f_transform_inverse = np.fft.ifftshift(f_transform_shifted)
        image_filtered = np.fft.ifft2(f_transform_inverse)
        image_filtered = np.abs(image_filtered)

        return Image(image_filtered)