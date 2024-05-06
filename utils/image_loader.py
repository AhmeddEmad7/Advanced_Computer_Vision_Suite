from PyQt6.QtWidgets import QFileDialog
from models.image import Image
import numpy as np
from PIL import Image as PILImage


def open_image(window):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(
        window, "Open Image", "", "Images (*.png *.jpg *.bmp *.gif)"
    )
    return file_path

def save_image(window, export_image: Image):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getSaveFileName(
        window, "Save Image", "", "Images (*.png *.jpg *.bmp *.gif)"
    )
    if file_path:
        # Convert numpy array to PIL Image
        # Bug with exporting noised images, but works with Gray Scale. Check dimensions
        image_pil = PILImage.fromarray(np.transpose(export_image.image_data))
        # Save the image
        image_pil.save(file_path)
        print("Image saved successfully.")

def save_matches_image(window, export_image: np.ndarray):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getSaveFileName(
        window, "Save Image", "", "Images (*.png *.jpg *.bmp *.gif)"
    )
    if file_path:
        # Convert numpy array to PIL Image
        # Bug with exporting noised images, but works with Gray Scale. Check dimensions
        image_pil = PILImage.fromarray(export_image)
        # Save the image
        image_pil.save(file_path)
        print("Image saved successfully.")

def save_array_image(window, export_image: np.ndarray):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getSaveFileName(
        window, "Save Image", "", "Images (*.png *.jpg *.bmp *.gif)"
    )
    if file_path:
        # Convert numpy array to PIL Image
        # Bug with exporting noised images, but works with Gray Scale. Check dimensions
        image_pil = PILImage.fromarray(export_image)
        # Save the image
        image_pil.save(file_path)
        print("Image saved successfully.")
