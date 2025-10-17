# Jakob Balkovec
# Mon Jun 23rd 2025
# DR-Summer Research

# utils.py

# desc: This file contains helper functions

from itertools import chain

def parse_txt_file(filename: str, include_img_path: bool = True):
    # pre:  'filename' is a path to a valid .txt file with image and XML paths
    # post: returns a list of dicts with 'image' and 'xmls' keys
    # desc: Parses a file mapping each image to its associated XML files.

    with open(filename, 'r') as file:
        lines = file.readlines()

    structured_input = []
    for line in lines:
        parts = line.strip().split()
        if not parts or len(parts) < 2:
            continue

        image_path = parts[0] if include_img_path else None
        xml_paths = parts[1:] if include_img_path else parts  # if no image, all are XMLs

        structured_input.append({
            "image": image_path,
            "xmls": xml_paths
        })

    return structured_input
