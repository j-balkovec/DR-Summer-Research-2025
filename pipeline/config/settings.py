# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: centralized configuration for paths, patch sizes, constants, and pipeline settings

from pathlib import Path
import math

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PIPELINE_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = BASE_DIR / "data" / "Seg-set" / "Original_Images"
MASK_ROOT = BASE_DIR / "data" / "Seg-set"

# 1. brief: path to the CSV file containing image-level labels and segmentation metadata
# 2. brief: root directory where extracted patch images will be saved
# 3. brief: path to the master DataFrame that stores patch-level metadata
# 4. brief: path to the master CSV file that stores image paths and metadata
CSV_PATH = BASE_DIR / "data" / "Seg-set" / "DR_Seg_Grading_Label.csv" # 1
PATCH_OUTPUT_DIR = BASE_DIR / "data" / "patches"                      # 2
MASTER_PICKLE_DF_PATH = PATCH_OUTPUT_DIR / "master_df.pkl"            # 3
MASTER_PATHS_CSV_PATH = PATCH_OUTPUT_DIR / "master_paths.csv"         # 4

# 1. brief: path to the DataFrame that stores patch-level metadata
# 2. brief: subdir name where the df is held
TARGET_DF = "patch_frame.pkl"   # 1
SUBDIR = "frame"                # 2

# brief: path to a folder used for intermediate caching of pipeline results (unused as of right now)
CACHE_DIR = PIPELINE_DIR / "cache"

PATCH_SIZE = 128                    # 128 x 128 -> 100 pathches per image
PATCH_HALF = PATCH_SIZE // 2
IMAGE_SHAPE = (1280, 1280)
HEALTHY_TO_LESION_RATIO = 1.5       # 60/40 -> 1.5

# 1. brief: margin in pixles to avoid sampling too close to lesions
# 2. brief: keep centers inside the FOV if provided
# 3. brief: exclude optic disc area when sampling healthy patches
# 4. brief: random seed for reproducibility
LESION_DILATE_PX = 6                # 1
FOV_REQUIRED = True                 # 2
AVOID_OPTIC_DISC = True             # 3
SEED = 1337                         # 4

# 1. brief: if True, skips partial patches at the borders and retains only fully enclosed 25x25 crops
# 2. brief: if True, extracts both symptomatic (lesion-centered) and healthy (non-lesion) patches
EXTRACT_FULL_PATCHES_ONLY = False    # 1 !__DEPRECATED__! since 1280 is evenly divisible by 128
EXTRACT_ALL_PATCHES = True           # 2

# brief: mapping of lesion types to their corresponding subdirectory names under the mask root
LESION_MASKS = {
    'microaneurysms': 'Microaneurysms_Masks',
    'hemorrhages': 'Hemorrhage_Masks',
    'hard_exudates': 'HardExudate_Masks',
    'soft_exudates': 'SoftExudate_Masks',
}

# brief: directory where visual check overlays will be saved
VISUAL_CHECK_DIR = PATCH_OUTPUT_DIR / "visual_check"

# brief: color map for lesion types used in visual checks
# note: this is only used to color the lesion types in the visual check overlays
COLOR_MAP = {
    "microaneurysms": (0, 0, 255),     # Red (BGR)
    "hemorrhages": (255, 0, 0),         # Blue
    "hard_exudates": (0, 255, 255),    # Yellow
    "soft_exudates": (0, 255, 0),      # Green
}

# brief: list of lesion types for easy access.
# note: !dependency! -> @see LESION_MASKS
#       this is used to iterate over lesion types in various parts of the pipeline
#       and to ensure consistency with the mask loading process.
#       it is also used to generate labels for patches in the labeling pipeline.
LESION_LABELS = list(LESION_MASKS.keys())

# 1. brief: maximum number of patches/images per shard (e.g. healthy_n has SHARD_DIR_LIMIT patches)
# 2. brief: maximum number of healthy patches to retain in the final dataset (30k as of right now)
# 3. brief: maximum number of black patches to retain in the final dataset (2k as of right now)
SHARD_DIR_LIMIT = 1000          # 1
HEALTHY_PATCHES_LIMIT = 30000   # 2
BLACK_PATCHES_LIMIT = 2000      # 3

# 1. brief: threshold for determining if a patch is mostly black (in pixels)
# 2. brief: ratio of black pixels in a patch to consider it mostly black
# 3. brief: minimum number of black pixels in a patch to consider it mostly black
PATCH_BLACK_THRESHOLD = 10     # 1
BLACK_RATIO = 0.90             # 2
BLACK_PIXELS_THRESHOLD = BLACK_RATIO * pow(PATCH_SIZE, 2) # 3 0.88 * patch_size^2 (128 * 128 = 16384)

# brief: if False, tqdm bar behaves as normal, else it's turned [OFF]
DISABLE_TQDM = False # default behavior

def toggle_disable_tqdm(default=False):
    # brief: toggles the global DISABLE_TQDM setting
    # note: [ON] = True, [OFF] = False
    global DISABLE_TQDM
    DISABLE_TQDM = default

# brief: batch size when running the pipeline in parallel
BATCH_SIZE = 100

# brief: maximum number of healthy patches to retain in each batch when running in parallel
# note: this is used to limit the number of healthy patches processed in each parallel batch
#       to avoid overwhelming the system with too many healthy patches at once + I don't want to rewrite my pipe
HEALTHY_PATCHES_LIMIT_MP = HEALTHY_PATCHES_LIMIT // BATCH_SIZE  # for multiprocessing

# ===== logging =====

# 1. brief: enables or disables detailed logging throughout the pipeline
# 2. brief: directory where pipeline logs will be saved
# 3. brief: path to the main pipeline log file
# 4. brief: path to the log file that stores batch processing results in JSON format
# 5. brief: maximum size of the log file in bytes before rotating
# 6. brief: number of backup log files to retain

LOG_ALL = False                                              # 1
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"    # 2
LOG_FILE = LOG_DIR / "pipeline.log"                          # 3
BATCH_LOG_PATH = LOG_DIR / "batch_log.json"                  # 4
MAX_BYTES = 512 * 1024  # 512 KB                             # 5
BACKUP_COUNT = 2                                             # 6

# ===== logging =====

if __name__ == "__main__":
    pass
