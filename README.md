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

1. `config.json` file
```
{
  "svo_filename": "front_2024-02-13-07-52-14.svo",
  "svo_start_percentage": 193,
  "svo_end_percentage": 338,
  "dense_sfm_path":"front_2024-02-13-07-52-14"
}


> All the paths mentioned in `config.json` would be relative to the `pipeline-dense-sfm` folder

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

- Put the `svo` file inside `pipeline-dense-sfm/input/` folder
- Update `pipeline-dense-sfm/config/rig.json`
- Update `pipeline-dense-sfm/config/config.json`
  - `svo_filename`: name of the svo file inside `pipeline-dense-sfm/input` folder
  - `svo_start_percentage`: svo % start point
  - `svo_end_percentage`: svo % end point
  - `dense_sfm_path`: folder containng the dense reconstruction output


Activate the python virtual environment and execute the main script => ss
```
source ../e33/bin/activate
sbatch run-dense-sfm-pipeline.sh
```


> Running with the default configuration would generate the dense sfm output at the `pipeline-dense-sfm/dense_sfm_output/` folder

### Some Helpful SLURM commands

```
squeue => see the current SLURM queue
tail -f slurm-<id>.out => see the <id>.out file in real time
scancel <id> => cancel id
```
