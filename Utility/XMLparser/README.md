Jakob Balkovec, Mon Jun 23 2025

## Lesion Parser

This notebook demo-es all the features of the `LesionXMLParser` implementation. Feel free to build on top of it, or change/tailor some functionality to fit your use case.

```python
import sys
import os

notebook_dir = os.getcwd()
parent_dir = os.path.abspath(os.path.join(notebook_dir, ".."))
sys.path.append(parent_dir)

```

```python
from lesion_parser import LesionXMLParser
import json
from utils import parse_txt_file
from config import VALID_LESION_TYPES

```

> The `parse_txt_file` function can be found in `XMLparser/utils.py`.

> The `VALID_LESION_TYPES` constant is defined in `XMLparser/config.py`.

## Initializing the Parser With a Single File

```python
single_file_parser = LesionXMLParser(["groundtruth/diaretdb1_image001_01_plain.xml"], root_dir="../data")
single_file_parser.parse()[:2]

```

    [{'image_path': None,
      'image_id': None,
      'xml_file': 'diaretdb1_image001_01_plain.xml',
      'type': 'Hard_exudates',
      'x': 713.0,
      'y': 532.0,
      'radius': 141.0},
     {'image_path': None,
      'image_id': None,
      'xml_file': 'diaretdb1_image001_01_plain.xml',
      'type': 'Haemorrhages',
      'x': 493.0,
      'y': 647.0,
      'radius': 5.0}]

I designed the constructor to accept either a list of XML file paths or a list of dictionaries where each entry maps an image to its corresponding XML files. I think this is the cleanest and most flexible approach, but I’m open to suggestions if you see a better way.

#### Supported Input Formats:

**List of XML paths:**

```python
["groundtruth/file1.xml", "groundtruth/file2.xml", ...]
```

**List of dictionaries (image + associated XMLs):**

```python
[
  {
    "image": "images/image001.png",
    "xmls": [
      "groundtruth/image001_01.xml",
      "groundtruth/image001_02.xml"
    ]
  },
  ...
]
```

> This makes it a little awkward when passing in a **single** file, since it has to be a `list` or `dict` of one item...

You’ll see later why I went with this approach, the idea was to allow passing in all the XML files up front, parse everything in one go, and then export the results as a container like a `pandas.DataFrame` or `numpy` array. This way, you can immediately take advantage of built-in functionality for filtering, sorting, and other operations without extra steps...

## Initalizing the Parser With a List of Files

```python
list_of_files = ["groundtruth/diaretdb1_image001_01_plain.xml",
                 "groundtruth/diaretdb1_image001_02_plain.xml",
                 "groundtruth/diaretdb1_image001_03_plain.xml",
                 "groundtruth/diaretdb1_image001_04_plain.xml"]

list_of_files_parser = LesionXMLParser(list_of_files, root_dir="../data")
list_of_files_parser.parse()[2:4]

```

    [{'image_path': None,
      'image_id': None,
      'xml_file': 'diaretdb1_image001_01_plain.xml',
      'type': 'Haemorrhages',
      'x': 978.0,
      'y': 354.0,
      'radius': 5.0},
     {'image_path': None,
      'image_id': None,
      'xml_file': 'diaretdb1_image001_01_plain.xml',
      'type': 'Haemorrhages',
      'x': 618.0,
      'y': 94.0,
      'radius': 5.0}]

Same thing as before, but now we pass in a list of XML files. This (alongside the `dict` "mode"), I think will is the most common use case. Here we pass in a list of all XML file associated with `diaretdb1_image001.png`. I clipped the output for brevity.

## Initializing the Parser With a Dictionary

```python
data_txt = r"../data/ddb1_v02_01_test_plain.txt"
parsed_text_input = parse_txt_file(data_txt)

print(json.dumps(parsed_text_input[:2], indent=2))

```

    [
      {
        "image": "images/diaretdb1_image002.png",
        "xmls": [
          "groundtruth/diaretdb1_image002_01_plain.xml",
          "groundtruth/diaretdb1_image002_02_plain.xml",
          "groundtruth/diaretdb1_image002_03_plain.xml",
          "groundtruth/diaretdb1_image002_04_plain.xml"
        ]
      },
      {
        "image": "images/diaretdb1_image005.png",
        "xmls": [
          "groundtruth/diaretdb1_image005_01_plain.xml",
          "groundtruth/diaretdb1_image005_02_plain.xml",
          "groundtruth/diaretdb1_image005_03_plain.xml",
          "groundtruth/diaretdb1_image005_04_plain.xml"
        ]
      }
    ]

