from enum import Enum
import cv2
from PyQt6.QtWidgets import QWidget, QPushButton, QSlider, QLabel, QComboBox
import pyqtgraph as pg
from models.image import Image, load_image_from_file_name_no_transpose
from models.segmentation import Segmentation
from models.segmentation import apply_agglomerative, apply_region_growing
from utils.image_loader import open_image, save_array_image

class SegmentationType(Enum):
    K_MEANS = 0
    MEAN_SHIFT = 1
    AGGLOMERATIVE = 2
    REGION_GROWING = 3

class SegementationController:
    def __init__(
        self,
        window: QWidget,
        image_load_btn: QPushButton,
        image_export_btn: QPushButton,
        apply_btn: QPushButton,
        loaded_image_panel: QWidget,
        result_image_panel: QWidget,
        method_comboBox: QComboBox,
        param1_slider: QSlider,
        param2_slider: QSlider,
        param1_slider_value: QLabel,
        param2_slider_value: QLabel,
        param1_name: QLabel,
        param2_name: QLabel,
        )  -> None:

        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.apply_btn = apply_btn
        self.loaded_image_panel = loaded_image_panel
        self.segmented_image_panel = result_image_panel
        self.segmentation_type_comboBox = method_comboBox
        self.param1_slider = param1_slider
        self.param2_slider = param2_slider
        self.param1_slider_value = param1_slider_value
        self.param2_slider_value = param2_slider_value
        self.param1_name = param1_name
        self.param2_name = param2_name
        self.seed_point = None

        # Initialize app controller state
        self.loaded_image: Image = None
        self.segmented_image: Image = None
        self.loaded_image_panel.mousePressEvent = self._mouse_click_event

        # Configure UI
        self._initialize_signals_slots()
        self.loaded_image_panel.showAxes(False)
        self.loaded_image_panel.invertY(True)

        self.segmented_image_panel.showAxes(False)
        self.segmented_image_panel.invertY(True)

    def _initialize_signals_slots(self):
        self.image_load_btn.clicked.connect(self._load_image)
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.segmentation_type_comboBox.currentIndexChanged.connect(self._change_segmentation_mode)
        self.param1_slider.valueChanged.connect(self._update_param1_slider_value)
        self.param2_slider.valueChanged.connect(self._update_param2_slider_value)
        self.apply_btn.clicked.connect(self._apply_segmentation)

    def _mouse_click_event(self, event):
        if self.segmentation_type_comboBox.currentIndex() == SegmentationType.REGION_GROWING.value:
            x = event.pos().x()
            y = event.pos().y()
            self.seed_point = (x, y)
            print(self.seed_point)

    def _load_image(self) -> None:
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name_no_transpose(image_path)
            self.loaded_image = loaded_image_data

            self.loaded_image_panel.clear()
            self.segmented_image_panel.clear()

            self.loaded_image_panel.addItem(pg.ImageItem(cv2.transpose(self.loaded_image.image_data)))

    def _export_result_image(self) -> None:
        if self.segmented_image is None:
            return
        save_array_image(self.window, self.segmented_image.image_data)

    def _change_segmentation_mode(self) -> None:
        self.loaded_image_panel.clear()
        self.segmented_image_panel.clear()
        if self.segmentation_type_comboBox.currentIndex() == SegmentationType.K_MEANS.value:
            self.param1_slider.show()
            self.param1_slider.setRange(1, 50)
            self.param1_slider.setValue(3)
            self.param2_slider.show()
            self.param1_slider_value.show()
            self.param1_slider_value.setText(str(3))
            self.param2_slider_value.show()
            self.param1_name.show()
            self.param1_name.setText("Number of Clusters")
            self.param2_name.show()
        elif(self.segmentation_type_comboBox.currentIndex() == SegmentationType.MEAN_SHIFT.value):
            self.param1_slider.show()
            self.param1_slider.setRange(5, 400)
            self.param1_slider.setValue(60)
            self.param2_slider.hide()
            self.param1_slider_value.show()
            self.param1_slider_value.setText(str(60))
            self.param2_slider_value.hide()
            self.param1_name.show()
            self.param1_name.setText("Bandwidth")
            self.param2_name.hide()
        elif(self.segmentation_type_comboBox.currentIndex() == SegmentationType.AGGLOMERATIVE.value):
            self.param2_slider.hide()
            self.param2_slider_value.hide()
            self.param2_name.hide()
            self.param1_name.setText("Number of Clusters")
        elif(self.segmentation_type_comboBox.currentIndex() == SegmentationType.REGION_GROWING.value):
            self.param1_slider.show()
            self.param2_slider.hide()
            self.param1_slider_value.show()
            self.param2_slider_value.hide()
            self.param1_name.show()
            self.param1_name.setText("Threshold")
            self.param2_name.hide()

    def _update_param1_slider_value(self, value) -> None:
        self.param1_slider_value.setText(str(value))

    def _update_param2_slider_value(self, value) -> None:
        self.param2_slider_value.setText(str(value))

    def _apply_segmentation(self):
        self.segmented_image_panel.clear()
        
        if self.segmentation_type_comboBox.currentIndex() == SegmentationType.K_MEANS.value:
            segmented_img = Segmentation._apply_kmeans(self.loaded_image.image_data, self.param1_slider.value(), self.param2_slider.value())

        elif(self.segmentation_type_comboBox.currentIndex() == SegmentationType.MEAN_SHIFT.value):
            segmented_img = Segmentation._apply_mean_shift(self.loaded_image.image_data, self.param1_slider.value())

        elif(self.segmentation_type_comboBox.currentIndex() == SegmentationType.AGGLOMERATIVE.value):
            segmented_img = apply_agglomerative(self.loaded_image.image_data, self.param1_slider.value(), initial_clusters=20)
            
        elif(self.segmentation_type_comboBox.currentIndex() == SegmentationType.REGION_GROWING.value):
            segmented_img = apply_region_growing(self.loaded_image.image_data, self.seed_point, self.param1_slider.value())

        self.segmented_image = Image(segmented_img)
        self.segmented_image_panel.addItem(pg.ImageItem(cv2.transpose(self.segmented_image.image_data)))