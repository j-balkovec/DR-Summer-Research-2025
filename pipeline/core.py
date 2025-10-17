# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: defines the main DRPipeline class to run registered image processing steps

# == sys path ==
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
# == sys path ==

from typing import List, Dict

import pandas as pd

from pipeline.utils.logger import get_logger
from pipeline.utils.io_utils import ensure_dir
from pipeline.config.settings import LOG_ALL, DISABLE_TQDM
from pipeline.utils.io_utils import tqdm_if_verbose

logger = get_logger(__name__, file_logging=True)

class Pipe:
    # brief: base class for all pipeline components
    def process(self, data: Dict) -> Dict:
        raise NotImplementedError("{!important!} each pipe must implement a process() method")

class DRPipeline:
    # brief: manages and runs a sequential set of data processing steps

    def __init__(self, pipes: List[Pipe], batch_idx=None):
        # pre: pipes is a list of classes with a `process()` method
        # post: initializes a pipeline with registered stages
        self.pipes = pipes
        self.batch_idx = batch_idx
        logger.info(f"[Main Line] Initialized with {len(pipes)} pipes") if LOG_ALL else None

    def run(self, dataset: List[Dict]) -> List[Dict]:
        # pre: dataset is a list of dicts, each representing one input case
        # post: returns dataset after passing through all pipe stages
        # desc: applies each pipe sequentially to each item in the dataset

        logger.info(f"[Main Line] Starting run on {len(dataset)} items") if LOG_ALL else None
        results = []

        for item in tqdm_if_verbose(dataset, desc="Running Pipeline", disable=DISABLE_TQDM):
            data = item.copy()
            for pipe in self.pipes:
                pipe_name = pipe.__class__.__name__
                logger.debug(f"[Main Line] Running pipe: {pipe_name}") if LOG_ALL else None
                data = pipe.process(data)
            results.append(data)

        logger.info("[Main Line] Run complete") if LOG_ALL else None

        # # collect all patches into a dataframe
        # all_patches = []
        # for result in results:
        #     all_patches.extend(result.get("patches", []))

        # patch_df = pd.DataFrame(all_patches)
        # logger.info(f"[Main Line] Final patch dataframe shape: {patch_df.shape}") if LOG_ALL else None

        # # store as attribute so it can be processed after running it
        # self.patch_df = patch_df

        # batch_idx = results[0].get("batch_idx", None)
        # pickle_path = PATCHES_PICKLE if self.batch_idx is None else PATCHES_PICKLE.parent / f"patches_batch_{self.batch_idx}.pkl"

        # ensure_dir(pickle_path.parent)
        # patch_df.to_pickle(pickle_path)
        # if LOG_ALL:
        #     logger.info(f"saved patch dataframe to {pickle_path}")

        # return results
