#! /usr/bin/env python3 

import pycolmap
import logging,coloredlogs
import open3d as o3d
import cv2
import utils
import os
from tqdm import tqdm
import shutil
from PIL import Image

DIR_ORIGINAL_IMGS = f"front_2023-11-03-11-13-52.svo/images"
DIR_PROCESSED_IMGS = f"images-processed"

# FOLDERS_TO_CREATE = [DIR_PROC_IMGS]

def process_segmentation_masks(input_dir, output_dir):

    assert output_dir is not None, "Output directory is not defined!"
    logging.warning(f"Processing seg-mask in the [{input_dir}] to [{output_dir}]!")
    utils.delete_folders([output_dir])
    utils.create_folders([output_dir])

    for file in tqdm(os.listdir(input_dir), desc="Processing segmentation masks"):
        if "seg" in file:
            
            path_png = os.path.join(input_dir, file)
            path_jpg = path_png.replace("_seg.png", ".jpg")


            with Image.open(path_png) as img:
                rgb_img = img.convert('RGB')
                rgb_img.save(path_jpg, "JPEG")
            
            
            # logging.info(f"Processing {path_png} to {path_jpg}")
            # # new_file_name = file.replace("_seg.png", ".png")            
            # # frame_78__seg.png to frame_78.png
            # # new_file_png = file.replace("_seg.png", ".png")

            # src = os.path.join(input_dir, file)
            # dst = os.path.join(output_dir, new_file_name)
            
            file_jpg = os.path.basename(path_jpg)
            dst = os.path.join(output_dir, file_jpg)
            

            try: 
                shutil.copy(path_jpg, dst)          
            except Exception as e:
                logging.error(f"Error while copying file {file} from {input_dir} to {output_dir}!")
                logging.error(e)

            # break
            

def main():
    input_dir_L = f"masks-segmentation/left_ids"
    ouput_dir_L = f"images/left"
    
    input_dir_R = f"masks-segmentation/right_ids"
    output_dir_R = f"images/right"
    
    process_segmentation_masks(input_dir_L, ouput_dir_L)
    process_segmentation_masks(input_dir_L, output_dir_R)

# def main(sfm_path):
    
#     # utils.delete_folders(FOLDERS_TO_CREATE)
#     # utils.create_folders(FOLDERS_TO_CREATE)
    
#     rec = pycolmap.Reconstruction(sfm_path)
    
#     for idx, (image_id, image) in tqdm(enumerate(rec.images.items()), total = len(rec.images)):
#         # if idx > 10: 
#         #     break
        
#         # logging.debug(f"Processing {idx}th image!")
#         # logging.info(f"{image_id} {image}")
#         img_path = f"{DIR_ORIGINAL_IMGS}/{image.name}"
#         img = cv2.imread(f"{DIR_ORIGINAL_IMGS}/{image.name}")

#         # img_transformed = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#         # img_transformed = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
#         # img_transformed = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
#         # img_transformed = cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)
#         img_transformed = cv2.cvtColor(img, cv2.COLOR_BGR2HLS)
        
        

#         img_path = f"{DIR_PROCESSED_IMGS}/{image.name}"
#         img_dir = os.path.dirname(img_path)

#         # utils.delete_folders([img_dir])
#         utils.create_folders([img_dir])

#         cv2.imwrite(f"{DIR_PROCESSED_IMGS}/{image.name}", img_transformed)
#         # cv2.imshow("img", img)
#         # cv2.waitKey(100)
        

if __name__ == "__main__":
    coloredlogs.install(level="INFO", force=True)
    # sfm_folder_BIN="output"
    # main(sfm_folder_BIN)      
    main()