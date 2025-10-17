# Jakob Balkovec
# Mon Jun 23rd 2025
# DR-Summer Research

# lesion_parser.py

# desc: This file defines the XML Parser

import os
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import json

import threading

from config import VALID_LESION_TYPES

class LesionXMLParser:
    # init: accepts XML file(s) directly or as part of a structured list with optional image associations.

    def __init__(self, xml_input, root_dir=None):
        # pre:  xml_input is either:
        #         - a single .xml filepath (string)
        #         - a list of .xml filepaths (list of str)
        #         - a list of dictionaries with keys: {"image": <str or None>, "xmls": <list of str>}
        #       root_dir is an optional base path used to resolve relative file paths
        #
        # post: Initializes the parser with normalized internal structure and empty cache/data containers
        #
        # desc: Validates and standardizes the input structure, ensuring consistent downstream parsing.
        #       Prepares class attributes needed for parsing and exporting lesion annotation data.

        if isinstance(xml_input, str):
            if not xml_input.endswith(".xml"):
                raise ValueError("String input must be an .xml file path")
            self.xml_input = [{"image": None, "xmls": [xml_input]}]

        elif isinstance(xml_input, list):
            if not xml_input:
                raise ValueError("Input list is empty")

            if all(isinstance(x, str) and x.endswith(".xml") for x in xml_input):
                self.xml_input = [{"image": None, "xmls": xml_input}]

            elif all(isinstance(x, dict) and "xmls" in x for x in xml_input):
                self.xml_input = xml_input

            else:
                raise ValueError("Input list must contain either .xml strings or dicts with 'xmls' key")

        else:
            raise ValueError("xml_input must be a string, list of strings, or list of dicts")

        self.xml_input = xml_input
        self.root_dir = root_dir
        self.parsed_data = []
        self._format_cache = {}
        self.parsed_object = None
        self.lock = threading.Lock()
        self.lesion_counter = 0


    def _resolve_path(self, path):
        # pre:  path is a string representing a file path (relative or absolute)
        # post: returns an absolute path if the file exists, else None
        # desc: attempts to resolve a file path using either the given path or root_dir as a base directory

        if os.path.isfile(path):
            return path
        if self.root_dir:
            full = os.path.join(self.root_dir, path)
            if os.path.isfile(full):
                return full
        return None


    def parse(self, mode="overwrite", mute_output=True):
        # pre:  xml_input is a valid list of .xml paths or dicts; files are accessible from root_dir or absolute paths
        # post: parsed_data is populated with extracted lesion entries, cache is cleared, optionally appends
        # desc: parses all provided XML files and extracts lesion metadata. Supports appending or overwriting previous results.
        with self.lock:
            if mode == "overwrite":
                self.parsed_data = []
            elif mode != "append":
                raise ValueError("Invalid mode. Use 'overwrite' or 'append'.")

            self._format_cache.clear()

            for entry in self.xml_input:
                image_path = entry.get("image")
                for xml_rel in entry["xmls"]:
                    xml_path = self._resolve_path(xml_rel)
                    if not xml_path:
                        print(f"File not found: {xml_rel}")
                        continue

                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        image_id = os.path.splitext(os.path.basename(image_path))[0] if image_path else None
                        xml_name = os.path.basename(xml_path)

                        # note: updated due to different types of regions
                        #   circleregion
                        #   polygonregion
                        #   elipsisregion

                        for mark in root.findall(".//marking"):
                            coords_text = mark.find(".//centroid/coords2d").text
                            x, y = map(float, coords_text.split(","))
                            region = None

                            for child in mark:
                                if child.tag.endswith("region"):
                                    region = child
                                    break

                            if region is None:
                                if mute_output == False:
                                    print("INFO: region is None")
                                else:
                                    continue

                            radius = radius_x = radius_y = angle = None
                            polygon_points = []

                            if region.tag == "circleregion":
                                radius_elem = region.find("radius")
                                if radius_elem is not None:
                                    radius = float(radius_elem.text)
                                    # radius_x = radius_y = radius
                                    # angle = 0.0

                            elif region.tag == "ellipseregion":
                                rx_elem = region.find("radius[@direction='x']")
                                ry_elem = region.find("radius[@direction='y']")
                                angle_elem = region.find("angle")
                                if rx_elem is not None and ry_elem is not None:
                                    radius_x = float(rx_elem.text)
                                    radius_y = float(ry_elem.text)
                                    radius = (radius_x + radius_y) / 2
                                    angle = float(angle_elem.text) if angle_elem is not None else 0.0

                            elif region.tag == "polygonregion":
                                centroid_text = region.find("centroid/coords2d").text
                                cx, cy = map(float, centroid_text.split(","))
                                radius = 0
                                polygon_points = []

                                for pt in region.findall("coords2d"):
                                    px, py = map(float, pt.text.split(","))
                                    polygon_points.append((px, py))
                                    dist = ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5
                                    radius = max(radius, dist)
                                # radius_x = radius_y = radius
                                # angle = 0.0

                            lesion_type = mark.find("markingtype").text

                            self.parsed_data.append({
                                "image_path": image_path,
                                "image_id": image_id,
                                "xml_file": xml_name,
                                "type": lesion_type,
                                "lesion_id": self.lesion_counter,
                                "x": x,
                                "y": y,
                                "radius": radius,
                                "radius_x": radius_x,
                                "radius_y": radius_y,
                                "angle": angle,
                                "polygon_points": polygon_points,
                                "region_type": region.tag
                            })
                            self.lesion_counter += 1

                    except Exception as e:
                        print(f"Skipping {xml_rel} due to error: {e}")

            return self.parsed_data


    def to_format(self, format="pandas"):
        # pre:  parser has been run with parse(), and parsed_data is available
        # post: returns parsed data in the specified format (with caching)
        # desc: converts the parsed data into one of the supported formats (pandas, csv, numpy, json)
        with self.lock:
            if not self.parsed_data:
                raise ValueError("No parsed data. Run parse() first.")

            format = format.lower()
            if format in self._format_cache:
                return self._format_cache[format]

            if format == "pandas":
                parsed_object = pd.DataFrame(self.parsed_data)
            elif format == "csv":
                df = pd.DataFrame(self.parsed_data)
                parsed_object = df.to_csv(index=False)
            elif format == "numpy":
                df = pd.DataFrame(self.parsed_data)
                parsed_object = df.to_numpy()
            elif format == "json":
                parsed_object = json.dumps(self.parsed_data, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")

            self._format_cache[format] = parsed_object
            return parsed_object


    def save_as(self, filename, format="csv"):
        # pre:  parser has been run with parse(), and parsed_data is available
        # post: writes parsed data to a file in the specified format
        # desc: saves the current parsed dataset to disk using one of the supported formats
        # note: locking handled in "to_format" method

        if not self.parsed_data:
            raise ValueError("No parsed data. Run parse() first.")

        format = format.lower()

        if format == "csv":
            parsed_object = self.to_format("csv")
            with open(filename, "w") as f:
                f.write(parsed_object)

        elif format == "txt":
            with open(filename, "w") as f:
                for entry in self.parsed_data:
                    line = f"{entry['image_path'] or ''} {entry['xml_file']} {entry['type']} {entry['x']} {entry['y']} {entry['radius']}\n"
                    f.write(line)

        elif format == "json":
            parsed_object = self.to_format("json")
            with open(filename, "w") as f:
                f.write(parsed_object)

        elif format == "pandas":
            df = self.to_format("pandas")
            df.to_pickle(filename) if filename.endswith(".pkl") else df.to_csv(filename, index=False)

        elif format == "numpy":
            arr = self.to_format("numpy")
            np.save(filename, arr)

        else:
            raise ValueError(f"Unsupported format for saving: {format}")

        print(f"Saved parsed data as {format} to: {filename}")


    def clear(self):
        # pre:  parser has previously loaded or filtered data
        # post: clears all parsed data and cached formats
        # desc: resets the parser to its initial state by clearing stored data and cached conversions

        with self.lock:
            self.parsed_data = []
            self._format_cache.clear()
            print("Cleared parsed data and format cache.")


    def filter_by_type(self, lesion_types):
        # pre:  'lesion_types' is a string or list of valid lesion type(s)
        # post: updates and returns parsed data filtered by specified type(s)
        # desc: filters the parsed lesion data to include only selected lesion types

        with self.lock:
            if lesion_types not in VALID_LESION_TYPES:
                raise ValueError(f"Invalid lesion type(s): {lesion_types}. Valid types are: {VALID_LESION_TYPES}")

            if not self.parsed_data:
                raise ValueError("No parsed data. Run parse() first.")

            if isinstance(lesion_types, str):
                lesion_types = [lesion_types]

            filtered = [
                entry for entry in self.parsed_data
                if entry["type"] in lesion_types
            ]

            self.parsed_data = filtered
            self._format_cache.clear()

            print(f"Filtered parsed data to {len(filtered)} entries with types: {lesion_types}")
            return self.parsed_data
