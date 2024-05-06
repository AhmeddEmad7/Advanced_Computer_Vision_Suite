import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication
# from controllers.thresholding_controller import ThresholdingController
from controllers.noise_controller import NoiseController
from controllers.equalizer_normalizer_controller import EqualizationNormalizationController
from controllers.edge_detection_controller import EdgeDetectionController
from controllers.filter_controller import FilterController
from controllers.plotter_controller import PlotterController
from controllers.RGB_plotter_controller import RGBPlotterController
from controllers.hybrid_controller import HybridController
from controllers.hough_tranform_controller import HoughTransformController
# from controllers.active_contour_controller import ActiveContourController
from controllers.active_contour_controller_greedy import ActiveContourControllerGreedy
from controllers.canny_edge_detection_controller import CannyEdgeDetectorController
from controllers.features_extractor_controller import FeaturesExtractorController
from controllers.sift_controller import SIFTController
from controllers.match_controller import MatchController
from controllers.threshold_controller import ThresholdController
from controllers.segmentation_controller import SegementationController


uiclass, baseclass = pg.Qt.loadUiType("views/mainwindow.ui")


class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()

        # Window and UI configurations
        self.setupUi(self)
        self.setWindowTitle("Computer Vision Toolkit")

        self._initialize_controller()

    def _initialize_controller(self):
        
        self.noise_controller = NoiseController(
            window=self,
            image_load_btn=self.noise_load_image_btn,
            image_export_btn=self.noise_export_image_btn,
            loaded_image_panel=self.noise_loaded_image,
            result_image_panel=self.noise_result_image,
            noise_type_combo=self.noise_type_combo,
            param1_label=self.noise_param1_label,
            param2_label=self.noise_param2_label,
            param1_value_label=self.noise_param_value_label_1,
            param2_value_label=self.noise_param_value_label_2,
            param1_slider=self.noise_param1_slider,
            param2_slider=self.noise_param2_slider,
            apply_noise_btn=self.noise_apply_btn,
        )

        self.edge_detector_contoller = EdgeDetectionController(
            window=self,
            image_load_btn=self.edge_load_img_btn,
            image_export_btn=self.edge_export_img_btn,
            loaded_image_panel=self.edge_loaded_image,
            result_image_panel=self.edge_exported_image,
            edge_detector_combo=self.edge_detectors_combo,
            apply_edge_detection_btn=self.apply_edge_detection_btn,
        )

        self.filter_controller = FilterController(
            window=self,
            image_load_btn=self.filter_load_image_btn,
            image_export_btn=self.filter_export_image_btn,
            loaded_image_panel=self.filter_loaded_image,
            result_image_panel=self.filter_result_image,
            filter_type_combo=self.filter_type_combo,
            param1_label=self.filter_param1_label,
            param2_label=self.filter_param2_label,
            param3_label=self.filter_param_value_label_3,
            param4_label=self.filter_param_value_label_4,
            param1_slider=self.filter_param1_slider,
            param2_slider=self.filter_param2_slider,
            apply_filter_btn=self.filter_apply_btn,
        )

        self.equalizer_normalizer_controller = EqualizationNormalizationController(
            window=self,
            image_load_btn=self.equalize_load_img_btn,
            image_export_btn=self.equalize_export_img_btn,
            loaded_image_panel=self.equalize_loaded_image,
            result_image_panel=self.equalize_exported_image,
            mode_combo=self.mode_combo_box,
            apply_equalization_btn=self.equalizer_normalizer_apply,
        )

        # self.thresholding_controller = ThresholdingController(
        #     window=self,
        #     image_load_btn=self.thres_load_image_btn,
        #     image_export_btn=self.thres_export_image_btn,
        #     loaded_image_panel=self.thres_loaded_image,
        #     result_image_panel=self.thres_result_image,
        #     thres_combo=self.thres_type_combo,
        #     param1_slider=self.thres_param1_slider,
        #     param2_slider=self.thres_param2_slider,
        #     param1_label=self.thres_param1_label,
        #     param2_label=self.thres_param2_label,
        #     param3_label=self.thres_param_value_label_5,
        #     param4_label=self.thres_param_value_label_6,
        #     apply_thres_btn=self.thres_apply_btn,
        # )

        self.plotter_controller = PlotterController(
            window=self,
            image_load_btn=self.plot_load_image_btn,
            loaded_image_panel=self.plot_loaded_image,
            gs_image_panel=self.plot_loaded_gs_image,
            hist_plot_panel=self.plot_hist,
            cdf_plot_panel=self.plot_cdf,
        )

        self.hybrid_controller = HybridController(
            window=self,
            low_pass_image_panel=self.hybrid_load_lowpass_image,
            high_pass_image_panel=self.hybrid_load_highpass_image,
            hybrid_image_panel=self.hybrid_result_image,
            lp_load_btn=self.load_lowpass_btn,
            hp_load_btn=self.load_highpass_btn,
            apply_hybrid_btn=self.apply_hybrid_btn,
        )

        self.rgb_plotter_controller = RGBPlotterController(
            window=self,
            loaded_image=self.rgb_loaded_image,
            r_hist=self.plot_hist_r,
            g_hist=self.plot_hist_g,
            b_hist=self.plot_hist_b,
            r_cdf=self.plot_cdf_r,
            g_cdf=self.plot_cdf_g,
            b_cdf=self.plot_cdf_b,
            load_image_btn=self.plot_load_rgb_image_btn,
        )

        self.canny_edge_detection_contoller = CannyEdgeDetectorController(
            window=self,
            image_load_btn=self.canny_load_image_btn,
            image_export_btn=self.canny_export_image_btn,
            loaded_image_panel=self.canny_loaded_image,
            result_image_panel=self.canny_result_image,
            apply_canny_transform_btn=self.canny_apply_btn,
            low_threshold_slider=self.low_threshold_slider,
            high_threshold_slider=self.high_threshold_slider,
            sigma_slider=self.sigma_slider,
            low_threshold_value_txtbox=self.low_threshold_value_txtbox,
            high_threshold_value_txtbox=self.high_threshold_value_txtbox,
            sigma_value_txtbox=self.sigma_value_txtbox
        )

        self.hough_transform_contoller = HoughTransformController(
            window=self,
            image_load_btn=self.hough_load_image_btn,
            image_export_btn=self.hough_export_image_btn,
            loaded_image_panel=self.hough_loaded_image,
            result_image_panel=self.hough_result_image,
            hough_type_combo=self.hough_type_combo,
            hough_apply_btn=self.hough_apply_btn,
            threshold_slider=self.threshold_slider,
            threshold_value_txtbox=self.threshold_value_txtbox
        )

        # self.active_contour_controller = ActiveContourController(
        #     window= self,
        #     image_load_btn= self.load_image_btn,
        #     run_snake_btn= self.snake_apply_btn,
        #     loaded_image_panel= self.initial_image_panel,
        #     result_image_panel= self.final_image_panel,
        #     radius_slider= self.radiusSlider,
        #     points_slider= self.pointsSlider,
        #     iteration_slider= self.iterationsSlider,
        #     max_px_move_slider= self.maxpixelSlider,
        #     alpha_slider= self.alphaSlider,
        #     beta_slider= self.betaSlider,
        #     gamma_slider= self.gammaSlider,
        #     conv_threshold_slider= self.convthresholdSlider,
        #     radius_label= self.radiusSlider_value,
        #     points_label= self.pointsSlider_value,
        #     iteration_label= self.iterationsSlider_value,
        #     max_px_move_label= self.maxpixelSlider_value,
        #     alpha_label= self.alphaSlider_value,
        #     beta_label= self.betaSlider_value,
        #     gamma_label= self.gammaSlider_value,
        #     conv_threshold_label= self.convthresholdSlider_value,
        #     chain_code_text= self.chain_code_text,
        #     area_text= self.area_text,
        #     perimeter_text= self.perimeter_text
        # )

        self.active_contour_controller = ActiveContourControllerGreedy(
            window= self,
            image_load_btn= self.load_image_btn,
            run_snake_btn= self.snake_apply_btn,
            loaded_image_panel= self.initial_image_panel,
            result_image_panel= self.final_image_panel,
            radius_slider= self.radiusSlider,
            points_slider= self.pointsSlider,
            iteration_slider= self.iterationsSlider,
            alpha_slider= self.alphaSlider,
            beta_slider= self.betaSlider,
            radius_label= self.radiusSlider_value,
            points_label= self.pointsSlider_value,
            iteration_label= self.iterationsSlider_value,
            alpha_label= self.alphaSlider_value,
            beta_label= self.betaSlider_value,
            chain_code_text= self.chain_code_text,
            area_text= self.area_text,
            perimeter_text= self.perimeter_text
        )

        self.features_extractor_controller = FeaturesExtractorController(
            window=self,
            image_load_btn=self.harris_load_image_btn,
            image_export_btn=self.harris_export_image_btn,
            loaded_image_panel=self.harris_loaded_image,
            result_image_panel=self.harris_result_image,
            param1_label=self.harris_param1_value_label,
            param1_slider=self.harris_param1_slider,
            apply_btn=self.harris_apply_btn,
            apply_lambda_minus_btn=self.harris_lambda_btn,
            clear_btn=self.harris_clear_btn,
            exec_time_label=self.exec_time_label,
        )

        self.sift_controller = SIFTController(
            window=self,
            image_load_btn=self.sift_load_image_btn,
            image_export_btn=self.sift_export_image_btn,
            loaded_image_panel=self.sift_loaded_image,
            result_image_panel=self.sift_result_image,
            param1_lcdNumber=self.lcdNumber,
            apply_btn=self.sift_apply_btn,
        )

        self.match_controller = MatchController(
            window=self,
            image_1_load_btn=self.match_load_image_btn_1,
            image_2_load_btn=self.match_load_image_btn_2,
            image_export_btn=self.match_export_image_btn,
            apply_btn=self.match_apply_btn,
            loaded_image_1_panel=self.match_loaded_image_1,
            loaded_image_2_panel=self.match_loaded_image_2,
            result_image_panel=self.match_result_image,
            threshold1_slider=self.match_thres1_slider,
            threshold2_slider=self.match_thres2_slider,
            method_comboBox=self.method_comboBox,
            match_lcdNumber=self.match_lcdNumber,
            threshold1_label=self.match_param1_value_label,
            threshold2_label=self.match_param2_value_label,
            lower_bound_label=self.lower_bound_label,
            upper_bound_label=self.upper_bound_label,
        )

        self.threshold_controller = ThresholdController(
            window=self,
            image_load_btn=self.threshold_load_image_btn,
            image_export_btn=self.threshold_export_image_btn,
            apply_btn=self.threshold_apply_btn,
            loaded_image_panel=self.threshold_loaded_image,
            result_image_panel=self.threshold_result_image,
            mode_comboBox=self.threshold_mode_combobox,
            global_radio_btn=self.global_radio_btn,
            local_radio_btn=self.local_radio_btn,
            box_size_slider=self.threshold_boxsize_slider,
            class_slider=self.threshold_class_slider,
            label=self.label,
            label2=self.label_2,
            box_size_label=self.box_size_label,
            num_classes_label=self.num_classes_label,
        )

        self.segmentation_controller = SegementationController(
            window=self,
            image_load_btn=self.segmentation_load_image_btn,
            image_export_btn=self.segmentation_export_image_btn,
            apply_btn=self.segmentation_apply_btn,
            loaded_image_panel=self.loaded_image_panel,
            result_image_panel=self.segmented_image_panel,
            method_comboBox=self.segmentation_comboBox,
            param1_slider=self.param1_slider,
            param2_slider=self.param2_slider,
            param1_slider_value=self.param1_slider_value,
            param2_slider_value=self.param2_slider_value,
            param1_name=self.param1_label,
            param2_name=self.param2_label,
        )


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
