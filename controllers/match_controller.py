import cv2
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QSlider,QLCDNumber, QComboBox
import time

from models.image import Image, load_image_from_file_name
from models.match import draw_matching
from utils.image_loader import open_image, save_matches_image

class MatchController:
    def __init__(
        self,
        window: QWidget,
        image_1_load_btn: QPushButton,
        image_2_load_btn: QPushButton,
        image_export_btn: QPushButton,
        apply_btn: QPushButton,
        loaded_image_1_panel: QWidget,
        loaded_image_2_panel: QWidget,
        result_image_panel: QWidget,
        threshold1_slider: QSlider,
        threshold2_slider: QSlider,
        method_comboBox: QComboBox,
        match_lcdNumber: QLCDNumber,
        threshold1_label: QLabel,
        threshold2_label: QLabel,
        lower_bound_label: QLabel,
        upper_bound_label: QLabel,
        ):

        self.window = window
        self.image_1_load_btn = image_1_load_btn
        self.image_2_load_btn = image_2_load_btn
        self.image_export_btn = image_export_btn
        self.apply_btn = apply_btn
        self.loaded_image_1_panel = loaded_image_1_panel
        self.loaded_image_2_panel = loaded_image_2_panel
        self.result_image_panel = result_image_panel
        self.threshold1_slider = threshold1_slider
        self.threshold2_slider = threshold2_slider
        self.method_comboBox = method_comboBox
        self.match_lcdNumber = match_lcdNumber
        self.threshold1_label = threshold1_label
        self.threshold2_label = threshold2_label
        self.lower_bound_label = lower_bound_label
        self.upper_bound_label = upper_bound_label

        # Initialize app controller state
        self.loaded_image_1: Image = None
        self.loaded_image_2: Image = None

        # Configure UI
        self._initialize_signals_slots()
        self.loaded_image_1_panel.showAxes(False)
        self.loaded_image_1_panel.invertY(True)

        self.loaded_image_2_panel.showAxes(False)
        self.loaded_image_2_panel.invertY(True)

        self.result_image_panel.showAxes(False)
        self.result_image_panel.invertY(True)

    def _initialize_signals_slots(self):
        self.image_1_load_btn.clicked.connect(lambda: self._load_image("Image 1", "Image1Item"))
        self.image_2_load_btn.clicked.connect(lambda: self._load_image("Image 2", "Image2Item"))
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.apply_btn.clicked.connect(self._apply_matching)
        self.method_comboBox.currentIndexChanged.connect(self._enable_disable_thresholds)
        self.threshold1_slider.valueChanged.connect(self._update_threshold1_value)
        self.threshold2_slider.valueChanged.connect(self._update_threshold2_value)

    def _load_image(self, image, image_item) -> None:
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)

            if(image == "Image 1" and image_item == "Image1Item"):
                self.loaded_image_1 = loaded_image_data
                self.loaded_image_1_panel.clear()
                self.result_image_panel.clear()

                self.loaded_image_1_panel.addItem(pg.ImageItem(self.loaded_image_1.image_data))

            else:
                self.loaded_image_2 = loaded_image_data
                self.loaded_image_2_panel.clear()
                self.result_image_panel.clear()

                self.loaded_image_2_panel.addItem(pg.ImageItem(self.loaded_image_2.image_data))

    def _export_result_image(self) -> None:
        if self.result_image is None:
            return
        save_matches_image(self.window, self.result_image)

    def _enable_disable_thresholds(self) -> None:
        if self.method_comboBox.currentText() == "SSD":
            self.threshold1_slider.show()
            self.threshold2_slider.show()
            self.threshold1_label.show()
            self.threshold2_label.show()
            self.lower_bound_label.show()
            self.upper_bound_label.show()
        else:
            self.threshold1_slider.hide()
            self.threshold2_slider.hide()
            self.threshold1_label.hide()
            self.threshold2_label.hide()
            self.lower_bound_label.hide()
            self.upper_bound_label.hide()

    def _update_threshold1_value(self, value) -> None:
        self.threshold1_label.setText(str(value))

    def _update_threshold2_value(self, value) -> None:
        self.threshold2_label.setText(str(value))

    def _apply_matching(self):
        self.result_image_panel.clear()
        method = self.method_comboBox.currentText()
        lower_bound = self.threshold1_slider.value()
        upper_bound = self.threshold2_slider.value()

        start_time = time.time()
        result = draw_matching(cv2.transpose(self.loaded_image_1.image_data), cv2.transpose(self.loaded_image_2.image_data),
                       method, lower_bound, upper_bound)
        end_time = time.time()

        computation_time = end_time - start_time
        self.result_image = result # For exporting later
        self.match_lcdNumber.display(computation_time)
        self.result_image_panel.addItem(pg.ImageItem(cv2.transpose(result))) # Transposing for visualization purpose