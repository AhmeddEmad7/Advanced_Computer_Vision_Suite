from enum import Enum

import cv2
import numpy as np
import pyqtgraph as pg
from models.image import Image, load_image_from_file_name
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QSlider
from utils.image_loader import open_image, save_image

class ThresholdType(Enum):
    Local_threshold = 0
    Global_threshold = 1


class ThresholdingController:
    def __init__(self,
                 window:QWidget,
                 image_load_btn:QPushButton,
                 image_export_btn:QPushButton,
                 loaded_image_panel:QWidget,
                 result_image_panel:QWidget,
                 thres_combo:QWidget,
                 param1_slider:QSlider,
                 param2_slider:QSlider,
                 param1_label:QLabel,
                 param2_label:QLabel,
                 param3_label:QLabel,
                 param4_label:QLabel,
                 apply_thres_btn: QPushButton,) -> None:
        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel
        self.thres_combo = thres_combo
        self.param1_slider = param1_slider
        self.param2_slider = param2_slider
        self.param1_label = param1_label
        self.param2_label = param2_label
        self.param3_label = param3_label
        self.param4_label = param4_label
        self.apply_thres_btn = apply_thres_btn


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

        self.param1_slider.valueChanged.connect(self._update_param1_value)
        self.param2_slider.valueChanged.connect(self._update_param2_value)


    def _update_param1_value(self, value: int) -> None:
        if value % 2 == 0:
            self.param3_label.setText(str(value + 1))
        else:
            self.param3_label.setText(str(value))


    def _update_param2_value(self, value: int) -> None:
        self.param4_label.setText(str(value))
    def _initialize_signals_slots(self) -> None:
            self.image_load_btn.clicked.connect(self._load_image)
            self.image_export_btn.clicked.connect(self._export_result_image)
            self.thres_combo.currentIndexChanged.connect(self._set_thres_type)
            self.apply_thres_btn.clicked.connect(self._apply_thres)
            self.param1_slider.valueChanged.connect(self.handle_slider_value_changed)

    def _load_image(self) -> None:
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)
            self.current_image = loaded_image_data
            if self.current_loaded_image_item is not None:
                self.current_loaded_image_item.clear()
            self.current_loaded_image_item = pg.ImageItem(self.current_image.image_data)
            self.loaded_image_panel.addItem(self.current_loaded_image_item)

    def _export_result_image(self) -> None:
        # Get the cuurent result image and export it
        if self.current_result is None:
            return
        save_image(self.window, self.current_result)
    def handle_slider_value_changed(self, value):
        # Adjust the value to the nearest odd number
        if value % 2 == 0:
            self.param1_slider.setValue(value + 1)
            self.param3_label.setText(str(value+1))

    def _set_thres_type(self, current_filter_type_index: int) -> None:
        self.param2_label.setText("C value")
        self.param1_label.show()
        self.param3_label.show()
        self.param1_slider.show()
        if current_filter_type_index == ThresholdType.Local_threshold.value:
            self.param1_label.show()
            self.param1_slider.show()
        elif current_filter_type_index == ThresholdType.Global_threshold.value:
            self.param2_label.setText("Threshold value")
            self.param1_label.hide()
            self.param1_slider.hide()
            self.param3_label.hide()

    def local_thresholding(self, image: Image, block_size, c_value):
        # image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
        grayscale_image = np.mean(image.image_data, axis=2)
        grayscale_image = np.uint8(grayscale_image)

        binary_local = cv2.adaptiveThreshold(grayscale_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c_value)

        # Return an instance of the Image class
        return Image(binary_local)

    def global_thresholding(self, image: Image, threshold_value):
        grayscale_image = np.mean(image.image_data, axis=2)

        _, binary_global = cv2.threshold(grayscale_image, threshold_value, 255, cv2.THRESH_BINARY)

        # Return an instance of the Image class
        return Image(binary_global)
    
    def _apply_thres(self) -> None:
        thres_type = self.thres_combo.currentIndex()
        if thres_type == ThresholdType.Local_threshold.value:
            block_size = self.param1_slider.value()
            c_value = self.param2_slider.value()
            self.current_result = self.local_thresholding(self.current_image, block_size, c_value)
        elif thres_type == ThresholdType.Global_threshold.value:
            threshold_value = self.param2_slider.value()
            self.current_result = self.global_thresholding(self.current_image, threshold_value)

        if self.current_result_image_item is not None:
            self.current_result_image_item.clear()
        self.current_result_image_item = pg.ImageItem(self.current_result.image_data)
        self.result_image_panel.addItem(self.current_result_image_item)