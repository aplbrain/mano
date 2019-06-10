from zmesh import Mesher
import numpy as np
from intern.remote.boss import BossRemote
import tqdm

"""
    Script to keep track of uploaded annotations.

    Luis.Rodriguez@jhuapl.edu
"""
def main(args):
    with open(user_file) as f:
        anno_config = json.load(f)

    # Create boss remote with the correct credentials
    rmt = BossRemote({
        "protocol": anno_config["protocol"],
        "host": anno_config["host"],
        "token": anno_config["token"],
    })

    ANN_COLL_NAME = anno_config["annotation"]["collection"]
    ANN_EXP_NAME = anno_config["annotation"]["experiment"]
    ANN_CHAN_NAME = anno_config["annotation"]["channel"]

    x_rng = [anno_config["xmin"], anno_config["xmax"]]
    y_rng = [anno_config["ymin"], anno_config["ymax"]]
    z_rng = [anno_config["zmin"], anno_config["zmax"]]
    res = anno_config["resolution"]

    #Get coordinate frame
    experiment = rmt.get_experiment(ANN_COLL_NAME, ANN_EXP_NAME)
    coordinate_frame = experiment.coord_frame
    cf = rmt.get_coordinate_frame(coordinate_frame)

    # If not unit is provided fetch from boss
    if args.units == None:
        args.units = cf.voxel_unit
    
    # Get voxel size unit to set conversion factor
    if args.units == "nanometers":
        conv_factor = 1
    elif args.units == "micrometers":
        conv_factor = 1000
    elif args.units == "millimeters":
        conv_factor = 1000000
    elif args.units == "centimeters":
        conv_factor = 10000000
    else:
        raise Exception("Something went wrong fetching your voxel units... try passing unit types using --unit")

    # Get voxel_sizes
    x_voxel_size = float(cf.x_voxel_size) * conv_factor
    y_voxel_size = float(cf.y_voxel_size) * conv_factor
    z_voxel_size = float(cf.z_voxel_size) * conv_factor

    # Get annotation data from boss:
    ann_chan = rmt.get_channel(ANN_CHAN_NAME, ANN_COLL_NAME, ANN_EXP_NAME)
    boss_data - boss.get_cutout(ann_chan, res, x_rng, y_rng, z_rng)

    # Mesh
    mesher = Mesher((x_voxel_size,y_voxel_size,z_voxel_size))
    mesher.mesh(boss_data)

    for oid in tqdm.tqdm(mesher.ids()):
        mesh = mesher.get_mesh(oid, normals=False)
        mesh.vertices += [x_rng[0]*conv_factor, y_rng[0]*conv_factor, z_rng[0]*conv_factor]
        with open("precompmeshes/{oid}", 'wb') as fh:
            fh.write(mesh.to_precomputed())

    # TODO - LMR - Add a way to push back to the boss through an API call OR the public bucket. Probably want to go with API version long term. 

if __name__ == '__main__':

    # Parser arguments:
    parser = argparse.ArgumentParser(description = "Script to upload annotations to the boss",
                                     formatter_class=argparse.RawDescriptionHelpFormatter
                                     )
    parser.add_argument("--filePath", "-fp",
                        metavar = "filePath",
                        required = True,
                        help = "Path to the nii file")
    parser.add_argument("--units", "-u",
                        metavar = "unit_type",
                        default = None,
                        required = True,
                        help = "The unit type of your coordinate frame (nanometers, millimeters etc)")
    args = parser.parse_args()

    # Define filePath for the user provided json file.
    user_file = args.filePath
    main(args)
