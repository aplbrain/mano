from intern.resource.boss.resource import *
from intern.remote.boss import BossRemote
from intern.utils.parallel import block_compute
import nibabel as nib
import numpy as np
from PIL import Image
import numpy as np
import json
import argparse
from requests import HTTPError

"""
    Script to keep track of uploaded annotations.

    Luis.Rodriguez@jhuapl.edu
"""
def main():
    with open(user_file) as f:
        anno_config = json.load(f)

    # Create boss remote with the correct credentials
    rmt = BossRemote({
        "protocol": anno_config["protocol"],
        "host": anno_config["host"],
        "token": anno_config["token"],
    })

    # Try to get_channel of existing raw data and create a new channel for annotations
    try:
        IMG_COLL_NAME = anno_config["image"]["collection"]
        IMG_EXP_NAME = anno_config["image"]["experiment"]
        IMG_CHAN_NAME = anno_config["image"]["channel"]
        img_chan = rmt.get_channel(IMG_CHAN_NAME, IMG_COLL_NAME, IMG_EXP_NAME)

        ANN_COLL_NAME = anno_config["annotation"]["collection"]
        ANN_EXP_NAME = anno_config["annotation"]["experiment"]
        ANN_CHAN_NAME = anno_config["annotation"]["channel"]
        chan_setup = ChannelResource(ANN_CHAN_NAME, ANN_COLL_NAME, ANN_EXP_NAME, type='annotation', datatype=anno_config["annotation"]["datatype"], sources=[anno_config["image"]["channel"]])

        # Try to create channel, if it already exists, simply pass
        try:
            ann_chan = rmt.create_project(chan_setup)
        except Exception as e:
            ann_chan = rmt.get_channel(ANN_CHAN_NAME, ANN_COLL_NAME, ANN_EXP_NAME)
            pass
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

    # If specified to download, grab a cutout from boss
    # If specified to upload, upload cutout to the boss for the same dimensions.
    if args.down:
        download_numpy = rmt.get_cutout(img_chan, res, x_rng, y_rng, z_rng)
        np.save(anno_config["image"]["file_path"], download_numpy)
        # If downloading, try to download annotations if they already exist.
        try:
            download_nifti = rmt.get_cutout(ann_chan, res, x_rng, y_rng, z_rng)
            nifti_img = nib.Nifti1Image(download_nifti, np.eye(4))
            nifti_img.to_filename(anno_config["annotation"]["file_path"])
            nib.save(nifti_img, anno_config["annotation"]["file_path"])
        except Exception as e:
            print("Annotation does not exist yet!")
            pass
        print("Download Successful!")
    elif args.up:
        if anno_config["annotation"]["extension"] == "npy":
            data = np.load(anno_config["annotation"]["file_path"])
        elif anno_config["annotation"]["extension"] == "nii":
            nii = nib.load(anno_config["annotation"]["file_path"])
            data = np.array(nii.get_data())

        # Handle single image uploads
        # Assume image is single (x, y)-ordered z-slice
        if len(data.shape) == 2:
            data = np.expand_dims(data, axis=-1)

        # Data must be in (Z, Y, X) order
        # Transpose accordingly
        data = data.transpose((2, 1, 0))

        # Use datatype specified in JSON provided file
        data = data.astype(anno_config["annotation"]["datatype"])

        # Maximum byte count before blosc fails is 2147483631
        # partition into 512x512x512 cubes accordingly
        block_bounds = block_compute(
                x_start=x_rng[0],
                x_stop=x_rng[1],
                y_start=y_rng[0],
                y_stop=y_rng[1],
                z_start=z_rng[0],
                z_stop=z_rng[1],
                block_size=(512, 512, 512))

        # Upload the data to the annotation channel
        print("Uploading your annotations...")
        for (x_bounds, y_bounds, z_bounds) in block_bounds:
            # Compute array indices by accounting for global origin
            x_array = [x_bounds[0] - x_rng[0], x_bounds[1] - x_rng[0]]
            y_array = [y_bounds[0] - y_rng[0], y_bounds[1] - y_rng[0]]
            z_array = [z_bounds[0] - z_rng[0], z_bounds[1] - z_rng[0]]
            subset = data[
                z_array[0]:z_array[1],
                y_array[0]:y_array[1],
                x_array[0]:x_array[1]]
            # Guarantee C-contiguous array ordering
            subset = subset.copy(order="C")
            rmt.create_cutout(
                    ann_chan,
                    res,
                    x_bounds,
                    y_bounds,
                    z_bounds,
                    subset)

        # Verify that the cutout uploaded correctly by comparing arrays
        ann_cutout_data = rmt.get_cutout(ann_chan, res, x_rng, y_rng, z_rng)
        np.testing.assert_array_equal(data[0,:,:], ann_cutout_data[0,:,:])

        print('Annotation data uploaded and verified.')

    else:
        print("Please specify either upload(-up) or download(-down) flags")

if __name__ == '__main__':

    # Parser arguments:
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

    # Define filePath for the user provided json file.
    user_file = args.filePath
    main()
