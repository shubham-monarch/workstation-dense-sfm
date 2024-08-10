#! /bin/bash 

python3 ply_handler.py \
--rgb_ply dense.ply \
--seg_ply segmented-dense.ply \
--yml Mavis.yaml \
--output segmented_labelled.ply