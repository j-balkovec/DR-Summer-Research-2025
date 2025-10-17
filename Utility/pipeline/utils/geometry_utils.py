# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: provides geometry-related functions for polygon manipulation and patch validity checking
import numpy as np
from typing import Optional, Tuple, List
import cv2

from pipeline.config.settings import (
    PATCH_SIZE, PATCH_BLACK_THRESHOLD, BLACK_RATIO,
    BLACK_PIXELS_THRESHOLD, LESION_LABELS
)

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

def _ensure_uint8(mask: Optional[np.ndarray]) -> np.ndarray:
    # pre: mask is None or np.ndarray
    # post: ensure binary uint8 mask or None
    # desc: convert to binary uint8 mask or None
    if mask is None:
        return None
    m = mask
    if m.dtype != np.uint8:
        m = (m > 0).astype(np.uint8)
    else:
        m = (m > 0).astype(np.uint8)
    return m

def _reflective_crop(img: np.ndarray, cx: int, cy: int, size: int) -> Tuple[np.ndarray, Tuple[int,int,int,int]]:
    # pre: img is HxW or HxWxC, cx,cy=center coords, size=patch size (square)
    # post: patch, bbox (x,y,w,h) in original image coords
    # desc: extract square patch centered at cx,cy with reflective padding if needed
    h, w = img.shape[:2]
    half = size // 2
    x0, y0 = cx - half, cy - half
    x1, y1 = x0 + size, y0 + size

    pad_left   = max(0, -x0)
    pad_top    = max(0, -y0)
    pad_right  = max(0, x1 - w)
    pad_bottom = max(0, y1 - h)

    if any((pad_left, pad_top, pad_right, pad_bottom)):
        img_p = cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_REFLECT_101)
        x0 += pad_left; y0 += pad_top; x1 += pad_left; y1 += pad_top
        patch = img_p[y0:y1, x0:x1].copy()
        # bbox reported in original image coords (clamped at 0)
        bx = max(0, cx - half); by = max(0, cy - half)
        return patch, (bx, by, size, size)
    else:
        patch = img[y0:y1, x0:x1].copy()
        return patch, (x0, y0, size, size)

def crop_128_no_pad(img, cx, cy, size=128, max_shift=None):
    # pre: img is HxW or HxWxC, cx,cy=center coords, size=patch size (square), max_shift=optional max shift from cx,cy
    # post: patch or None if out of bounds or exceeds max_shift, bbox (x
    # desc: extract square patch centered at cx,cy; return None if out of bounds or exceeds max_shift

    h, w = img.shape[:2]
    half = size // 2

    # clamp center to keep full patch inside
    nx = min(max(cx, half), w - half)
    ny = min(max(cy, half), h - half)

    # optionally refuse large shifts (protect centroid fidelity)
    if max_shift is not None:
        if abs(nx - cx) > max_shift or abs(ny - cy) > max_shift:
            return None, None  # signal to skip

    x0, y0 = nx - half, ny - half
    x1, y1 = x0 + size, y0 + size
    patch = img[y0:y1, x0:x1].copy()
    return patch, (x0, y0, size, size)

def _connected_component_centroids(mask: np.ndarray) -> List[Tuple[int,int,int]]:
    # pre: mask is binary uint8
    # post: list of (cx,cy,area) for each connected component
    # desc: find connected components and return their centroids and areas

    m = (mask > 0).astype(np.uint8)
    n, lbl = cv2.connectedComponents(m)
    out = []
    for i in range(1, n):
        ys, xs = np.where(lbl == i)
        if xs.size == 0:
            continue
        cx = int(round(xs.mean()))
        cy = int(round(ys.mean()))
        out.append((cx, cy, int(xs.size)))
    return out

def _dilate(mask: np.ndarray, r: int) -> np.ndarray:
    # pre: mask is binary uint8, r=dilation radius in pixels
    # post: dilated mask
    # desc: dilate binary mask by r pixels using elliptical kernel

    if r <= 0:
        return (mask > 0).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    return cv2.dilate((mask > 0).astype(np.uint8), k, iterations=1)

def _random_point_in_mask(mask: np.ndarray) -> Optional[Tuple[int,int]]:
    # pre: mask is binary uint8
    # post: random (x,y) point in mask or None if no valid point
    # desc: select random point in mask

    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return None
    i = np.random.randint(0, xs.size)
    return int(xs[i]), int(ys[i])

def _make_label_vector(cls_name: Optional[str]) -> List[int]:
    # pre: cls_name is None or str
    # post: binary label vector
    # desc: create binary label vector for given class name

    vec = [0] * len(LESION_LABELS)
    if cls_name in LESION_LABELS:
        vec[LESION_LABELS.index(cls_name)] = 1
    return vec

def _black_tag(patch_rgb: np.ndarray) -> str:
    # pre: patch_rgb is RGB patch of shape (PATCH_SIZE, PATCH_SIZE, 3)
    # post: "black" if patch is considered black, else None
    # desc: determine if patch is predominantly black based on thresholds

    gray_patch = np.mean(patch_rgb, axis=2)
    black_pixels = np.sum(gray_patch < PATCH_BLACK_THRESHOLD)
    black_ratio = black_pixels / (PATCH_SIZE * PATCH_SIZE)
    if black_pixels >= BLACK_PIXELS_THRESHOLD and black_ratio >= BLACK_RATIO:
        return "black"
    return None
