from PyQt6.QtWidgets import QWidget, QPushButton
import pyqtgraph as pg
from models.image import Image, load_image_from_file_name
from utils.image_loader import open_image, save_image
from enum import Enum

from models import edge_detectors
from models.image import Image
from models.filters import Filter


class EdgeDetector(Enum):
    Sobel = 0
    Robert = 1
    Prewitt = 2
    Canny = 3

class EdgeDetectionController:
    def __init__(self, window: QWidget, image_load_btn: QPushButton, image_export_btn: QPushButton,
                loaded_image_panel: QWidget, result_image_panel: QWidget, edge_detector_combo: QWidget,
                apply_edge_detection_btn: QPushButton) -> None:
        
        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel
        self.edge_detector_combo = edge_detector_combo
        self.apply_edge_detection_btn = apply_edge_detection_btn


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

    def _initialize_signals_slots(self) -> None:
        self.image_load_btn.clicked.connect(self._load_image)
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.apply_edge_detection_btn.clicked.connect(self._apply_edge_detection)


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


    def _apply_edge_detection(self):

        if self.current_loaded_image_item is None:
            return

        
        edge_detector = self.edge_detector_combo.currentIndex()

        if edge_detector == EdgeDetector.Sobel.value:
            self.current_result = edge_detectors.apply_sobel(self.current_image)

        elif edge_detector == EdgeDetector.Robert.value:
            self.current_result = edge_detectors.apply_roberts(self.current_image)

        elif edge_detector == EdgeDetector.Prewitt.value:
            self.current_result = edge_detectors.apply_prewitt(self.current_image)

        elif edge_detector == EdgeDetector.Canny.value:
            self.current_result = edge_detectors.apply_canny(self.current_image)

        self.current_loaded_image_item = pg.ImageItem(self.current_result.image_data)
        self.result_image_panel.addItem(self.current_loaded_image_item)