> Note: The `"image"` field is pulled from the input, not the actual image file. For example:

      "xml path": groundtruth/diaretdb1_image005_01_plain.xml",
        -> "image": "diaretdb1_image005.png"

```python
dict_parser = LesionXMLParser(xml_input=parsed_text_input, root_dir="../data")
parsed = dict_parser.parse()
parsed[:2]

```

    [{'image_path': 'images/diaretdb1_image002.png',
      'image_id': 'diaretdb1_image002',
      'xml_file': 'diaretdb1_image002_01_plain.xml',
      'type': 'Haemorrhages',
      'x': 570.0,
      'y': 805.0,
      'radius': 16.0},
     {'image_path': 'images/diaretdb1_image002.png',
      'image_id': 'diaretdb1_image002',
      'xml_file': 'diaretdb1_image002_01_plain.xml',
      'type': 'Haemorrhages',
      'x': 669.0,
      'y': 685.0,
      'radius': 20.0}]

Again, same thing as before, only now, we're initializing the `LesionXMLParser` with a dictionary. Note that the dictionary was obtained from the `parse_txt_file` function, which reads a text file containing the image and XML paths.

**As shown above:**

```python
{
  "image": "diaretdb1_image005.png",
  "xmls": [
    "groundtruth/diaretdb1_image005_01_plain.xml",
    "groundtruth/diaretdb1_image005_02_plain.xml"
  ]
}
```

## Formatting the Output

As mentioned above, the parser is designed to return 4 types of output:

- Pandas DataFrame
- Numpy array
- JSON
- Dictionary
- Raw python list (if `.to_format()` is never invoked)

### Pandas DataFrame

```python
pandas_df = dict_parser.to_format("pandas")
pandas_df.head()

```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>image_path</th>
      <th>image_id</th>
      <th>xml_file</th>
      <th>type</th>
      <th>x</th>
      <th>y</th>
      <th>radius</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>images/diaretdb1_image002.png</td>
      <td>diaretdb1_image002</td>
      <td>diaretdb1_image002_01_plain.xml</td>
      <td>Haemorrhages</td>
      <td>570.0</td>
      <td>805.0</td>
      <td>16.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>images/diaretdb1_image002.png</td>
      <td>diaretdb1_image002</td>
      <td>diaretdb1_image002_01_plain.xml</td>
      <td>Haemorrhages</td>
      <td>669.0</td>
      <td>685.0</td>
      <td>20.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>images/diaretdb1_image002.png</td>
      <td>diaretdb1_image002</td>
      <td>diaretdb1_image002_01_plain.xml</td>
      <td>Haemorrhages</td>
      <td>811.0</td>
      <td>733.0</td>
      <td>48.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>images/diaretdb1_image002.png</td>
      <td>diaretdb1_image002</td>
      <td>diaretdb1_image002_01_plain.xml</td>
      <td>Haemorrhages</td>
      <td>895.0</td>
      <td>700.0</td>
      <td>5.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>images/diaretdb1_image002.png</td>
      <td>diaretdb1_image002</td>
      <td>diaretdb1_image002_01_plain.xml</td>
      <td>Haemorrhages</td>
      <td>1054.0</td>
      <td>716.0</td>
      <td>5.0</td>
    </tr>
  </tbody>
</table>
</div>

### CSV String

```python
csv_string = dict_parser.to_format("csv")
print(csv_string[:488])  # 488 works out to 4 entries + labels

```

    image_path,image_id,xml_file,type,x,y,radius
    images/diaretdb1_image002.png,diaretdb1_image002,diaretdb1_image002_01_plain.xml,Haemorrhages,570.0,805.0,16.0
    images/diaretdb1_image002.png,diaretdb1_image002,diaretdb1_image002_01_plain.xml,Haemorrhages,669.0,685.0,20.0
    images/diaretdb1_image002.png,diaretdb1_image002,diaretdb1_image002_01_plain.xml,Haemorrhages,811.0,733.0,48.0
    images/diaretdb1_image002.png,diaretdb1_image002,diaretdb1_image002_01_plain.xml,Haemorrhages,895.0,700.0,5.0

