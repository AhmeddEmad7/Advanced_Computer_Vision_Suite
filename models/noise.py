from models.image import Image
import numpy as np
import cv2


class Noise:
    @staticmethod
    def apply_salt_and_papper_noise(
        image: Image, salt_prob=0.02, pepper_prob=0.02
    ) -> Image:
        gray_scaled = cv2.cvtColor(image.image_data, cv2.COLOR_RGB2GRAY)
        noisy_image = np.copy(gray_scaled)

        salt_mask = np.random.rand(*gray_scaled.shape[:2]) < salt_prob
        noisy_image[salt_mask] = 255

        pepper_mask = np.random.rand(*gray_scaled.shape[:2]) < pepper_prob
        noisy_image[pepper_mask] = 0

        return Image(noisy_image)

    @staticmethod
    def apply_uniform_noise(image: Image, noise_strength=30) -> Image:
        gray_scaled = cv2.cvtColor(image.image_data, cv2.COLOR_RGB2GRAY)
        noise = np.zeros_like(gray_scaled, dtype=np.uint8)
        cv2.randn(noise, 0, noise_strength)

        noisy_image = cv2.add(gray_scaled, noise)
        return Image(noisy_image)

    @staticmethod
    def apply_gaussian_noise(image: Image, mean=0, std_dev=25):
        gray_scaled = cv2.cvtColor(image.image_data, cv2.COLOR_RGB2GRAY)
        h, w = gray_scaled.shape
        noise = np.random.normal(mean, std_dev, (h, w))
        noisy_image = gray_scaled + noise.astype(np.uint8)
        return Image(noisy_image)
