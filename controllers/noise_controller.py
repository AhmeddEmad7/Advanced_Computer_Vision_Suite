from enum import Enum
import pyqtgraph as pg
from models.image import Image, load_image_from_file_name
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QSlider

from models.noise import Noise
from utils.image_loader import open_image, save_image


class NoiseType(Enum):
    UNIFORM = 0
    GAUSSIAN = 1
    SALT_AND_PEPPER = 2


class NoiseController:
    def __init__(
        self,
        window: QWidget,
        image_load_btn: QPushButton,
        image_export_btn: QPushButton,
        loaded_image_panel: QWidget,
        result_image_panel: QWidget,
        noise_type_combo: QWidget,
        param1_label: QLabel,
        param2_label: QLabel,
        param1_value_label: QLabel,
        param2_value_label: QLabel,
        param1_slider: QSlider,
        param2_slider: QSlider,
        apply_noise_btn: QPushButton,
    ) -> None:
        # Connect to Window Elements
        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel
        self.noise_type_combo = noise_type_combo
        self.param1_label = param1_label
        self.param2_label = param2_label
        self.param1_value_label = param1_value_label
        self.param2_value_label = param2_value_label
        self.param1_slider = param1_slider
        self.param2_slider = param2_slider
        self.apply_noise_btn = apply_noise_btn

        # Initialize app controller state
        self.current_image: Image = None
        self.current_result: Image = None
        self.current_loaded_image_item: pg.ImageItem = None
        self.current_result_image_item: pg.ImageItem = None

        # Configure UI
        self._initialize_signals_slots()
        self._set_noise_type(0)
        self.loaded_image_panel.showAxes(False)
        self.loaded_image_panel.invertY(True)
        self.result_image_panel.showAxes(False)
        self.result_image_panel.invertY(True)

    def _initialize_signals_slots(self) -> None:
        self.image_load_btn.clicked.connect(self._load_image)
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.noise_type_combo.currentIndexChanged.connect(self._set_noise_type)
        self.apply_noise_btn.clicked.connect(self._apply_noise)

        self.param1_slider.valueChanged.connect(self._update_param1_value)
        self.param2_slider.valueChanged.connect(self._update_param2_value)

    def _update_param1_value(self, value: int) -> None:
        self.param1_value_label.setText(str(value))

    def _update_param2_value(self, value: int) -> None:
        self.param2_value_label.setText(str(value))

    def _apply_noise(self) -> None:
        if self.current_image is None:
            return

        noise_type_index = self.noise_type_combo.currentIndex()
        if noise_type_index == NoiseType.UNIFORM.value:
            noise_strength = self.param1_slider.value()
            noisy_image: Image = Noise.apply_uniform_noise(
                self.current_image, noise_strength
            )
        elif noise_type_index == NoiseType.GAUSSIAN.value:
            mean = self.param1_slider.value()
            std_dev = self.param2_slider.value()
            noisy_image: Image = Noise.apply_gaussian_noise(
                self.current_image, mean, std_dev
            )
        else:
            salt_to_pepper_ratio = self.param1_slider.value()
            noisy_image: Image = Noise.apply_salt_and_papper_noise(
                self.current_image,
                salt_to_pepper_ratio / 100,
                salt_to_pepper_ratio / 100,
            )

        self._render_result_with_image(noisy_image)

    def _render_result_with_image(self, result_image: Image) -> None:
        self.current_result = result_image
        if self.current_result_image_item is not None:
            self.current_result_image_item.clear()
        self.current_result_image_item = pg.ImageItem(self.current_result.image_data)
        self.result_image_panel.addItem(self.current_result_image_item)

    def _set_noise_type(self, current_noise_type_index: int) -> None:
        # Default to uniform noise
        self.param1_slider.setValue(0)
        self.param2_slider.setValue(0)
        self.param2_label.show()
        self.param2_slider.show()
        self.param2_value_label.show()

        if current_noise_type_index == NoiseType.GAUSSIAN.value:
            self.param1_label.setText("Mean")
            self.param2_label.setText("Standard Deviation")
        elif current_noise_type_index == NoiseType.SALT_AND_PEPPER.value:
            self.param1_label.setText("Salt to Pepper Ratio (%)")
            self.param2_label.hide()
            self.param2_slider.hide()
            self.param2_value_label.hide()
        else:
            self.param1_label.setText("Strength")
            self.param2_label.hide()
            self.param2_slider.hide()
            self.param2_value_label.hide()

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
