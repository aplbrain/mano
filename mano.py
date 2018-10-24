from intern.resource.boss.resource import *
from intern.remote.boss import BossRemote
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
    
    #Creates boss remote with the correct credentials
    rmt = BossRemote({
        "protocol": anno_config["protocol"],
        "host": anno_config["host"],
        "token": anno_config["token"],
    })

    #Try to get_cahnnel of exisiting raw data and create a new channel for annotations
    try:
        IMG_COLL_NAME = anno_config["image"]["collection"]
        IMG_EXP_NAME = anno_config["image"]["experiment"]
        IMG_CHAN_NAME = anno_config["image"]["channel"]
        img_chan = rmt.get_channel(IMG_CHAN_NAME, IMG_COLL_NAME, IMG_EXP_NAME)

        ANN_COLL_NAME = anno_config["annotation"]["collection"]
        ANN_EXP_NAME = anno_config["annotation"]["experiment"]
        ANN_CHAN_NAME = anno_config["annotation"]["channel"]
        chan_setup = ChannelResource(ANN_CHAN_NAME, ANN_COLL_NAME, ANN_EXP_NAME, type='annotation', description=anno_config["annotation"]["description"], datatype=anno_config["annotation"]["datatype"], sources=[anno_config["image"]["channel"]])

        # Try to create channel, if it already exisits, simply pass
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
        np.save(annos_config["image"]["file_path"], donwload_numpy)
        # If downloading, try to download annotations if they already exist. 
        try:
            download_nifti = rmt.get_cutout(ann_chan, res, x_rng, y_rng, z_rng)
            nifti_img = nib.Nifti1Image(download_nifti, np.eye(4))
            nib.save(nifti_img, anno_config["annotation"]["file_path"])
        except Exception as e:
            print("Annotation does not exist yet!")
            pass
    if args.up:
        nii = nib.load(anno_config["annotation"]["file_path"]) 
        data = np.array(nii.get_data())
        # Data must be in Z, Y, X format
        data = np.swapaxes(data,0,2)

        # Use datatype specified in JSON provided file
        data = data.astype(anno_config["annotation"]["datatype"])
        
        #Upload the data to the annotation channel
        print("Uploading your annotations...")
        rmt.create_cutout(ann_chan, res, x_rng, y_rng, z_rng, data)
    else: 
        print("Please specify either upload(-up) or download(-down) flags")

    # Verify that the cutout uploaded correctly by comparing arrays. 
    ann_cutout_data = rmt.get_cutout(ann_chan, res, x_rng, y_rng, z_rng)
    np.testing.assert_array_equal(data[0,:,:], ann_cutout_data[0,:,:])

    print('Annotation data uploaded and verified.')

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

    #Define filePath for the user provided json file. 
    user_file = args.filePath
    main() 