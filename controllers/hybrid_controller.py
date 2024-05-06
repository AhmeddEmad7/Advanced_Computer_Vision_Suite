import cv2
import pyqtgraph as pg
from utils.image_loader import open_image
from models.image import Image, load_image_from_file_name
from models.filters import FrequencyFilter
from PyQt6.QtWidgets import QWidget, QPushButton

class HybridController:
    def __init__(
        self,
        window: QWidget,
        low_pass_image_panel: QWidget,
        high_pass_image_panel: QWidget,
        hybrid_image_panel: QWidget,
        lp_load_btn: QPushButton,
        hp_load_btn: QPushButton, 
        apply_hybrid_btn: QPushButton
    ):
        self.window = window
        self.low_pass_image_panel = low_pass_image_panel
        self.high_pass_image_panel = high_pass_image_panel
        self.hybrid_image_panel = hybrid_image_panel
        self.lp_load_btn = lp_load_btn
        self.hp_load_btn = hp_load_btn
        self.apply_hybrid_btn = apply_hybrid_btn

        self.low_pass_image: Image = None
        self.high_pass_image: Image = None
        self.hybrid_image: Image = None
        self.loaded_low_pass_image_item: pg.ImageItem = None
        self.loaded_high_pass_image_item: pg.ImageItem = None
        self.hybrid_image_item: pg.ImageItem = None

        self._initialize_signals_slots()
        self.low_pass_image_panel.showAxes(False)
        self.high_pass_image_panel.showAxes(False)
        self.hybrid_image_panel.showAxes(False)
        self.low_pass_image_panel.invertY(True)
        self.high_pass_image_panel.invertY(True)
        self.hybrid_image_panel.invertY(True)

    def _initialize_signals_slots(self) -> None:
        self.lp_load_btn.clicked.connect(lambda: self._load_image("LPF"))
        self.hp_load_btn.clicked.connect(lambda: self._load_image("HPF"))
        self.apply_hybrid_btn.clicked.connect(self._hybrid_images)

    def _load_image(self, filter):
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)

            if(filter == "LPF"):
                self.low_pass_image = loaded_image_data

                if self.loaded_low_pass_image_item is not None:
                    self.loaded_low_pass_image_item.clear()
                self.loaded_low_pass_image_item = pg.ImageItem(self.low_pass_image.image_data)
                self.low_pass_image_panel.addItem(self.loaded_low_pass_image_item)

            else:
                self.high_pass_image = loaded_image_data

                if self.loaded_high_pass_image_item is not None:
                    self.loaded_high_pass_image_item.clear()

                self.loaded_high_pass_image_item = pg.ImageItem(self.high_pass_image.image_data)
                self.high_pass_image_panel.addItem(self.loaded_high_pass_image_item)            

    def _hybrid_images(self):
        filter = FrequencyFilter(20)
        self.high_pass_image.image_data = cv2.resize(self.high_pass_image.image_data, (self.low_pass_image.image_data.shape[1], self.low_pass_image.image_data.shape[0]))

        low_pass_filtered_image = filter.apply_low_pass_filter(self.low_pass_image)
        high_pass_filtered_image = filter.apply_high_pass_filter(self.high_pass_image)
        hybrid_image = Image(low_pass_filtered_image.image_data + high_pass_filtered_image.image_data)

        if self.hybrid_image_item is not None:
            self.hybrid_image_item.clear()

        self.hybrid_image_item = pg.ImageItem(hybrid_image.image_data)
        self.hybrid_image_panel.addItem(self.hybrid_image_item)


        


    