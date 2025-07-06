# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: centralized configuration for paths, patch sizes, constants, and pipeline settings

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
PIPELINE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "data" / "Seg-set" / "Original_Images"
MASK_ROOT = BASE_DIR / "data" / "Seg-set"

# 1. brief: path to the CSV file containing image-level labels and segmentation metadata
# 2. brief: root directory where extracted patch images will be saved
# 3. brief: path to CSV metadata file for all extracted patches
# 4. brief: path to pickled pandas DataFrame containing patch metadata (including image arrays, labels, etc.)
CSV_PATH = BASE_DIR / "data" / "Seg-set" / "DR_Seg_Grading_Label.csv" # 1
PATCH_OUTPUT_DIR = BASE_DIR / "data" / "patches"                      # 2
PATCHES_CSV = PATCH_OUTPUT_DIR / "csv" / "patch_metadata.csv"         # 3
PATCHES_PICKLE = PATCH_OUTPUT_DIR / "frame" / "patch_frame.pkl"       # 4


# brief: path to a folder used for intermediate caching of pipeline results (unused as of right now)
CACHE_DIR = PIPELINE_DIR / "cache"

PATCH_SIZE = 25
PATCH_HALF = PATCH_SIZE // 2
IMAGE_SHAPE = (1280, 1280)

# 1. brief: if True, skips partial patches at the borders and retains only fully enclosed 25x25 crops
# 2. brief: if True, extracts both symptomatic (lesion-centered) and healthy (non-lesion) patches
EXTRACT_FULL_PATCHES_ONLY = False    # 1
EXTRACT_ALL_PATCHES = True           # 2

# brief: mapping of lesion types to their corresponding subdirectory names under the mask root
LESION_MASKS = {
    'microaneurysms': 'Microaneurysms_Masks',
    'hemorrhages': 'Hemorrhage_Masks',
    'hard_exudates': 'HardExudate_Masks',
    'soft_exudates': 'SoftExudate_Masks',
    'irma': 'IRMA_Masks',
    'neovascularization': 'Neovascularization_Masks'
}

# ===== logging =====

# 1. brief: enables or disables detailed logging throughout the pipeline
# 2. brief: directory where pipeline logs will be saved
# 3. brief: path to the main pipeline log file
# 4. brief: maximum size of the log file in bytes before rotating
# 5. brief: number of backup log files to retain

LOG_ALL = False # 1                                          # 1
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"    # 2
LOG_FILE = LOG_DIR / "pipeline.log"                          # 3
MAX_BYTES = 5 * 1024 * 1024  # 5MB                           # 4
BACKUP_COUNT = 2                                             # 5

# ===== logging =====
