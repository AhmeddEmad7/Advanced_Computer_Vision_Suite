import cv2
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QSlider

from models.image import Image, load_image_from_file_name
from models.features_extractor import applyHarris, applyLambdaMinus
from utils.image_loader import open_image, save_matches_image


class FeaturesExtractorController:
    def __init__(
        self,
        window: QWidget,
        image_load_btn: QPushButton,
        image_export_btn: QPushButton,
        loaded_image_panel: QWidget,
        result_image_panel: QWidget,
        param1_label: QLabel,
        param1_slider: QSlider,
        apply_btn: QPushButton,
        apply_lambda_minus_btn: QPushButton,
        clear_btn: QPushButton,
        exec_time_label: QLabel,
    ):
        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel
        self.param1_label = param1_label
        self.param1_slider = param1_slider
        self.apply_btn = apply_btn
        self.apply_lambda_minus_btn = apply_lambda_minus_btn
        self.clear_btn = clear_btn
        self.exec_time_label = exec_time_label

        # Initialize app controller state
        self.current_image: Image = None
        self.current_result: Image = None

        self.current_loaded_image_item: pg.ImageItem = None
        self.current_result_image_item: pg.ImageItem = None

        # Configure UI
        self._initialize_signals_slots()
        self.loaded_image_panel.showAxes(False)
        self.loaded_image_panel.invertY(True)
        self.result_image_panel.showAxes(False)
        self.result_image_panel.invertY(True)

    def _initialize_signals_slots(self):
        self.image_load_btn.clicked.connect(self._load_image)
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.apply_btn.clicked.connect(self._apply_harris)
        self.apply_lambda_minus_btn.clicked.connect(self._apply_lambda_minus)
        self.param1_slider.valueChanged.connect(self._update_param1_label)
        self.clear_btn.clicked.connect(self._clear_result_image)

    def _update_param1_label(self) -> None:
        current_value = self.param1_slider.value() / 100
        self.param1_label.setText(f"{current_value:.3f}")

    def _apply_harris(self) -> None:
        if self.current_image is None:
            return

        # Apply Harris
        delta = self.param1_slider.value() / 100
        harris_applied_img, exec_time = applyHarris(
            self.current_image.image_data, delta
        )
        self.exec_time_label.setText(f"Took: {exec_time:.3f} s")

        self._render_result_with_image(harris_applied_img)

    def _apply_lambda_minus(self) -> None:
        if self.current_image is None:
            return

        # Apply Lambda Minus
        delta = self.param1_slider.value() / 100
        lambda_minus_applied_img, exec_time = applyLambdaMinus(
            self.current_image.image_data, delta
        )
        self.exec_time_label.setText(f"Took: {exec_time:.3f} s")

        self._render_result_with_image(lambda_minus_applied_img)

    def _render_result_with_image(self, result_image: Image) -> None:
        self._clear_result_image()
        self.current_result = result_image
        self.current_result_image_item = pg.ImageItem(result_image.image_data)
        self.result_image_panel.addItem(self.current_result_image_item)

    def _clear_result_image(self) -> None:
        self.result_image_panel.clear()
        if self.current_result_image_item is not None:
            self.current_result_image_item.clear()
        self.current_result = None
        self.current_result_image_item = None

    def _load_image(self) -> None:
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)
            self.current_image = loaded_image_data
            if self.current_loaded_image_item is not None:
                self.current_loaded_image_item.clear()
                self.result_image_panel.clear()
            self.current_loaded_image_item = pg.ImageItem(self.current_image.image_data)
            self.loaded_image_panel.addItem(self.current_loaded_image_item)

    def _export_result_image(self) -> None:
        # Get the cuurent result image and export it
        if self.current_result is None:
            return
        img_to_export = cv2.transpose(self.current_result.image_data)
        save_matches_image(self.window, img_to_export)
