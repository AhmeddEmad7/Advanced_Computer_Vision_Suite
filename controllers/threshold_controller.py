import cv2
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QSlider,
    QComboBox,
    QRadioButton,
    QLabel,
)
from models.image import Image, load_image_from_file_name
from utils.image_loader import open_image, save_array_image
from models.thresholding import (
    apply_optimal_threshold,
    apply_otsu_threshold,
    apply_multi_class_threshold,
    local_multi_class_thresholding,
)


class ThresholdController:
    def __init__(
        self,
        window: QWidget,
        image_load_btn: QPushButton,
        image_export_btn: QPushButton,
        apply_btn: QPushButton,
        loaded_image_panel: QWidget,
        result_image_panel: QWidget,
        mode_comboBox: QComboBox,
        global_radio_btn: QRadioButton,
        local_radio_btn: QRadioButton,
        box_size_slider: QSlider,
        class_slider: QSlider,
        label: QLabel,
        label2: QLabel,
        box_size_label: QLabel,
        num_classes_label: QLabel,
    ):
        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.apply_btn = apply_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel
        self.mode_comboBox = mode_comboBox
        self.global_radio_btn = global_radio_btn
        self.local_radio_btn = local_radio_btn
        self.box_size_slider = box_size_slider
        self.class_slider = class_slider
        self.label = label
        self.label2 = label2
        self.box_size_label = box_size_label
        self.num_classes_label = num_classes_label

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

        self.box_size_slider.hide()
        self.box_size_label.hide()
        self.label.hide()
        self.label2.hide()
        self.class_slider.hide()
        self.num_classes_label.hide()

    def _initialize_signals_slots(self) -> None:
        self.image_load_btn.clicked.connect(self._load_image)
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.apply_btn.clicked.connect(self._apply_threshold)
        self.local_radio_btn.toggled.connect(self._toggle_box_size_slider)
        self.global_radio_btn.toggled.connect(self._toggle_box_size_slider)
        self.mode_comboBox.currentIndexChanged.connect(self._toggle_box_size_slider)
        self.box_size_slider.valueChanged.connect(self._update_box_size_label)
        self.class_slider.valueChanged.connect(self._update_num_classes_label)

    def _update_box_size_label(self) -> None:
        self.box_size_label.setText(f"{self.box_size_slider.value()}%")

    def _update_num_classes_label(self) -> None:
        self.num_classes_label.setText(f"{self.class_slider.value()}")

    def _toggle_box_size_slider(self) -> None:
        is_global = self.global_radio_btn.isChecked()
        mode = self.mode_comboBox.currentText()
        self.label.setText("Box Size")
        self.local_radio_btn.show()
        self.global_radio_btn.show()
        self.box_size_slider.show()
        self.box_size_label.hide()
        if mode != "Multi Level":
            self.label2.hide()
            self.class_slider.hide()
            self.num_classes_label.hide()

            if is_global:
                self.box_size_slider.hide()
                self.box_size_label.hide()
                self.label.hide()
            else:
                self.box_size_slider.show()
                self.box_size_label.show()
                self.label.show()
        else:
            if is_global:
                self.box_size_slider.hide()
                self.box_size_label.hide()
                self.label.hide()
            else:
                self.box_size_slider.show()
                self.box_size_label.show()
                self.label.show()

            self.label2.show()
            self.class_slider.show()
            self.num_classes_label.show()

    def _apply_threshold(self) -> None:
        if self.current_image is None:
            return

        # Get mode, isGlobal, and box size
        mode = self.mode_comboBox.currentText()
        is_global = self.global_radio_btn.isChecked()
        box_size = int(
            self.box_size_slider.value() / 100 * self.current_image.image_data.shape[0]
        )
        class_size = self.class_slider.value()
        print(box_size)
        print("class_size", class_size)
        thresholded_image: Image = None

        if mode == "Optimal":
            thresholded_image = Image(
                apply_optimal_threshold(
                    self.current_image.image_data, is_global, box_size
                )
            )
        elif mode == "Otsu":
            thresholded_image = Image(
                apply_otsu_threshold(self.current_image.image_data, is_global, box_size)
            )
        else:
            if is_global:
                thresholded_image = Image(
                    apply_multi_class_threshold(
                        self.current_image.image_data, class_size
                    )
                )
            else:
                thresholded_image = Image(
                    local_multi_class_thresholding(
                        self.current_image.image_data, box_size, class_size
                    )
                )
        self._render_result_with_image(thresholded_image)

    def _render_result_with_image(self, current_result: Image) -> None:
        self.current_result = current_result
        if self.current_result_image_item is not None:
            self.current_result_image_item.clear()
        self.current_result_image_item = pg.ImageItem(self.current_result.image_data)
        self.result_image_panel.addItem(self.current_result_image_item)

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
        img_to_export = cv2.transpose(self.current_result.image_data)
        save_array_image(self.window, img_to_export)
