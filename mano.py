import intern
from intern.remote.boss import BossRemote
import nibabel as nib
import numpy as np
from PIL import Image
import numpy as np
import os
import json
import argparse

"""
    Script to keep track of uploaded annotations.
"""
def main():
    with open(user_file) as f:
        anno_config = json.load(f)
    

    rmt = BossRemote({
        "protocol": anno_config["protocol"],
        "host": anno_config["host"],
        "token": anno_config["token"],
    })

    nii = nib.load(anno_config["file_path"]) 
    data = np.array(nii.dataobj)
    try:
        IMG_COLL_NAME = anno_config["image"]["collection"]
        IMG_EXP_NAME = anno_config["image"]["experiment"]
        IMG_CHAN_NAME = anno_config["image"]["channel"]
        img_chan = rmt.get_channel(IMG_CHAN_NAME, IMG_COLL_NAME, IMG_EXP_NAME)

        ANN_COLL_NAME = anno_config["annotation"]["collection"]
        ANN_EXP_NAME = anno_config["annotation"]["experiment"]
        ANN_CHAN_NAME = anno_config["annotation"]["channel"]
        rmt.create_project(ANN_CHAN_NAME, ANN_COLL_NAME, ANN_EXP_NAME,'image', datatype=anno_config["datatype"]))
    except Exception as e:
        print("Please specify image or annotation collection/experiment/channel for both annotations and raw images in your json file")
        print(e)
        exit(0)

    # Ranges use the Python convention where the second number is the stop
    # value.  Thus, x_rng specifies x values where: 0 <= x < 8.
    x_rng = [anno_config["xmin"], anno_config["xmax"]]
    y_rng = [anno_config["ymin"], anno_config["ymax"]]
    z_rng = [anno_config["zmin"], anno_config["zmax"]]
    res = anno_config["resolution"]

    data = data.copy(order="C")

    # Make data match what was specified for the channel.
    data = data.astype(np.uint64)

    # If specified to download, grab a cutout from boss
    # If specified to upload, upload cutout to the boss for the same dimensions. 
    if args.down:
        download_numpy = rmt.get_cutout(img_chan, res, x_rng, y_rng, z_rng)
        np.save(donwload_numpy)
    if args.up:
        ann_chan = get_channel(ANN_CHAN_NAME, ANN_COLL_NAME, ANN_EXP_NAME)
        rmt.create_cutout(ann_chan, res, x_rng, y_rng, z_rng, data)
    else: 
        print("Please specify either upload(-up) or download(-down) flags")

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description = "Script to upload annotations to the boss",
                                     formatter_class=argparse.RawDescriptionHelpFormatter
                                     )
    parser.add_argument("--filePath", "-fp",
                        metavar = "filePath",
                        required = True,
                        help = "Path to the nii file")
    parser.add_argument("-up",
                    action='store_true',
                    help = "Execute upload")
    parser.add_argument("-down",
                action='store_true',
                help = "Execute download")
    args = parser.parse_args()

    user_file = args.filePath
    main() 