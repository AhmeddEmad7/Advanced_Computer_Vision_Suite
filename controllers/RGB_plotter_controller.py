import cv2
from PyQt6.QtWidgets import QWidget, QPushButton
from utils.image_loader import open_image
from models.image import Image, load_image_from_file_name
from models.image import Image
import pyqtgraph as pg

class RGBPlotterController:
    def __init__(self, window: QWidget, loaded_image: QWidget, r_hist: QWidget, g_hist: QWidget, b_hist: QWidget,
                r_cdf: QWidget, g_cdf: QWidget, b_cdf: QWidget, load_image_btn = QPushButton) -> None:
        
        self.window = window
        self.loaded_image_panel = loaded_image
        self.red_hist_panel = r_hist
        self.green_hist_panel = g_hist
        self.blue_hist_panel = b_hist
        self.red_cdf_panel = r_cdf
        self.green_cdf_panel = g_cdf
        self.blue_cdf_panel = b_cdf
        self.load_rgb_image_btn = load_image_btn

        self.loaded_image: Image = None
        self.loaded_image_item: pg.ImageItem = None

        # Setting background for graphs to be 'white'
        self.loaded_image_panel.setBackground('w')

        self.red_hist_panel.setBackground('w')
        self.green_hist_panel.setBackground('w')
        self.blue_hist_panel.setBackground('w')

        self.red_cdf_panel.setBackground('w')
        self.green_cdf_panel.setBackground('w')
        self.blue_cdf_panel.setBackground('w')

        self._initialize_signals_slots()
        self.loaded_image_panel.showAxes(False)
        self.loaded_image_panel.invertY(True)
        self.red_hist_panel.showGrid(True, True)
        self.red_cdf_panel.showGrid(True, True)
        self.green_hist_panel.showGrid(True, True)
        self.green_cdf_panel.showGrid(True, True)
        self.blue_hist_panel.showGrid(True, True)
        self.blue_cdf_panel.showGrid(True, True)
    
    def _initialize_signals_slots(self) -> None:
        self.load_rgb_image_btn.clicked.connect(self._load_image)

    def _load_image(self):
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)
            if(loaded_image_data.is_rgb()): # Check first if it is an RGB image
                self.loaded_image = loaded_image_data

                if self.loaded_image_item is not None:
                    self.loaded_image_item.clear()

                self.loaded_image_item = pg.ImageItem(self.loaded_image.image_data)
                self.loaded_image_panel.addItem(self.loaded_image_item)
                self._get_channels_histograms()
                self._get_channels_cdfs()
                self._plot_statistics()

    def _get_channels_histograms(self):
        self.r_hist = self.loaded_image.get_channel_hist_data(2)
        self.g_hist = self.loaded_image.get_channel_hist_data(1)
        self.b_hist = self.loaded_image.get_channel_hist_data(0)

    def _get_channels_cdfs(self):
        self.r_cdf = self.loaded_image.get_channel_cdf_data(2)
        self.g_cdf = self.loaded_image.get_channel_cdf_data(1)
        self.b_cdf = self.loaded_image.get_channel_cdf_data(0)

    def _plot_statistics(self):
        self.red_hist_panel.plot(self.r_hist, clear=True, pen={'color': (255, 0, 0), 'width': 2})
        self.red_cdf_panel.plot(self.r_cdf, clear=True, pen={'color': (255, 0, 0), 'width': 2})

        self.green_hist_panel.plot(self.g_hist, clear=True, pen={'color': (0, 255, 0), 'width': 2})
        self.green_cdf_panel.plot(self.g_cdf, clear=True, pen={'color': (0, 255, 0), 'width': 2})

        self.blue_hist_panel.plot(self.b_hist, clear=True, pen={'color': (0, 0, 255), 'width': 2})
        self.blue_cdf_panel.plot(self.b_cdf, clear=True, pen={'color': (0, 0, 255), 'width': 2})

            