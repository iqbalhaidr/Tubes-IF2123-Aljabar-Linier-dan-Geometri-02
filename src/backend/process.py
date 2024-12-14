import numpy as np
from PIL import Image
import os

# Image Processing and Loading
def preprocess_images(image_dir, target_size=(100, 100)):
    image_vectors = []
    image_paths = []
    
    for filename in os.listdir(image_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(image_dir, filename)
            image_paths.append(filepath)

            # Open image and process
            img = Image.open(filepath).convert('RGB')
            img_resized = img.resize(target_size)
            
            # Convert to grayscale
            img_array = np.array(img_resized)
            R, G, B = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
            grayscale = 0.2989 * R + 0.5870 * G + 0.1140 * B

            # Flatten and add to the list
            image_vectors.append(grayscale.flatten())
    
    return np.array(image_vectors), image_paths

# Data Centering
def standardize_data(data):
    mean_vector = np.mean(data, axis=0)
    centered_data = data - mean_vector
    return centered_data, mean_vector

# PCA Computation Using SVD
def compute_pca(data, n_components):
    U, S, Vt = np.linalg.svd(data, full_matrices=False)
    eigenvectors = Vt[:n_components].T  # Top components
    projected_data = data @ eigenvectors
    return projected_data, eigenvectors, S[:n_components]

# Similarity Computation
def find_similar_images(query_image, dataset, eigenvectors, mean_vector, top_k=5):
    query_standardized = query_image - mean_vector
    query_projection = query_standardized @ eigenvectors

    # Compute Euclidean distances
    distances = np.linalg.norm(dataset - query_projection, axis=1)
    sorted_indices = np.argsort(distances)[:top_k]
    sorted_results = [(idx, distances[idx]) for idx in sorted_indices]

    return sorted_results
