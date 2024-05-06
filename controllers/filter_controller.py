
from enum import Enum
import pyqtgraph as pg
from models.image import Image, load_image_from_file_name
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QSlider

from models.filters import Filter ,FrequencyFilter
from utils.image_loader import open_image, save_image
class FilterType(Enum):
    Average = 0
    Median = 1
    GAUSSIAN = 2
    Low_pass = 3
    High_pass = 4

class FilterController:
    def __init__(
            self,
            window: QWidget,
            image_load_btn: QPushButton,
            image_export_btn: QPushButton,
            loaded_image_panel: QWidget,
            result_image_panel: QWidget,
            filter_type_combo: QWidget,
            param1_label: QLabel,
            param2_label: QLabel,
            param3_label: QLabel,
            param4_label: QLabel,
            param1_slider: QSlider,
            param2_slider: QSlider,
            apply_filter_btn: QPushButton,

        ) -> None:
            # Connect to Window Elements
            self.window = window
            self.image_load_btn = image_load_btn
            self.image_export_btn = image_export_btn
            self.loaded_image_panel = loaded_image_panel
            self.result_image_panel = result_image_panel
            self.filter_type_combo = filter_type_combo
            self.param1_label = param1_label
            self.param2_label = param2_label
            self.param3_label = param3_label
            self.param4_label = param4_label
            self.param1_slider = param1_slider
            self.param2_slider = param2_slider
            self.apply_filter_btn = apply_filter_btn

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
            self.param2_label.hide()
            self.param3_label.hide()
            self.param2_slider.hide()
            self.param1_slider.valueChanged.connect(self._update_param1_value)
            self.param2_slider.valueChanged.connect(self._update_param2_value)

    def _update_param1_value(self, value: int) -> None:
        if value % 2 == 0:
            self.param4_label.setText(str(value+1))
        else:
            self.param4_label.setText(str(value))

    def _update_param2_value(self, value: int) -> None:
        self.param3_label.setText(str(value))
    def _initialize_signals_slots(self) -> None:
            self.image_load_btn.clicked.connect(self._load_image)
            self.image_export_btn.clicked.connect(self._export_result_image)
            self.filter_type_combo.currentIndexChanged.connect(self._set_filter_type)
            self.apply_filter_btn.clicked.connect(self._apply_filter)
            self.param1_slider.valueChanged.connect(self.handle_slider_value_changed)
            
    def handle_slider_value_changed(self, value):
        # Adjust the value to the nearest odd number
        if value % 2 == 0:
            self.param1_slider.setValue(value + 1)
        self.param4_label.setText(str(value+ 1))
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

    def _set_filter_type(self, current_filter_type_index: int) -> None:
        self.param1_label.setText("Kernel Size")
        if current_filter_type_index == FilterType.GAUSSIAN.value:
            self.param2_label.show()
            self.param3_label.show()
            self.param2_slider.show()
        elif current_filter_type_index == FilterType.Low_pass.value or current_filter_type_index == FilterType.High_pass.value:
            self.param1_label.setText("Cutoff Frequency")
            self.param2_label.hide()
            self.param2_slider.hide()
            self.param3_label.hide()
        else:
            self.param2_label.hide()
            self.param3_label.hide()
            self.param2_slider.hide()

    def _apply_filter(self) -> None:
        if self.current_image is None:
            return
        filter_type_index = self.filter_type_combo.currentIndex()
        value = self.param1_slider.value()
        filter_instance = Filter(value)

        if filter_type_index == FilterType.Average.value:
            filter_image: Image = filter_instance.apply_average_filter(self.current_image)
        elif filter_type_index == FilterType.Median.value:
            filter_image: Image = filter_instance.apply_median_filter(self.current_image)

        elif filter_type_index == FilterType.GAUSSIAN.value:
            value2 = self.param2_slider.value()
            filter_image: Image = filter_instance.apply_gaussian_filter(self.current_image, value2)
        elif filter_type_index == FilterType.Low_pass.value:
            frequency_filter = FrequencyFilter(value)
            filter_image: Image = frequency_filter.apply_low_pass_filter(self.current_image)
        else:
            frequency_filter = FrequencyFilter(value)
            filter_image: Image = frequency_filter.apply_high_pass_filter(self.current_image)
        self._render_result_with_image(filter_image)

    def _render_result_with_image(self, result_image: Image) -> None:
        self.current_result = result_image
        if self.current_result_image_item is not None:
            self.current_result_image_item.clear()
        self.current_result_image_item = pg.ImageItem(self.current_result.image_data)
        self.result_image_panel.addItem(self.current_result_image_item)

