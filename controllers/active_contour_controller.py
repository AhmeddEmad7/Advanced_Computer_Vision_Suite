import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QSlider, QLineEdit
from models.image import Image, rgb2gray, load_image_from_file_name
from models.active_contour import ActiveContour
from utils.image_loader import open_image

class ActiveContourController:
    def __init__(
            self,
            window: QWidget,
            image_load_btn: QPushButton,
            run_snake_btn: QPushButton,
            loaded_image_panel: QWidget,
            result_image_panel: QWidget,
            radius_slider: QSlider,
            points_slider: QSlider,
            iteration_slider: QSlider,
            max_px_move_slider: QSlider,
            alpha_slider: QSlider,
            beta_slider: QSlider,
            gamma_slider: QSlider,
            conv_threshold_slider: QSlider,
            radius_label: QLabel,
            points_label: QLabel,
            iteration_label: QLabel,
            max_px_move_label: QLabel,
            alpha_label: QLabel,
            beta_label: QLabel,
            gamma_label: QLabel,
            conv_threshold_label: QLabel,
            chain_code_text: QLineEdit,
            area_text: QLineEdit,
            perimeter_text: QLineEdit

        ) -> None:
            
            # Connect to Window Elements
            self.window = window
            self.image_load_btn = image_load_btn
            self.run_snake_btn = run_snake_btn
            self.loaded_image_panel = loaded_image_panel
            self.result_image_panel = result_image_panel
            self.radius_slider = radius_slider
            self.points_slider = points_slider
            self.iterations_slider = iteration_slider
            self.max_px_move_slider = max_px_move_slider
            self.alpha_slider = alpha_slider
            self.beta_slider = beta_slider
            self.gamma_slider = gamma_slider
            self.convergence_thres_slider = conv_threshold_slider
            self.radius_label = radius_label
            self.points_label = points_label
            self.iterations_label = iteration_label
            self.max_px_move_label = max_px_move_label
            self.alpha_label = alpha_label
            self.beta_label = beta_label
            self.gamma_label = gamma_label
            self.convergence_thres_label = conv_threshold_label
            self.chain_code = chain_code_text
            self.contour_area = area_text
            self.contour_perimeter = perimeter_text

            # Initialize app controller state
            self.initial_image: Image = None
            self.initial_image_item: pg.ImageItem = None
            self.result_image_item: pg.ImageItem = None

            #config
            self._initialize_signals_slots()
            self.loaded_image_panel.showAxes(False)
            self.loaded_image_panel.invertY(True)
            self.result_image_panel.showAxes(False)
            self.result_image_panel.invertY(True)
        

    def _initialize_signals_slots(self) -> None:
        self.image_load_btn.clicked.connect(self._load_image)
        self.run_snake_btn.clicked.connect(self.run_snake_algorithm)

        self.radius_slider.valueChanged.connect(self._update_radius_value)
        self.points_slider.valueChanged.connect(self._update_points_value)
        self.iterations_slider.valueChanged.connect(self._update_iterations_value)
        self.max_px_move_slider.valueChanged.connect(self._update_max_px_move_value)
        self.alpha_slider.valueChanged.connect(self._update_alpha_value)
        self.beta_slider.valueChanged.connect(self._update_beta_value)
        self.gamma_slider.valueChanged.connect(self._update_gamma_value)
        self.convergence_thres_slider.valueChanged.connect(self._update_convergence_thres_value)

    def _update_radius_value(self, value) -> None:
        self.radius_label.setText(str(value))
        self.draw_initial_contour()

    def _update_points_value(self, value) -> None:
        self.points_label.setText(str(value))
        self.draw_initial_contour()

    def _update_iterations_value(self, value) -> None:
        self.iterations_label.setText(str(value))

    def _update_max_px_move_value(self, value) -> None:
        self.max_px_move_label.setText(str(value / 10.0))

    def _update_alpha_value(self, value) -> None:
        self.alpha_label.setText(str(value / 100.0))

    def _update_beta_value(self, value) -> None:
        self.beta_label.setText(str(value/ 100.0))

    def _update_gamma_value(self, value) -> None:
        self.gamma_label.setText(str(value / 1000.0))

    def _update_convergence_thres_value(self, value) -> None:
        self.convergence_thres_label.setText(str(value / 10.0))

    def _load_image(self) -> None:
        image_path = open_image(self.window)
        if image_path:
            loaded_image_data: Image = load_image_from_file_name(image_path)
            self.initial_image = loaded_image_data

            if self.initial_image_item is not None:
                self.initial_image_item.clear()
                self.loaded_image_panel.clear()
                self.result_image_panel.clear()

            self.initial_image_item = pg.ImageItem(self.initial_image.image_data)
            self.loaded_image_panel.addItem(self.initial_image_item)
            self.result_image_item = pg.ImageItem(self.initial_image.image_data)
            self.result_image_panel.addItem(self.result_image_item)
            self.draw_initial_contour()

    def draw_initial_contour(self):
        self.circle_contour = np.array([[]])
        self.loaded_image_panel.clear()
        self.initial_image_item = pg.ImageItem(self.initial_image.image_data)
        self.loaded_image_panel.addItem(self.initial_image_item)

        radius, n_points, _ , _ , _ , _ , _ , _ = self.get_parameters_values()
        self.image_to_process = rgb2gray(self.initial_image)
        image_height, image_width = self.image_to_process.height, self.image_to_process.width

        center = (image_height // 2, image_width // 2)
        theta = np.linspace(0, 2*np.pi, n_points)
        self.circle_contour = np.column_stack([center[0] + radius * np.cos(theta),
                                        center[1] + radius * np.sin(theta)])
        
        pen = pg.mkPen(color='r', width=8)
        self.loaded_image_panel.plot(self.circle_contour[:,0], self.circle_contour[:,1], pen=pen)

    def get_parameters_values(self):
        radius = self.radius_slider.value()
        points = self.points_slider.value()
        alpha = self.alpha_slider.value() / 100.0
        beta = self.beta_slider.value() / 100.0
        gamma = self.gamma_slider.value() / 1000.0
        max_px_move = self.max_px_move_slider.value() / 10.0
        max_num_iter = self.iterations_slider.value()
        convergence = self.convergence_thres_slider.value() / 10.0

        return radius, points, alpha, beta, gamma, max_px_move, max_num_iter, convergence
    
    def run_snake_algorithm(self):
        self.result_image_panel.clear()
        self.result_image_item = pg.ImageItem(self.initial_image.image_data)
        self.result_image_panel.addItem(self.result_image_item)
        _, _, alpha, beta, gamma, max_px_move, max_num_iter, convergence = self.get_parameters_values()
        ac = ActiveContour(
            alpha=alpha,
            beta=beta,
            gamma=gamma,
            max_px_move=max_px_move,
            max_num_iter=max_num_iter,
            convergence=convergence
        )
        final_snake = ac.run(self.image_to_process, self.circle_contour)
        pen = pg.mkPen(color='b', width=8)
        self.result_image_panel.plot(final_snake[:,0], final_snake[:,1], pen=pen)
        code = ac.compute_chain_code(final_snake)
        area, perimeter = ac.compute_area_perimeter(code)
        self.preview_information(code, area, perimeter)
    
    def preview_information(self, code, area, perimeter):
        self.chain_code.setText(''.join(map(str, code)))
        self.contour_area.setText(str(area))
        self.contour_perimeter.setText(str(perimeter))