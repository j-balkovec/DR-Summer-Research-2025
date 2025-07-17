# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: provides geometry-related functions for polygon manipulation and patch validity checking
import numpy as np

from shapely.geometry import Polygon, box
from skimage import measure
from shapely.affinity import translate


# =================== WARNIGNS ===================
import warnings

# note: this is here because the healthy patches don't include any lesions, thus no shape to intersect with.
#       "shapely" throws a warning when trying to intersect with an empty shape
warnings.filterwarnings("ignore", message=".*invalid value encountered in intersection.*")
warnings.filterwarnings("ignore", message=".*invalid value encountered in simplify_preserve_topology.*")
warnings.filterwarnings("ignore", message=".*invalid value encountered in intersects.*")
# =================== WARNIGNS ===================


def polygon_from_mask(mask: np.ndarray) -> list:
    # pre: mask is a binary mask (2D numpy array)
    # post: returns a list of valid polygons extracted from the mask
    # desc: extracts contours from the binary mask and converts them to polygons

    contours = measure.find_contours(mask, 0.5)
    return [Polygon(c[:, ::-1]) for c in contours if Polygon(c[:, ::-1]).is_valid]

def patch_center_to_polygon(x: int, y: int, patch_half: int) -> Polygon:
    # pre: x, y are patch centers; patch_half is half patch size
    # post: returns a shapely Polygon representing the patch
    # desc: creates a square polygon from a center point

    return Polygon([
        (x - patch_half, y - patch_half),
        (x + patch_half, y - patch_half),
        (x + patch_half, y + patch_half),
        (x - patch_half, y + patch_half)
    ])

def is_patch_inside(polygon: Polygon, x: int, y: int, patch_half: int) -> bool:
    # pre: polygon is a valid shapely Polygon, x and y are coordinates, patch_half is half the size of the patch
    # post: returns True if the patch centered at (x, y) with size patch_half is inside the polygon
    # desc: checks if a square patch centered at (x, y) with size patch_half is completely inside the polygon

    patch_box = box(x - patch_half, y - patch_half, x + patch_half, y + patch_half)
    return polygon.contains(patch_box)

def translate_polygon(polygon: Polygon, dx: float, dy: float) -> Polygon:
    # pre: polygon is a valid shapely Polygon, dx and dy are translation offsets
    # post: returns a new Polygon translated by (dx, dy)
    # desc: translates the polygon by the specified offsets

    return translate(polygon, xoff=dx, yoff=dy)

def get_patch_coordinates(x, y, size):
    # pre: x, y are the center coordinates of the patch, size is the size of the patch
    # post: returns a dictionary with the coordinates of the four corners of the patch
    # desc: calculates the coordinates of the four corners of a square patch centered at (x, y)

    return {
        "top-left": (x, y),
        "top-right": (x + size - 1, y),
        "bottom-left": (x, y + size - 1),
        "bottom-right": (x + size - 1, y + size - 1),
    }
