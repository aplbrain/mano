## Manual Annotation Protocol
 
Many neurocartography applications require manual annotations to train machine learning algorithms and explore datasets.  Here we describe a protocol for uploading annotations using ITK Snap. 

### Overall Steps

- Create a JSON file specifying how to upload data following the example below. 
- Download data by running `python3 mano.py -fp /path/to/json/file -d`
- Annotate by loading in your data to ITK Snap
- Modify your JSON file by inserting the annotation_channel location
- To upload data run `python3 mano.py -fp /path/to/json/file -u`

### File name convention

<to insert> 

### Annotation channel naming convention

For provenance and reproducibility, we recommend the following annotation channel naming convention:

<user>_<format>_<class>_<type>_<initials>

- user: {manual, automated}
- format: {sparse, dense, centroid, skeleton}
- class: {pixel, object}
- type: {a: axon, b: blood vessel, c: cell, d: dendrite, r: region of interest
- initials: {user initials, automated algorithm}

Example:

`manual_dense_pixel_abc_wrgr`

### LIMS 

We recommend maintaining a searchable database of projects with info


### Starter JSON file

Please replace `<value>` with your values (remove the `<>` as well) 
```
{
    "protocol": "https", 
    "host": "api.bossdb.org",
    "token": "<string>",
    "file_path": "<string>",
    "image": {
        "collection": "<string>",
        "experiment": "<string>",
        "channel": "<string>",
        "datatype": "<string>"
    },
    
    "annotation": {
        "collection": "<string>",
        "experiment": "<string>",
        "channel": "<string>",
        "datatype": "<string>",
        "description": "<string>"
    },
    
    "xmin": <number>,
    "ymin": <number>,
    "zmin": <number>,
    "xmax": <number>,
    "ymax": <number>,
    "zmax": <number>,
    "resolution": <number>
}
```
