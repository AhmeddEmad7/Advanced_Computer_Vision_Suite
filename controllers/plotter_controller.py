import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QPushButton
from models.image import Image, load_image_from_file_name, rgb2gray
from utils.image_loader import open_image


class PlotterController:
    def __init__(
        self,
        window: QWidget,
        image_load_btn: QPushButton,
        loaded_image_panel: QWidget,
        gs_image_panel: QWidget,
        hist_plot_panel: QWidget,
        cdf_plot_panel: QWidget,
    ):
        self.window = window
        self.image_load_btn = image_load_btn
        self.loaded_image_panel = loaded_image_panel
        self.gs_image_panel = gs_image_panel
        self.hist_plot_panel = hist_plot_panel
        self.cdf_plot_panel = cdf_plot_panel
        
        # Setting background for graphs to be 'white'
        self.loaded_image_panel.setBackground('w')
        self.gs_image_panel.setBackground('w')
        self.hist_plot_panel.setBackground('w')
        self.cdf_plot_panel.setBackground('w')

        # Initialize app controller state
        self.current_image: Image = None
        self.current_loaded_image_item: pg.ImageItem = None
        
        self.gs_image: Image = None
        self.gs_image_item: pg.ImageItem = None

        # Configure UI
        self._initialize_signals_slots()
        self.loaded_image_panel.showAxes(False)
        self.loaded_image_panel.invertY(True)
        self.gs_image_panel.showAxes(False)
        self.gs_image_panel.invertY(True)
        self.hist_plot_panel.showGrid(True, True)
        self.cdf_plot_panel.showGrid(True, True)

    def _initialize_signals_slots(self) -> None:
        self.image_load_btn.clicked.connect(self._load_image)

    # def _convert_to_gray(self) -> None:
    #     if self.current_image is None:
    #         return
    #     gray_image: Image = Noise.convert_to_gray(self.current_image)
    #     self._render_result_with_image(gray_image)

    def _load_image(self) -> None:
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)
            gs_image_data: Image = rgb2gray(loaded_image_data)

            self.current_image = loaded_image_data
            self.gs_image = gs_image_data
            if self.current_loaded_image_item is not None:
                self.current_loaded_image_item.clear()
                self.gs_image_item.clear()

            self.current_loaded_image_item = pg.ImageItem(self.current_image.image_data)
            self.gs_image_item = pg.ImageItem(self.gs_image.image_data)

            self.loaded_image_panel.addItem(self.current_loaded_image_item)
            self.gs_image_panel.addItem(self.gs_image_item)

        # TODO: Histogram and CDF plotting don't work due to data shape mismatch
        hist_plot = self.current_image.get_hist_data()
        cdf_plot = self.current_image.get_cdf_data()
        self.hist_plot_panel.plot(hist_plot, clear=True, pen={'color': (0, 0, 0), 'width': 2})
        self.cdf_plot_panel.plot(cdf_plot, clear=True, pen={'color': (0, 0, 0), 'width': 2})
