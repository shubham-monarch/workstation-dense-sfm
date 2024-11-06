#! /usr/bin/env python3

from pathlib import Path
from typing import List    
import cv2
import numpy as np
import os
import logging, coloredlogs
import argparse
from tqdm import tqdm

# LOGGING SETUP
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
coloredlogs.install(level='INFO', logger=logger, force=True)


def remove_hood(input_path, output_dir):

    img_name = os.path.basename(input_path)
    os.makedirs(output_dir, exist_ok=True)
    img = cv2.imread(str(input_path))

    h, w, _ = img.shape
    
    if img is None:
        return
    x1, y1, x2, y2 = [int(0.68* h), int(0.21 * w), int(h), int(0.85 * w)]  
    
    # Black out the bbox region
    img[x1:x2, y1:y2] = 0
        
    output_path = os.path.join(output_dir, img_name)
    cv2.imwrite(str(output_path), img)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Remove hood from images')
    parser.add_argument('--i', type=str, required=True,
                        help='Input directory containing images')
    parser.add_argument('--o', type=str, required=True, 
                        help='Output directory for processed images')
    
    args = parser.parse_args()
    
    input_dir = Path(args.i)
    output_dir = Path(args.o)
    
    for img_file in tqdm(list(input_dir.glob('*.jpg')), desc="Processing images"):
        remove_hood(img_file, output_dir)
