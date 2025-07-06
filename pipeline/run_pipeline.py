# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: [Driver] runs the main pipeline

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
# == sys path ==

from pipeline.pipes.load_image import LoadImagePipe
from pipeline.pipes.clahe_green import CLAHEGreenChannelPipe
from pipeline.pipes.lesion_masks import LesionMaskLoadingPipe
from pipeline.pipes.extract_patches import PatchExtractionPipe
from pipeline.pipes.label_patches import LabelPatchesPipe
from pipeline.pipes.save_patches import SavePatchesPipe
from pipeline.utils.data_utils import load_and_prepare_metadata

from pipeline.core import DRPipeline


all_data = load_and_prepare_metadata()

pipeline = DRPipeline([
    LoadImagePipe(),
    CLAHEGreenChannelPipe(),
    LesionMaskLoadingPipe(),
    PatchExtractionPipe(),
    LabelPatchesPipe(),
    SavePatchesPipe()
])

_ = pipeline.run(all_data) # assignable

# === TBRMVD ===
# # assignable
# results = pipeline.run(all_data)
# # flatten
# all_patches = [patch for item in results for patch in item["patches"]]
# # df
# patches_df = pd.DataFrame(all_patches)
