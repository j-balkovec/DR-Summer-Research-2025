# Project Directory Overview

This document provides an overview of the project directory structure and some important notes to help you navigate and use the resources effectively.

## Directory Structure

The project is organized as follows:

```
.
├── Jakob
├── Literature
│   ├── CNN
│   ├── DLMedicalImages
│   ├── DR
│   ├── FundusImageAnalysis
│   ├── HybridAppraoch
│   └── Sckit-learnCheatSheet
├── Models
│   ├── Alyssa-Patch
│   │   ├── Multi
│   │   └── Single
│   ├── Daniel-Image
│   │   ├── Multi
│   │   └── Single
│   └── Jakob-Hybrid
│       ├── Analysis
│       ├── Multi
│       └── Single
├── Notebooks
│   ├── FDGAR_ds
│   └── KAGGLE_ds
├── Reports
│   ├── Alyssa-Patch
│   ├── Daniel-Image
│   └── Jakob-Hybrid
│       └── images
└── Utility
    ├── pipeline
    │   ├── __pycache__
    │   ├── cache
    │   ├── config
    │   │   └── __pycache__
    │   ├── jobs
    │   │   └── __pycache__
    │   ├── logs
    │   ├── notebooks
    │   ├── pipes
    │   │   └── __pycache__
    │   ├── schema
    │   └── utils
    │       └── __pycache__
    ├── scripts
    └── XMLparser
        ├── __pycache__
        ├── data
        │   └── groundtruth
        ├── examples
        │   └── parsed
        └── tests

51 directories
```

## Main Directories of Interest

While there are many directories, you can skip some depending on your focus. The primary directories you will likely use are:

- **Models:** Contains different approaches implemented by each team member. Each approach is organized into subdirectories for single-class and multi-class classification.
- **Notebooks:** Jupyter notebooks for data exploration and preliminary analysis.
- **Utility:** Contains scripts and pipeline configurations used throughout the project.

## Additional Notes

### Pipeline Usage

The pipeline is ready to run. Once you have access to the data, you can update the data path and execute it. Look in the `jobs` directory and decide what kind of job you want to run.

**Single-Threaded Implementation:**

This implementation works great if you want to run the pipeline over a small subset of the data or if you have limited system resources. However, it is not recommended for processing the entire dataset due to its significantly slower performance (expect 8hrs+ over the whole FDGAR dataset).

**Multi-Threaded Implementation:**

This implementation should be your default choice for running the pipeline, as it is designed to run concurrently and significantly speeds up processing time. Before you run it, make sure your environment supports multithreading and can handle up to 8 worker threads. If that is not the case, you can modify/reduce the number of worker threads in the configuration file located in `Utility/pipeline/config`. Know that this version brings down the execution time to around 30-45min over the whole FDGAR dataset, which is a significant improvement compared to the single threaded version.

Note that the "progress" logs for the pipeline don't work as expected. The whole purpose of them was to give you the abilty to restart the pipeline from a checkpoint if it failed or was interrupted. However, due to the way multithreading works, the logs don't get written in the correct order, making them useless for that purpose. I recommend using 2 workarounds:

1. Monitor the output directories to see which files have been processed already.
2. Run the whole thing in one go without stopping it.

> **Tip:** Close all tabs and applications running during the execution of the pipeline to free up as many system resources as possible.

**Caveats:** When I was running the pipeline, I found the disk I/O to be a huge bottle neck. When running multiple threads (8 in my case), they're all trying to read and write from the same place, slowing down the pipeline as a queue forms. This is annoying, but normal behavior, and unfortunately, there is no easy workaround unless you go into very low-level system optimizations, which was out of scope for this project.

> **Tip:** If you stop the pipeline mid way, or if it throws an error, it WILL NOT! release the resources it was using. You will need to restart your machine to free them up.

> **Tip:** If you want to delete the patches produced by the pipeline, do so using the provided script in `Utility/scripts/clear_all_patches.sh` (update the paths). **DO NOT** use Finder or File Explorer to delete them, as that will cause the system to _re-index_ all of the files, which can take hours or even days with how many files there are, making your system pretty much unusable during that time. TRUST ME ON THIS ONE!

> **Note:** The fans will turn on during the pipeline execution, this is normal behavior as your CPU/GPU will be under heavy load.

> **Tip:** Download `htop` (Linux/Mac) or use Task Manager (Windows) to monitor your system resources during the pipeline execution, my advice is to leave about half of your cores free to avoid overloading your system. I believe the default configuration uses `os.something_count...() // 2` worker threads, so if you have a 16-core CPU, you should be fine.

### Pipeline Modifications

The pipeline is modular and easy to modify. If you want to make changes, you need to have a solid understanding of how concurrency and multithreading work in Python, how resources are handled in such environments, and mostly importantly, what a pipeline design pattern is. Know that every pipe should have the same input and output format to ensure compatibility and the ability to chain them together.

### XMLParser

The `XMLParser` went unused in the main workflow, but it's in the repo should you guys need it at some point. It is well documented and easy to use. Know that it can only parse the XML files from the Kaggle dataset and convert them into CSV, JSON,... files for easier handling.

### Models

The models should be pretty straightforward to use. Each team member has their own directory with their approach, and inside each, there are subdirectories for single-class and multi-class classification. Each model directory contains the necessary scripts and instructions to train and evaluate the models. The functions are documented to help you understand their purpose and usage. Some of the functions are unused (dead code) but are left there for reference. For some of the approaches, change the paths or remove some of the unnecessary parts to fit your needs (Google Drive cells).

---

Feel free to explore the directories and modify files as needed to suit your analysis and development workflow.

If you have any questions or need further assistance, please don't hesitate to reach out to your professor or us.

**Jakob Balkovec**: jakob.balkovec@gmail.com
**Daniel Kirov-Tomilov**:
**Alyssa Abogado**:
