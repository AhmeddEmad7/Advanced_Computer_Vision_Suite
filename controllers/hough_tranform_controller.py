from PyQt6.QtWidgets import QWidget, QPushButton, QSlider, QLabel
import pyqtgraph as pg
from enum import Enum

from models.image import Image, load_image_from_file_name
from utils.image_loader import open_image, save_image
from models import hough_tranform


class HoughTransform(Enum):
    Line = 0
    Circle = 1
    Ellipse = 2

class HoughTransformController:
    def __init__(self, window: QWidget, image_load_btn: QPushButton, image_export_btn: QPushButton,
                loaded_image_panel: QWidget, result_image_panel: QWidget, hough_type_combo: QWidget,
                hough_apply_btn: QPushButton, threshold_slider: QSlider, threshold_value_txtbox: QLabel, threshold_value=130) -> None:
        
        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel
        self.hough_type_combo = hough_type_combo
        self.apply_hough_transform_btn = hough_apply_btn
        self.threshold_slider = threshold_slider
        self.threshold_value_txtbox = threshold_value_txtbox
        self.threshold_value = threshold_value

        # Initialize app controller state
        self.current_image: Image = None
        self.current_result: Image = None
        self.current_loaded_image_item: pg.ImageItem = None
        self.current_result_image_item: pg.ImageItem = None

        # Configure UI
        self._initialize_signals_slots()
        # self._set_noise_type(0)
        self.loaded_image_panel.showAxes(False)
        self.loaded_image_panel.invertY(True)
        self.result_image_panel.showAxes(False)
        self.result_image_panel.invertY(True)
        self.threshold_value_txtbox.setText(str(self.threshold_value))
        
    def _initialize_signals_slots(self) -> None:
        self.image_load_btn.clicked.connect(self._load_image)
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.apply_hough_transform_btn.clicked.connect(self._apply_hough_transform)
        self.threshold_slider.valueChanged.connect(self._handle_slider_value_changes)
    

    def _handle_slider_value_changes(self, value):
        self.threshold_value = value
        self.threshold_value_txtbox.setText(str(value))

    def _load_image(self) -> None:
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)
            self.current_image = loaded_image_data
            if self.current_loaded_image_item is not None:
                self.current_loaded_image_item.clear()
                self.loaded_image_panel.clear()
                self.result_image_panel.clear()
            self.current_loaded_image_item = pg.ImageItem(self.current_image.image_data)
            self.loaded_image_panel.addItem(self.current_loaded_image_item)


    def _export_result_image(self) -> None:
        # Get the cuurent result image and export it
        if self.current_result is None:
            return
        save_image(self.window, self.current_result)


    def _apply_hough_transform(self):
        self.result_image_panel.clear()
        if self.current_loaded_image_item is None:
            return

        hough_tranform_type = self.hough_type_combo.currentIndex()

        if hough_tranform_type == HoughTransform.Line.value:
            self.current_result = hough_tranform.detect_and_draw(self.current_image, shape='lines', threshold=self.threshold_value)

        elif hough_tranform_type == HoughTransform.Circle.value:
            self.current_result = hough_tranform.detect_and_draw(self.current_image, shape='circles', threshold=self.threshold_value)

        elif hough_tranform_type == HoughTransform.Ellipse.value:
            self.current_result = hough_tranform.detect_and_draw(self.current_image, shape='ellipses', threshold=self.threshold_value)

        self.current_loaded_image_item = pg.ImageItem(self.current_result.image_data)
        self.result_image_panel.addItem(self.current_loaded_image_item)
