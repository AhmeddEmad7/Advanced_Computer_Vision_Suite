import numpy as np
import cv2
from models.sift import computeKeypointsAndDescriptors
from models.image import rgb2gray

def calculate_SSD(des1,des2):
    ssd = 0
    for i in range(len(des1)):
        ssd += (des1[i]-des2[i])**2
    ssd = np.sqrt(ssd)
    return ssd

def calculate_NCC(image_1_descriptors, image_2_descriptors):
    image_1_descriptors_norm = (image_1_descriptors - np.mean(image_1_descriptors)) / np.std(image_1_descriptors)
    image_2_descriptors_norm = (image_2_descriptors - np.mean(image_2_descriptors)) / np.std(image_2_descriptors)

    # Compute normalized cross-correlation
    ncc = np.dot(image_1_descriptors_norm, image_2_descriptors_norm) / len(image_1_descriptors)
    return ncc

def feature_matching(descriptor1, descriptor2, method, threshold1, threshold2):
    keyPoints1 = descriptor1.shape[0]
    keyPoints2 = descriptor2.shape[0]

    matched_features = []
    for kp1 in range(keyPoints1):
        # Initial variables (will be updated) where distance for SSD is a distance and for
        # NCC it is the correlation score
        score = np.inf if(method == "SSD") else -np.inf
        y_index = -1
        
        for kp2 in range(keyPoints2):
            if method == "SSD":
                distance = calculate_SSD(descriptor1[kp1], descriptor2[kp2])
                # print(score)
                if distance < score:
                    score = distance
                    y_index = kp2

            elif method == "NCC":
                corr_score = calculate_NCC(descriptor1[kp1], descriptor2[kp2])
                if corr_score > score:
                    score = corr_score
                    y_index = kp2

        if method == "SSD":
            # Score here indicates distance for SSD
            if score >= threshold1 and score <= threshold2:
                feature = cv2.DMatch()
                # The index of the feature in the first image
                feature.queryIdx = kp1
                #  The index of the feature in the second image
                feature.trainIdx = y_index
                # The distance between the two features
                feature.distance = score
                matched_features.append(feature)
        else:
            # Score here indicates correlation score for SSD
            # NCC takes all keypoints having a correlation score higher than 0.75
            if(score >= 0.75):
                feature = cv2.DMatch()
                feature.queryIdx = kp1
                feature.trainIdx = y_index
                feature.distance = score
                matched_features.append(feature)

    return matched_features

def draw_matching(image_1, image_2, method, threshold1, threshold2):
    # Compute keypoints and descriptors on "gray" images only
    kps1, descriptors1 = computeKeypointsAndDescriptors(rgb2gray(image_1))
    kps2, descriptors2 = computeKeypointsAndDescriptors(rgb2gray(image_2))
    matched_features = feature_matching(descriptors1, descriptors2, method, threshold1, threshold2)
    matched_image = cv2.drawMatches(image_1, kps1, image_2, kps2, matched_features, None, flags=cv2.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
    
    return matched_image