### JSON String

```python
json_string = dict_parser.to_format("json")
print(json_string[:460]) # 460 works out to 2 entries

```

    [
      {
        "image_path": "images/diaretdb1_image002.png",
        "image_id": "diaretdb1_image002",
        "xml_file": "diaretdb1_image002_01_plain.xml",
        "type": "Haemorrhages",
        "x": 570.0,
        "y": 805.0,
        "radius": 16.0
      },
      {
        "image_path": "images/diaretdb1_image002.png",
        "image_id": "diaretdb1_image002",
        "xml_file": "diaretdb1_image002_01_plain.xml",
        "type": "Haemorrhages",
        "x": 669.0,
        "y": 685.0,
        "radius": 20.0
      },

### Numpy Array

```python
numpy_array = dict_parser.to_format("numpy")
print(numpy_array[:2])

```

    [['images/diaretdb1_image002.png' 'diaretdb1_image002'
      'diaretdb1_image002_01_plain.xml' 'Haemorrhages' 570.0 805.0 16.0]
     ['images/diaretdb1_image002.png' 'diaretdb1_image002'
      'diaretdb1_image002_01_plain.xml' 'Haemorrhages' 669.0 685.0 20.0]]

## Saving the Output

The parser can save the output in various formats, including:

- CSV
- JSON
- Numpy array
- Pickle
- Text file

> Note: You have to specify the location as well as the format when saving the output. The default format is CSV, but you can change it by passing the `format` argument to the `save` method. As far as location goes, you have to specify the full path, and create a directory if you wish to save all of the files in one place. **Nothing is done under the hood**. This could be a potential improvement, but I wanted to keep it simple for now...

```python
dict_parser.save_as("parsed/lesions.txt", "txt")
dict_parser.save_as("parsed/lesions.csv", "csv")
dict_parser.save_as("parsed/lesions.json", "json")
dict_parser.save_as("parsed/lesions.pkl", "pandas")
dict_parser.save_as("parsed/lesions.npy", "numpy")

```

    Saved parsed data as txt to: parsed/lesions.txt
    Saved parsed data as csv to: parsed/lesions.csv
    Saved parsed data as json to: parsed/lesions.json
    Saved parsed data as pandas to: parsed/lesions.pkl
    Saved parsed data as numpy to: parsed/lesions.npy

## Filtering

```python
print("Valid types:", VALID_LESION_TYPES)
dict_parser.filter_by_type("IRMA")
dict_parser.to_format("pandas").head()

```

    Valid types: ['Red_small_dots', 'Soft_exudates', 'Disc', 'Neovascularisation', 'Fundus_area', 'Hard_exudates', 'Haemorrhages', 'IRMA']
    Filtered parsed data to 30 entries with types: ['IRMA']

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>image_path</th>
      <th>image_id</th>
      <th>xml_file</th>
      <th>type</th>
      <th>x</th>
      <th>y</th>
      <th>radius</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>images/diaretdb1_image007.png</td>
      <td>diaretdb1_image007</td>
      <td>diaretdb1_image007_01_plain.xml</td>
      <td>IRMA</td>
      <td>513.0</td>
      <td>795.0</td>
      <td>86.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>images/diaretdb1_image007.png</td>
      <td>diaretdb1_image007</td>
      <td>diaretdb1_image007_01_plain.xml</td>
      <td>IRMA</td>
      <td>1076.0</td>
      <td>103.0</td>
      <td>43.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>images/diaretdb1_image007.png</td>
      <td>diaretdb1_image007</td>
      <td>diaretdb1_image007_01_plain.xml</td>
      <td>IRMA</td>
      <td>827.0</td>
      <td>528.0</td>
      <td>28.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>images/diaretdb1_image007.png</td>
      <td>diaretdb1_image007</td>
      <td>diaretdb1_image007_02_plain.xml</td>
      <td>IRMA</td>
      <td>494.0</td>
      <td>787.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>images/diaretdb1_image007.png</td>
      <td>diaretdb1_image007</td>
      <td>diaretdb1_image007_02_plain.xml</td>
      <td>IRMA</td>
      <td>204.0</td>
      <td>249.0</td>
      <td>59.0</td>
    </tr>
  </tbody>
</table>
</div>

The parser provides some basic filtering for types of lesions, which can be useful for quickly narrowing down the results. I kept this super simple for now, as I imagine most of us will be using built in functions (pandas, numpy, etc.) to filter the results anyway...

## Caching

The parser does some intermediate caching to avoid redundant calls to functions. This wasn't originally planned, but I thought it could be useful for larger datasets. The cache is stored in a dictionary, and you shouldn't access, but if you really need to, you can access it via the `_format_cache` attribute. You can also clear the cache using the `clear` method.

```python
dict_parser.clear()

```

    Cleared parsed data and format cache.

## Using Pandas

```python
import pandas as pd
# pandas_df from earlier

# filter for haemorrhages
haemorrhages = pandas_df[pandas_df['type'] == 'Haemorrhages']
print(haemorrhages.head())

```

                          image_path            image_id  \
    0  images/diaretdb1_image002.png  diaretdb1_image002
    1  images/diaretdb1_image002.png  diaretdb1_image002
    2  images/diaretdb1_image002.png  diaretdb1_image002
    3  images/diaretdb1_image002.png  diaretdb1_image002
    4  images/diaretdb1_image002.png  diaretdb1_image002

                              xml_file          type       x      y  radius
    0  diaretdb1_image002_01_plain.xml  Haemorrhages   570.0  805.0    16.0
    1  diaretdb1_image002_01_plain.xml  Haemorrhages   669.0  685.0    20.0
    2  diaretdb1_image002_01_plain.xml  Haemorrhages   811.0  733.0    48.0
    3  diaretdb1_image002_01_plain.xml  Haemorrhages   895.0  700.0     5.0
    4  diaretdb1_image002_01_plain.xml  Haemorrhages  1054.0  716.0     5.0

```python
# number of lesions per image
lesions_per_image = pandas_df.groupby('image_id').size().sort_values(ascending=False)
print(lesions_per_image.head())

```

    image_id
    diaretdb1_image021    307
    diaretdb1_image019    264
    diaretdb1_image015    238
    diaretdb1_image016    228
    diaretdb1_image067    216
    dtype: int64

```python
# average lesion radius per type
avg_radius = pandas_df.groupby('type')['radius'].mean()
print(avg_radius.sort_values(ascending=False))

```

    type
    Disc                  106.964539
    Fundus_area            74.500000
    Neovascularisation     72.500000
    IRMA                   47.318182
    Hard_exudates          41.068376
    Soft_exudates          37.464789
    Haemorrhages           29.462158
    Red_small_dots          9.653253
    Name: radius, dtype: float64

## Using Numpy

```python
import numpy as np

# numpy_array from earlier

xs = np.array([float(x) for x in numpy_array[:, 4]])
ys = np.array([float(y) for y in numpy_array[:, 5]])

# filter entries within a box
mask = (xs > 500) & (ys < 1000)
filtered = numpy_array[mask]

print(filtered[:5])

```

    [['images/diaretdb1_image002.png' 'diaretdb1_image002'
      'diaretdb1_image002_01_plain.xml' 'Haemorrhages' 570.0 805.0 16.0]
     ['images/diaretdb1_image002.png' 'diaretdb1_image002'
      'diaretdb1_image002_01_plain.xml' 'Haemorrhages' 669.0 685.0 20.0]
     ['images/diaretdb1_image002.png' 'diaretdb1_image002'
      'diaretdb1_image002_01_plain.xml' 'Haemorrhages' 811.0 733.0 48.0]
     ['images/diaretdb1_image002.png' 'diaretdb1_image002'
      'diaretdb1_image002_01_plain.xml' 'Haemorrhages' 895.0 700.0 5.0]
     ['images/diaretdb1_image002.png' 'diaretdb1_image002'
      'diaretdb1_image002_01_plain.xml' 'Haemorrhages' 1054.0 716.0 5.0]]

```python
radii = np.array([float(r) if r is not None else np.nan for r in numpy_array[:, 6]])

# compute stats
mean_radius = np.nanmean(radii)
std_radius = np.nanstd(radii)
print(f"Mean radius: {mean_radius:.2f}, Std: {std_radius:.2f}")

```

    Mean radius: 25.81, Std: 34.93
