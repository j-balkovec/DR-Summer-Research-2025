# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: contains image processing utilities such as CLAHE, green_channel, etc.

import cv2
import numpy as np

from pipeline.config.settings import PATCH_BLACK_THRESHOLD, BLACK_RATIO

def extract_green_channel(image: np.ndarray) -> np.ndarray:
    # pre: image is a valid BGR image
    # post: returns the green channel of the image
    # desc: extracts the green channel from a BGR image

    return image[:, :, 1]

def apply_clahe(image: np.ndarray, clip_limit=2.0, tile_grid_size=(8, 8)) -> np.ndarray:
    # pre: image is a valid grayscale image
    # post: CLAHE enhanced image
    # desc: applies CLAHE to the image

    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(image)

def resize_image(image: np.ndarray, size=(1280, 1280)) -> np.ndarray:
    # pre: image is a valid image
    # post: resized image
    # desc: resizes the image to the specified size

    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)

def normalize_image(image: np.ndarray) -> np.ndarray:
    # pre: image is a valid image with pixel values in [0, 255]
    # post: normalized image with pixel values in [0, 1]
    # desc: normalizes pixel values to [0, 1] range

    return image.astype(np.float32) / 255.0


# Pixel level, more rigid and harsh checks
def count_black_pixels(patch, threshold=PATCH_BLACK_THRESHOLD):
    # pre: patch is a valid image patch (numpy array)
    # post: returns the number of pixels below the threshold
    # desc: counts pixels in the patch that are below the specified threshold

    if isinstance(patch, np.ndarray):
        if patch.ndim == 3:
            return np.sum(np.all(patch < threshold, axis=-1))
        elif patch.ndim == 2:
            return np.sum(patch < threshold)
    return 0

# Looser check, more flexible
def is_mostly_black(patch, threshold=PATCH_BLACK_THRESHOLD, black_ratio=BLACK_RATIO):
    # pre: patch is a valid image patch (numpy array)
    # post: returns True if the patch is mostly black, False otherwise
    # desc: checks if the patch has a high ratio of black pixels
    arr = np.array(patch)
    if arr.ndim == 3:
        arr = arr.mean(axis=2)
    black_pixels = np.sum(arr < threshold)
    return (black_pixels / arr.size) > black_ratio

