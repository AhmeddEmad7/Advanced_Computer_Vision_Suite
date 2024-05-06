import numpy as np
import cv2

################ K-Means ################
def initialize_centers(k, image):
    """Randomly initialize k centers"""
    height, width, _ = image.shape
    centers = np.zeros((k, 3))  # RGB image
    for i in range(k):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        centers[i] = image[y, x]
    return centers

def assign_clusters(image, centers):
    """Assign each pixel to the nearest cluster center"""
    height, width, _ = image.shape
    clusters = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            pixel = image[y, x]
            distances = np.linalg.norm(centers - pixel, axis=1)
            cluster = np.argmin(distances)
            clusters[y, x] = cluster
    return clusters

def update_centers(image, clusters, k):
    """Update cluster centers based on assigned pixels"""
    centers = np.zeros((k, 3))
    for i in range(k):
        points = image[clusters == i]
        if len(points) > 0:
            centers[i] = np.mean(points, axis=0)
    return centers

def kmeans(image, k, max_iterations):
    """Perform k-means clustering on the image"""
    centers = initialize_centers(k, image)
    for _ in range(max_iterations):
        clusters = assign_clusters(image, centers)
        new_centers = update_centers(image, clusters, k)
        if np.allclose(new_centers, centers):
            break
        centers = new_centers
    return clusters, centers
################ K-Means ################
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y
class Segmentation:

    @staticmethod
    def _apply_kmeans(image, k, max_iterations):
        """Assign each pixel to the color of its nearest cluster center"""
        clusters, centers = kmeans(image, k, max_iterations)
        segmented_image = np.zeros_like(image)
        for i in range(len(centers)):
            segmented_image[clusters == i] = centers[i]
        return segmented_image.astype(np.uint8)
    
    @staticmethod
    def _apply_mean_shift(image, bandwidth):
        """Assign each pixel to the mean of the window around it"""
        # Compute the mean shift vector for each pixel
        height, width, channels = image.shape
        ms_image = np.zeros((height, width), dtype=np.int32)
        label = 1
        for y in range(height):
            for x in range(width):
                if ms_image[y, x] == 0:
                    mean_vector = np.zeros(channels, dtype=np.float32)
                    pixel_rgb_vector = image[y, x].astype(np.float32)
                    count = 0
                    while True:
                        prev_mean_vector = mean_vector
                        prev_count = count
                        for i in range(max(y - bandwidth, 0), min(y + bandwidth, height)):
                            for j in range(max(x - bandwidth, 0), min(x + bandwidth, width)):
                                # Checking if pixel is not assigned to a cluster yet and if its color is close to the pixel's
                                if ms_image[i, j] == 0 and np.linalg.norm(pixel_rgb_vector - image[i, j]) < bandwidth:
                                    mean_vector += image[i, j]
                                    count += 1
                                    ms_image[i, j] = label

                        # Mean calculated
                        mean_vector /= count
                        # Difference between mean vectors is less than a threshold or the number of pixels assigned to the cluster (count) remains the same as in the previous iteration
                        if np.linalg.norm(mean_vector - prev_mean_vector) < 1e-5 or count == prev_count:
                            break

                    ms_image[ms_image == label] = count
                    label += 1

        unique_labels = np.unique(ms_image)
        ms_colored_image = np.zeros_like(image)
        for i, label in enumerate(unique_labels):
            # Assign the mean color of pixels in each cluster in the original image to the corresponding pixels in the segmented image
            mask = (ms_image == label)
            ms_colored_image[mask] = np.mean(image[mask], axis=0)

        return ms_colored_image
    
    @staticmethod
    def _region_growing(image, seed_point, threshold):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        segmented_image = np.zeros_like(image)
        # Initialize the queue with the seed point
        queue = [seed_point]

        # Define connectivity (4-connectivity)
        connectivity = [(0, 1), (1, 0), (-1, 0), (0, -1)]

        # Loop through the queue until it's empty
        while queue:
            # Get the current pixel
            current_point = queue.pop(0)
            x, y = current_point

            # Check if the current pixel is within the image boundaries
            if 0 <= x < image.shape[0] and 0 <= y < image.shape[1]:
                # Check if the pixel is unsegmented
                if segmented_image[x, y] == 0:
                    # Check the similarity criterion
                    if abs(int(image[x, y]) - int(image[seed_point])) < threshold:
                        # Add the current pixel to the segmented region
                        segmented_image[x, y] = 5
                        # Add neighboring pixels to the queue
                        for dx, dy in connectivity:
                            queue.append((x - dx, y - dy))


        return 255 - segmented_image


