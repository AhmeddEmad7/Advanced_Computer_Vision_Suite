import cv2
import numpy as np


class Image:
    def __init__(self, image_data: np.ndarray) -> None:
        self.image_data = image_data
        self.height = self.image_data.shape[0]
        self.width = self.image_data.shape[1]
        self.center_x, self.center_y = self.width / 2, self.height / 2

    def is_rgb(self) -> bool:
        return len(self.image_data.shape) == 3 and self.image_data.shape[2] == 3

    def get_hist_data(self) -> np.ndarray:
        hist, _ = np.histogram(self.image_data.flatten(), 256, [0, 256])
        return hist
    
    def get_channel_hist_data(self, channel: int) -> np.ndarray:
        hist = (cv2.calcHist([self.image_data], [channel], None, [256], [0, 256])).flatten()
        return hist
        
    def get_cdf_data(self) -> np.ndarray:
        hist = self.get_hist_data()
        cdf = hist.cumsum()
        cdf_normalized: np.ndarray = cdf / cdf.max()
        return cdf_normalized
    
    def get_channel_cdf_data(self, channel: int) -> np.ndarray:
        hist = self.get_channel_hist_data(channel)
        cdf = hist.cumsum()
        cdf_normalized: np.ndarray = cdf / cdf.max()
        return cdf_normalized
    

def load_image_from_file_name(file_name: str) -> Image:
    image_data = cv2.cvtColor(cv2.imread(file_name), cv2.COLOR_BGR2RGB)
    return Image(cv2.transpose(image_data))

def load_image_from_file_name_no_transpose(file_name: str) -> Image:
    image_data = cv2.cvtColor(cv2.imread(file_name), cv2.COLOR_BGR2RGB)
    return Image(image_data)

def read_gray_image(image_path: str):
    return Image(cv2.imread(image_path, cv2.IMREAD_GRAYSCALE))

def read_rgb_image(image_path: str):
    return Image(cv2.imread(image_path, cv2.IMREAD_COLOR))

# def rgb2gray(image: np.ndarray) -> np.ndarray:
#     grayscale_image = np.dot(image[..., :3], [0.299, 0.587, 0.114])
#     grayscale_image = grayscale_image.astype(np.uint8)

#     return grayscale_image

def rgb2gray(image: Image) -> Image:
    image_np = image.image_data

    grayscale_image = np.dot(image_np[..., :3], [0.299, 0.587, 0.114])
    grayscale_image = grayscale_image.astype(np.uint8)

    return Image(grayscale_image)