#! /usr/bin/env python3

import logging,coloredlogs
import open3d as o3d
import os
import numpy as np
import yaml
from tqdm import tqdm


def is_close_color(color1: np.ndarray, color2: np.ndarray, tolerance=10) -> bool:
    '''
    Check if two bgr colors are close to each other
    '''
    # logging.warning(f"[is_close_color]")
    # logging.info(f"color1: {color1} color2: {color2}")
    return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

def get_label(bgr: np.ndarray, color_map: dict) -> int:
    '''
    Get label for a bgr pixel using the color_map

    :param bgr: color in [b, g, r] format
    :param color_map: dict: color_map to use for mapping colors to labels
    '''

    # logging.warning(f"[get_label]")
    # logging.info(f"bgr: {bgr}")
    # logging.info(f"type(bgr): {type(bgr)}")
    
    for label, color in color_map.items():
        if is_close_color(bgr, np.array(color)):
            return label
    
    # default to 0 if not found
    return 0
    
if __name__ == "__main__":
    coloredlogs.install(level="INFO", force=True)

    module_path = os.path.dirname(__file__)
    
    ply_segmented = os.path.join(module_path,"dense-segmented.ply")
    mavis_file = os.path.join(module_path, "Mavis.yaml")

    
    with open(mavis_file, 'r') as f:
        data = yaml.safe_load(f)

    color_map = data.get("color_map", {})

    logging.info(f"color_map: {color_map}")
    
    # {label : (r, g, b)} to {(r, g, b) : label}
    color_map = {key: tuple(value) for key, value in color_map.items()}

    logging.info(f"color_map: {color_map}")

    pcd = o3d.io.read_point_cloud(ply_segmented)
    points, colors_rgb = np.asarray(pcd.points), np.asarray(pcd.colors)
    colors_bgr = colors_rgb[:, [2, 1, 0]]  # Reorder RGB to BGR
    logging.info(f"type(colors_bgr): {type(colors_bgr)} colors_bgr.shape: {colors_bgr.shape}")
    
    # for color_bgr in colors_bgr: 
    #     # logging.info(f"type(color): {type(color_bgr)} color.shape: {color_bgr.shape}")
    #     # logging.info(f"color_bgr: {color_bgr}")
    
    #     # logging.info("=======================")
    #     # for label, color in color_map.items():
    #     #     # if is_close_color(bgr, np.array(color)):
    #     #     logging.info(f"color: {color} label: {label}")  
    #     # logging.info("=======================\n")
        
    #     # label = get_label((color*255).astype(np.uint8), color_map)
    #     label = get_label((color_bgr*255), color_map)
    #     logging.info(f"label: {label}")
    #     break
    
    
    # labels = np.array([get_label(color_bgr, color_map) for color_bgr in colors_bgr])
    labels = np.array([get_label(color_bgr * 255, color_map) for color_bgr in tqdm(colors_bgr, desc="Processing labels")])
    
    import matplotlib.pyplot as plt
    from collections import Counter

    # Assuming labels is a list or array of labels obtained from your code
    label_counts = Counter(labels)

    # Sort labels and counts for consistent plotting
    sorted_labels, sorted_counts = zip(*sorted(label_counts.items()))

    plt.figure(figsize=(10, 8))
    plt.bar(sorted_labels, sorted_counts, color='skyblue')
    plt.xlabel('Label')
    plt.ylabel('Count')
    plt.title('Histogram of Labels')
    plt.xticks(rotation=45)
    plt.show()
    # logging.info(f"labels: {labels[:100]}")
    # logging.info(f"type(labels): {type(labels)} labels.shape: {labels.shape}")
    # logging.info(f"labels: {labels}")
     
    # with open(ply_segmented, 'w') as f:
    #     f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
    #     f.write("property float x\nproperty float y\nproperty float z\n")
    #     f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
    #     f.write("property uchar label\n")
    #     f.write("end_header\n")
    #     for point, rgb, label in zip(points, (rgb_values*255).astype(np.uint8), labels):
    #         f.write(f"{point[0]} {point[1]} {point[2]} {rgb[0]} {rgb[1]} {rgb[2]} {label}\n")
