# Project Title

Occupancy Dataset Generator

## Description

Generates frame-wise occupancy-dataset   

## Getting Started

### Dependencies

* COLMAP 
* pycolmap 
* pixSFM
* HLoc


### Installation 

* Setup a `venv` based virtual python environment
```
python3 -m venv env_occ_pipeline
source env_occ_pipeline/bin/activate
```
* Install COLMAP 
```
git clone git@github.com:shubham-monarch/colmap.git
git checkout dev
mkdir build && cd build 
cmake .. -DCMAKE_CUDA_ARCHITECTURES=all -DCMAKE_INSTALL_PREFIX=/usr/local/ -GNinja  
ninja
sudo ninja install 
```
* Install pixSFM
```
sudo apt-get install libhdf5-dev
git clone git@github.com:shubham-monarch/pixel-perfect-sfm.git --recursive
git checkout rig_ba
cd pixel-perfect-sfm
pip install -r requirements.txt
```

* Clone the occupancy-pipeline repo
```
git clone git@github.com:Monarch-Tractor/workstation-sfm-setup.git
```


### Executing the pipeline

* Copy the svo file(s) / folder(s) inside the `input` folder
* Exectute the main.sh file

```
./main.sh
```
### Output
* The output in the desired format is generated at the `output` folder.

### Logging
* Realtime logs are stored at logs/main.log
```
tail -f logs/main.log
```

