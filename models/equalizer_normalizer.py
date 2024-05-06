import numpy as np
import cv2
from models.image import Image

class EqualizerNormalizer:
    def __init__(self, ):
        pass

    # def equalize_image(self, image: Image) -> Image:
    #     ### Image here must be in gray scale
    #     # image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    #     equalized_image = cv2.equalizeHist(image.image_data)

    #     return Image(equalized_image)
    

    def histogram_equalization(self, image_data):
        # Compute the histogram of the input image
        histogram, bins = np.histogram(image_data.flatten(), bins=256, range=[0,256])

        # Compute the cumulative distribution function (CDF)
        cdf = histogram.cumsum()

        # Normalize the CDF
        cdf_normalized = cdf * 255 / cdf[-1]

        # Use the CDF values to map the pixel values in the original image
        equalized_image_data = np.interp(image_data.flatten(), bins[:-1], cdf_normalized).reshape(image_data.shape)

        return equalized_image_data
    


    def equalize_rgb_image(self, image: Image) -> Image:
        equalized_image_data = self.histogram_equalization(image.image_data)

        return Image(equalized_image_data)


    def normalize_image(self, image: Image) -> Image:
        ### Load the image in color (BGR format)
        # image = cv2.imread(image_path)

        image_float = image.image_data.astype(float)

        normalized_image = (image_float - np.min(image_float)) / (np.max(image_float) - np.min(image_float))

        # normalized_image = cv2.normalize(image_float, None, 0.0, 1.0, cv2.NORM_MINMAX)

        return Image(normalized_image)
