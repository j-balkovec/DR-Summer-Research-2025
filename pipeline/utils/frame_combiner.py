# Jakob Balkovec
# DR-Pipeline
#   Sun Jul 6th 2025

# brief: combines the pandas DataFrames from each patch subdirectory into a single master DataFrame

# == sys path ==
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))
# == sys path ==

import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from pipeline.config.settings import PATCH_OUTPUT_DIR, TARGET_DF, SUBDIR, MASTER_PICKLE_DF_PATH

def load_patch_df(image_dir):
    # pre: image_dir is a valid directory containing the subdirectory with TARGET_DF
    # post: returns a DataFrame loaded from the TARGET_DF file in the specified sub
    # desc: loads the DataFrame from the specified subdirectory and attaches the image_id
    #       to the DataFrame for tracking purposes

    df_path = image_dir / SUBDIR / TARGET_DF
    if df_path.exists():
        try:
            df = pd.read_pickle(df_path)
            df["image_id"] = image_dir.name  # attach image_id for tracking
            return df
        except Exception as e:
            print(f"[ERROR] {df_path.name}: {e}")
    return None

def build_master_df():
    # pre: PATCH_OUTPUT_DIR contains subdirectories with TARGET_DF files
    # post: returns a concatenated DataFrame of all patch metadata
    # desc: aggregates all patch DataFrames from each image subdirectory into a single master Data
    #       DataFrame for easier access and analysis

    image_dirs = [d for d in PATCH_OUTPUT_DIR.iterdir() if (d / SUBDIR / TARGET_DF).exists()]
    with ThreadPoolExecutor() as executor:
        dfs = list(executor.map(load_patch_df, image_dirs))

    master_df = pd.concat([df for df in dfs if df is not None], ignore_index=True)
    return master_df.sort_values(by="image_id").reset_index(drop=True)

# brief: main entry point
if __name__ == "__main__":
    print("[INFO] Building master DataFrame from patch metadata...")
    master_df = build_master_df()
    master_df.to_pickle(MASTER_PICKLE_DF_PATH)
    print(f"[DONE] Master DataFrame shape: {master_df.shape}")

