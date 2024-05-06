import cv2
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QPushButton, QLCDNumber
import time
from models.image import Image, load_image_from_file_name
from models.sift import computeKeypointsAndDescriptors
from utils.image_loader import open_image, save_image

class SIFTController:
    def __init__(
        self,
        window: QWidget,
        image_load_btn: QPushButton,
        image_export_btn: QPushButton,
        loaded_image_panel: QWidget,
        result_image_panel: QWidget,
        param1_lcdNumber: QLCDNumber,
        apply_btn: QPushButton,
        ):

        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel
        self.param1_lcdNumber = param1_lcdNumber
        self.apply_btn = apply_btn

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
        self.apply_btn.clicked.connect(self._apply_SIFT)
        # self.param1_slider.valueChanged.connect(self._update_param1_label)

    def _load_image(self):
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)
            self.current_image = loaded_image_data
            if self.current_loaded_image_item is not None:
                self.current_loaded_image_item.clear()
                self.current_result_image_item.clear()
            self.current_loaded_image_item = pg.ImageItem(loaded_image_data.image_data)
            self.loaded_image_panel.addItem(self.current_loaded_image_item)

    def _export_result_image(self) -> None:
            # Get the cuurent result image and export it
            if self.current_result is None:
                return
            save_image(self.window, self.current_result)

    def _apply_SIFT(self):
        self.result_image_panel.clear()
        if self.current_image is None:
            return
        start_time = time.time()

        grayscale_image = cv2.cvtColor(self.current_image.image_data, cv2.COLOR_RGB2GRAY)

        keypoints, descriptors = computeKeypointsAndDescriptors(grayscale_image)  # Pass raw image data

        image_with_keypoints = cv2.drawKeypoints(self.current_image.image_data, keypoints, None)  # Use raw image data

        end_time = time.time()

        computation_time = end_time - start_time


        self.param1_lcdNumber.display(computation_time)

        print("SIFT computation time: {:.2f} seconds".format(computation_time))
        self.current_result = image_with_keypoints  # Directly store the result
        self.current_result_image_item = pg.ImageItem(image_with_keypoints)  # Create a new ImageItem
        self.result_image_panel.addItem(self.current_result_image_item)


