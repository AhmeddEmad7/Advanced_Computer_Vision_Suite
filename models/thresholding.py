import numpy as np
import cv2

def calculate_optimal_threshold(image):
    # Initial threshold
    T = np.mean(image)
    while True:
        # Split into background and object based on the threshold
        background = image[image <= T]
        objects = image[image > T]

        # Calculate the mean of the background and objects
        mean_background = np.mean(background) if len(background) > 0 else 0
        mean_objects = np.mean(objects) if len(objects) > 0 else 0

        # Update threshold
        T_new = (mean_background + mean_objects) / 2

        # Check for convergence
        if abs(T - T_new) < 0.5:  # Convergence threshold is 0.5
            break
        T = T_new
    return T


# This function will be used in controllers """"apply_optimal_threshold """"
def apply_optimal_threshold(image, global_threshold=True, block_size=32):
    # Convert to grayscale if the image is colored
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if global_threshold:
        # Apply global optimal thresholding
        threshold = calculate_optimal_threshold(image)
        _, binary_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        ##Pixels in the image with intensity values greater than this
        # threshold will be set to the maximum value (in this case, 255),
        # and those with lower intensities will be set to 0.
    else:
        # Apply local optimal thresholding
        binary_image = np.zeros_like(image)
        for i in range(0, image.shape[0], block_size):
            for j in range(0, image.shape[1], block_size):
                block = image[i : i + block_size, j : j + block_size]
                threshold = calculate_optimal_threshold(block)
                _, block_binary = cv2.threshold(
                    block, threshold, 255, cv2.THRESH_BINARY
                )
                binary_image[i : i + block_size, j : j + block_size] = block_binary

    return binary_image


def otsu_threshold(image):
    # Flatten the image into 1D array
    pixel_values = image.flatten()

    # Calculate histogram and probabilities of each intensity level
    histogram, _ = np.histogram(pixel_values, bins=np.arange(257), density=True)

    # Initial values
    s_max = (0, 0)  # Max sigma, Threshold

    for threshold in range(256):
        # Update probabilities and means
        wB = np.sum(histogram[:threshold])  # Weight Background // prop class 0
        wF = np.sum(histogram[threshold:])  # Weight Foreground // prop class 1

        mB = np.sum(np.arange(threshold) * histogram[:threshold]) / wB if wB > 0 else 0
        mF = (
            np.sum(np.arange(threshold, 256) * histogram[threshold:]) / wF
            if wF > 0
            else 0
        )

        # Calculate Between Class Variance
        sigma = wB * wF * (mB - mF) ** 2
        ## global mean is constant for all threshold values so can ignore it
        # Check if new maximum found
        ## as max sigma max threshold
        if sigma > s_max[0]:
            s_max = (sigma, threshold)

    # Apply threshold
    thresholded_image = (image > s_max[1]).astype(np.uint8) * 255
    return thresholded_image, s_max[1]


## this functionm will use in controllers """"apply_otsu_threshold"""
def apply_otsu_threshold(image, global_threshold=True, block_size=32):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if global_threshold:
        # Global Otsu thresholding
        _, threshold = otsu_threshold(image)
        print(f"Global Otsu Threshold: {threshold}")
        binary_image = (image > threshold).astype(np.uint8) * 255
    else:
        # Local Otsu thresholding
        height, width = image.shape
        binary_image = np.zeros_like(image, dtype=np.uint8)
        for i in range(0, height, block_size):
            for j in range(0, width, block_size):
                block = image[i : i + block_size, j : j + block_size]
                if block.size == 0:
                    continue
                _, threshold = otsu_threshold(block)
                binary_image[i : i + block_size, j : j + block_size] = (
                    block > threshold
                ).astype(np.uint8) * 255

    return binary_image

def find_optimal_thresholds(image, num_classes):
    # Ensure the image is in grayscale
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Calculate histogram and normalize it to get probability densities
    histogram, bin_edges = np.histogram(image, bins=256, range=(0, 256))

    thresholds = []
    for _ in range(num_classes - 1):
        max_variance = 0
        best_threshold = None

        for threshold in range(1, 256):
            wB = np.sum(histogram[:threshold])
            wF = np.sum(histogram[threshold:])
            if wB == 0 or wF == 0:
                continue

            mB = np.sum(np.arange(threshold) * histogram[:threshold]) / wB
            mF = np.sum(np.arange(threshold, 256) * histogram[threshold:]) / wF

            variance = wB * wF * (mB - mF) ** 2
            if variance > max_variance:
                max_variance = variance
                best_threshold = threshold

        if best_threshold is not None:
            thresholds.append(best_threshold)
            # Zero out the histogram below the current threshold to find the next one
            histogram[:best_threshold] = 0

    return thresholds


def apply_multi_class_threshold(image, num_classes):
    # Ensure the image is in grayscale
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Find optimal thresholds based on the desired number of classes
    thresholds = find_optimal_thresholds(image, num_classes)

    # Ensure the thresholds list includes the lower bound (0) and the upper bound (256)
    thresholds = [0] + sorted(thresholds) + [256]

    # Create a segmented image where each class is represented by a unique intensity
    segmented_image = np.zeros_like(image, dtype=np.uint8)

    for i in range(1, len(thresholds)):
        mask = (image >= thresholds[i - 1]) & (image < thresholds[i])
        segmented_image[mask] = (255 // (num_classes - 1)) * (i - 1)
        ## calc the intensity value for each class and assign it to the pixels in the mask region

    return segmented_image


def local_multi_class_thresholding(image, block_size, num_classes):
    if len(image.shape) > 2:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    height, width = image.shape
    segmented_image = np.zeros_like(image)

    # Process each block separately
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            block = image[i:i + block_size, j:j + block_size]
            # Calculate thresholds for this block
            # Apply thresholds to segment the block
            segmented_block = apply_multi_class_threshold(block, num_classes)
            segmented_image[i:i + block_size, j:j + block_size] = segmented_block

    return segmented_image
