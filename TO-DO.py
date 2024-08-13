# - aws api integration
# - aws / local input detection

# - output-backend -> output folder
# - aws instance setup
# 	- add colmap cmake update to s pycolmap installtion 
# 	- retag colmap , pycolmap
# 	- update requirements.txt
# 	- update pipeline tag
# - processed/unprocessed folders
# 	- add svo files
# 	- cleanup before running the pipelines
# - documentation
# 	- update release notes
# 	- update installation steps
# 	- add + update setup.mds
# 	- add readme.md
# 	- update colmap installation steps in setup.md
# - add segmentation inference script

# - check if script is being executed from the project root
# - dense reconstruction support for multiple gpus
# - [error-handling / folder deletion] for Ctrl-C / unexpected script termination 
# - update default bb params for pointcloud cropping
# - return -1 for failed jsons
# - add colmap cmake update to support pycolmap installtion 
# - retag colmap , pycolmap
# - update COLMAP tags with pycolmap bindings integration
# - update requirements.txt
# - update pipeline tag
# - cleanup for all the modules
# - aws integration 
# - add main-ws.sh, main-aws.sh
# - aws integration
# - move all files inside input to a folder
# - add status-processed / unprocessed folders for user feeback
# - move output-backend ---> output script
# - output/input-backend clean-up
# - add images  support
# - check if script is being executed from the project root
# - dense reconstruction support for multiple gpus
# - [error-handling / folder deletion] for Ctrl-C / unexpected script termination 
# - update default bb params for pointcloud cropping
# - user feedback mechanism 
# - module post-processing cleaning => [vo / dense ]
# - fix script kill issue
# - modularize python script calls in main-file.sh 
# - change output-dir name for p360 module
# - tracking weight files
# - fix number of points in different in ply-rgb and ply-seg
# - python script existing folder detection
# - automate uploading to aws
# - better input parsing 
# - output folder generation script
# - finalize main.sh input reading
# - add clean-up.sh
# - delete dense_reconstruction folder on failure 
# - delete input-backend/vo
# - fix dense-reconstruction crashing
# - run steps after dense-reconstruction
# - failed dense-folder deletion not working
# - log the main.sh output to date-based logging
# - final folder output logging
# - script based based folder detection

# ============================
# [ec2 setup]
# - dense reconstruction failing after rig-bundle-adjustement

# [fail cases]
# output-backend/config/RJM/2024_06_06_utc/svo_files/front_2024-06-05-09-09-54_220_291.json
# output-backend/config/RJM/2024_06_06_utc/svo_files/front_2024-06-05-09-09-54_418_489.json

# ============================



# - [logging]
# - log every processed segment
# - log every  finished segment
# - log every finished svo file 
# - figure out a way to resume after script termination
# - [git issues]
# - tracking weight files
# - [aws utils]
# - upload output-backend/dense-reconstruction + output-backend/segmented-frame-by-frame folder to aws
