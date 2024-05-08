# Dense SFM Workstation Setup 
This repository implements a `pixsfm` and `COLMAP` based dense 3D-reconstruction pipeline. 

### Directory Structure

```.
├── dense-reconstruction
│   ├── output
│   └── scripts
├── pipeline-dense-sfm
│   ├── config
│   ├── dense_sfm_output
│   └── svo_output
├── rig-bundle-adjuster
│   ├── output
│   └── scripts
└── sparse-reconstruction
    ├── output
    ├── pixsfm_dataset
    │   ├── left
    │   └── right
    └── scripts
```

### Understanding the config files 

All config files can be found at `pipeline-dense-sfm/config` folder. 

> Recommended to go with the default values used

1. `config.json` file
```
{
  "svo_path": "svo_output/",     # svo folder location relative to pipeline-dense-sfm folder
  "camera_params": [1093.2768, 1093.2768, 964.989,  569.276, 0, 0, 0, 0],   # [fx, fy, cx, cy, k1, k2, k3,k4]    
  "dense_sfm_path":"dense_sfm_output/"   # dense sfm output location relative to pipeline-dense-sfm folder 
}
```

2. `rig.json` file 
```
[
  {
    "ref_camera_id": 1,
    "cameras":
    [
      {
          "camera_id": 1,
          "image_prefix": "left",
          "rel_tvec": [0.13, 0, 0],
          "rel_qvec": [0,0,0,1]
      },
      {
          "camera_id": 2,
          "image_prefix": "right",
          "rel_tvec": [0, 0, 0],
	      "rel_qvec": [0,0,0,1]
      }
    ]
  }
]

```

### How to use? 

```
git clone git@github.com:shubham-monarch/workstation-sfm-setup.git
git checkout dev
cd workstation-sfm-setup
cd pipeline-dense-sfm
```

1. Update the `config/rig.json` with the relative camera poses in the rig 
2. Update the `config/config.json` with svo_path, camera_params and dense_sfm_path (recommended to go with default values)

3. [Important] Copy the target `svo` files at the `svo_output` folder files, defaults to `pipeline-dense-sfm/svo_output/` 
The `svo_output` folder should look like this => 

```
├── frame_0
│   ├── images
│   ├── pointcloud
│   └── pose
└── frame_1
    ├── images
    ├── pointcloud
    └── pose
```

`sbatch run-dense-sfm-pipeline.sh`


