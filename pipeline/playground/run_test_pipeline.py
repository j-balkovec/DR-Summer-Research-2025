# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: test runner for DRPipeline using 2 sample images

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

from pipeline.pipes.load_image import LoadImagePipe
from pipeline.pipes.clahe_green import CLAHEGreenChannelPipe
from pipeline.pipes.lesion_masks import LesionMaskLoadingPipe
from pipeline.pipes.extract_patches import PatchExtractionPipe
from pipeline.pipes.label_patches import LabelPatchesPipe
from pipeline.pipes.save_patches import SavePatchesPipe

from pipeline.core import DRPipeline

from pipeline.utils.io_utils import read_csv_image_paths
from pipeline.config.settings import IMAGE_DIR, CSV_PATH

from pipeline.utils.clean_repo import clean_pipeline_outputs

clean_pipeline_outputs()

# === Load & filter CSV entries ===

all_data = read_csv_image_paths(CSV_PATH)

# Filter to just 2 images
test_data = [
    d for d in all_data
    if Path(d["image_path"]).name in ["0068_1.png"]
]

# Add full path to image
for item in test_data:
    item["image_path"] = IMAGE_DIR / item["image_path"]

# === Construct pipeline ===
pipeline = DRPipeline([
    LoadImagePipe(),
    CLAHEGreenChannelPipe(),
    LesionMaskLoadingPipe(),
    PatchExtractionPipe(),
    LabelPatchesPipe(),
    SavePatchesPipe()
])

# === Run pipeline ===
_ = pipeline.run(test_data) # assignable
