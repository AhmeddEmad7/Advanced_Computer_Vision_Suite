from PyQt6.QtWidgets import QWidget, QPushButton, QSlider, QLabel
import pyqtgraph as pg

from models.image import Image,load_image_from_file_name
from models.canny_edge_detection import apply_canny_edge_detection

from utils.image_loader import open_image, save_image
from enum import Enum
class SLIDERS(Enum):
    SIGMA = 0
    LOW = 1
    HIGH = 2

class CannyEdgeDetectorController:
    def __init__(self, window: QWidget, image_load_btn: QPushButton, image_export_btn: QPushButton,
                loaded_image_panel: QWidget, result_image_panel: QWidget,
                apply_canny_transform_btn: QPushButton, low_threshold_slider: QSlider,
                 high_threshold_slider: QSlider, low_threshold_value_txtbox: QLabel,
                  sigma_slider: QSlider,high_threshold_value_txtbox: QLabel,sigma_value_txtbox: QLabel,) -> None:
        
        self.window = window
        self.image_load_btn = image_load_btn
        self.image_export_btn = image_export_btn
        self.loaded_image_panel = loaded_image_panel
        self.result_image_panel = result_image_panel

        self.apply_canny_transform_btn = apply_canny_transform_btn
        self.low_threshold_slider = low_threshold_slider
        self.high_threshold_slider = high_threshold_slider
        self.sigma_slider = sigma_slider
        
        self.low_threshold_value_txtbox = low_threshold_value_txtbox
        self.high_threshold_value_txtbox = high_threshold_value_txtbox
        self.sigma_value_txtbox = sigma_value_txtbox


        self.low_threshold_slider.setRange(1,10)
        self.high_threshold_slider.setRange(1,10)
        self.sigma_slider.setRange(1,10)

        self.low_threshold_slider.setValue(1)
        self.high_threshold_slider.setValue(1)
        self.sigma_slider.setValue(1)

        self.low_threshold_slider.setSingleStep(1)
        self.high_threshold_slider.setSingleStep(1)
        self.sigma_slider.setSingleStep(1)


        self.low_threshold_value_txtbox.setText(str((self.low_threshold_slider.value()/10)))
        self.high_threshold_value_txtbox.setText(str((self.high_threshold_slider.value()/10)))
        self.sigma_value_txtbox.setText(str((self.sigma_slider.value())))



        # Initialize app controller state
        self.current_image: Image = None
        self.current_result: Image = None
        self.current_loaded_image_item: pg.ImageItem = None
        self.current_result_image_item: pg.ImageItem = None


        self.loaded_image_panel.showAxes(False)
        self.loaded_image_panel.invertY(True)
        self.result_image_panel.showAxes(False)
        self.result_image_panel.invertY(True)

        self._initialize_signals_slots()
    
    
    def _initialize_signals_slots(self):
        self.image_load_btn.clicked.connect(self._load_image)
        self.image_export_btn.clicked.connect(self._export_result_image)
        self.apply_canny_transform_btn.clicked.connect(self._apply_canny)
        self.low_threshold_slider.valueChanged.connect( lambda: self._handle_slider_value_changes(SLIDERS.LOW))
        self.high_threshold_slider.valueChanged.connect(lambda :self._handle_slider_value_changes(SLIDERS.HIGH))
        self.sigma_slider.valueChanged.connect(lambda: self._handle_slider_value_changes(SLIDERS.SIGMA))

    def _handle_slider_value_changes(self,type):
        if(type == SLIDERS.LOW):
            value = self.low_threshold_slider.value()/10
            self.low_threshold_value_txtbox.setText(str(value))
        elif(type == SLIDERS.HIGH):
            value = self.high_threshold_slider.value()/10
            self.high_threshold_value_txtbox.setText(str(value))
        elif(type ==SLIDERS.SIGMA):
            value = self.sigma_slider.value()
            self.sigma_value_txtbox.setText(str(value))        


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



    def _apply_canny(self):
        self.result_image_panel.clear()

        if self.current_loaded_image_item is None:
            return

        self.current_result = apply_canny_edge_detection(self.current_image,self.sigma_slider.value(),self.low_threshold_slider.value(),self.high_threshold_slider.value())
        self.current_resulted_image_item = pg.ImageItem(self.current_result.image_data)
        self.result_image_panel.addItem(self.current_resulted_image_item)