class AgglomerativeClustering:
    def __init__(self, source: np.ndarray, clusters_numbers: int = 2, initial_k: int = 25):
        """

        :param source:
        :param clusters_numbers:
        :param initial_k:
        """
        self.clusters_num = clusters_numbers
        self.initial_k = initial_k
        src = np.copy(source.reshape((-1, 3)))

        self.fit(src)

        self.output_image = [[self.predict_center(list(src)) for src in row] for row in source]
        self.output_image = np.array(self.output_image, np.uint8)

    def initial_clusters(self, points):
        """
        partition pixels into self.initial_k groups based on color similarity
        """
        groups = {}
        d = int(256 / self.initial_k)
        for i in range(self.initial_k):
            j = i * d
            groups[(j, j, j)] = []
        for i, p in enumerate(points):
            if i % 100000 == 0:
                print('processing pixel:', i)
            go = min(groups.keys(), key=lambda c: euclidean_distance(p, c))
            groups[go].append(p)
        return [g for g in groups.values() if len(g) > 0]

    def fit(self, points):
        # initially, assign each point to a distinct cluster
        print('Computing initial clusters ...')
        self.clusters_list = self.initial_clusters(points)
        print('number of initial clusters:', len(self.clusters_list))
        print('merging clusters ...')

        while len(self.clusters_list) > self.clusters_num:
            # Find the closest (most similar) pair of clusters
            cluster1, cluster2 = min(
                [(c1, c2) for i, c1 in enumerate(self.clusters_list) for c2 in self.clusters_list[:i]],
                key=lambda c: clusters_distance_2(c[0], c[1]))

            # Remove the two clusters from the clusters list
            self.clusters_list = [c for c in self.clusters_list if c != cluster1 and c != cluster2]

            # Merge the two clusters
            merged_cluster = cluster1 + cluster2

            # Add the merged cluster to the clusters list
            self.clusters_list.append(merged_cluster)

            print('number of clusters:', len(self.clusters_list))

        print('assigning cluster num to each point ...')
        self.cluster = {}
        for cl_num, cl in enumerate(self.clusters_list):
            for point in cl:
                self.cluster[tuple(point)] = cl_num

        print('Computing cluster centers ...')
        self.centers = {}
        for cl_num, cl in enumerate(self.clusters_list):
            self.centers[cl_num] = np.average(cl, axis=0)

    def predict_cluster(self, point):
        """
        Find cluster number of point
        """
        # assuming point belongs to clusters that were computed by fit functions
        return self.cluster[tuple(point)]

    def predict_center(self, point):
        """
        Find center of the cluster that point belongs to
        """
        point_cluster_num = self.predict_cluster(point)
        center = self.centers[point_cluster_num]
        return center


def clusters_distance_2(cluster1, cluster2):
    """
    Computes distance between two centroids of the two clusters

    cluster1 and cluster2 are lists of lists of points
    """
    cluster1_center = np.average(cluster1, axis=0)
    cluster2_center = np.average(cluster2, axis=0)
    return euclidean_distance(cluster1_center, cluster2_center)

    
def apply_agglomerative(source: np.ndarray, clusters_numbers: int = 2, initial_clusters: int = 25):
    """

    :param source:
    :param clusters_numbers:
    :param initial_clusters:
    :return:
    """
    agglomerative = AgglomerativeClustering(source=source, clusters_numbers=clusters_numbers,
                                            initial_k=initial_clusters)

    return agglomerative.output_image

def euclidean_distance(x1, x2):
    return np.sqrt(np.sum((x1 - x2) ** 2))


def regionGrow(img, seeds, thresh, p = 1):
    height, weight = img.shape
    seedMark = np.zeros(img.shape)
    seedList = []

    for seed in seeds:
        seedList.append(seed)
    label = 1
    connects = selectConnects(p)

    while (len(seedList) > 0):
        currentPoint = seedList.pop(0)

        seedMark[currentPoint.x, currentPoint.y] = label

        for i in range(8):
            tmpX = currentPoint.x + connects[i].x
            tmpY = currentPoint.y + connects[i].y

            if tmpX < 0 or tmpY < 0 or tmpX >= height or tmpY >= weight:
                continue

            grayDiff = getGrayDiff(img, currentPoint, Point(tmpX, tmpY))

            if grayDiff < thresh and seedMark[tmpX, tmpY] == 0:
                seedMark[tmpX, tmpY] = label
                seedList.append(Point(tmpX, tmpY))

    return seedMark


def getGrayDiff(img, currentPoint, tmpPoint):
    return abs(int(img[currentPoint.x, currentPoint.y]) - int(img[tmpPoint.x, tmpPoint.y]))


def selectConnects(p):
    if p != 0:
        connects = [Point(-1, -1), Point(0, -1), Point(1, -1),
                    Point(1, 0), Point(1, 1), Point(0, 1),
                    Point(-1, 1), Point(-1, 0)]
    else:
        connects = [Point(0, -1), Point(1, 0), Point(0, 1), Point(-1, 0)]

    return connects

def apply_region_growing(source: np.ndarray, points, threshold):
    """

    :param source:
    :return:
    """

    src = np.copy(source)
    img_gray = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)

    x = points[0]
    y = points[1]
    seeds = [Point(x, y)]

    # seeds = [Point(10, 10), Point(82, 150), Point(20, 300)]
    output_image = regionGrow(img_gray, seeds, threshold)

    return output_image