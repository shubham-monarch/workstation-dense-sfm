import numpy as np
import open3d as o3d
import yaml
import argparse
import logging, coloredlogs
import random 
from PIL import Image
import os


def load_ply(ply_file):
    
    pcd = o3d.io.read_point_cloud(ply_file)
    return np.asarray(pcd.points), np.asarray(pcd.colors)

def load_yml(yml_file):
    logging.warning(f"[load_yml]")
    with open(yml_file, 'r') as f:
        color_map = yaml.safe_load(f)

    logging.info(f"type(color_map): {type(color_map)}")
    logging.info(f"color_map: {color_map}")

    # return
    # return {tuple(map(int, key.split(','))): value for key, value in color_map.items()}
    logging.info("=====================================")
    a = [value for key, value in color_map.items()]
    logging.info(f"a: {a}")
    logging.info("=====================================")
    
def get_label(segmentation_rgb, color_map):
    return color_map.get(tuple((segmentation_rgb * 255).astype(int)), 0)  # Default to 0 if not found

def create_xyzrgbl_ply(rgb_ply_file, seg_ply_file, yml_file, output_ply_file):
    
    points, rgb_values = load_ply(rgb_ply_file)
    points_seg, seg_rgb_values = load_ply(seg_ply_file)
    
    # assert len(points) == len(seg_rgb_values), "Number of points in RGB and segmentation PLY files do not match."
    # assert np.all(points == points_seg), "Point coordinates in RGB and segmentation PLY files do not match."

    # logging.info(f"type(points): {type(points)} points.shape: {points.shape}")
    # logging.info(f"type(points_seg): {type(points_seg)} points_seg.shape: {points_seg.shape}")
    # logging.info(f"type(rgb_values): {type(rgb_values)} rgb_values.shape: {rgb_values.shape}")
    # logging.info(f"type(seg_rgb_values): {type(seg_rgb_values)} seg_rgb_values.shape: {seg_rgb_values.shape}")


    # logging.info("=====================================")
    # # # logging.info(f"points[:5]: {points[:5]}")
    # # # logging.info(f"points_seg[:5]: {points_seg[:5]}")
    # # logging.info(f"rgb_values[:5]\n: {rgb_values[:20] * 255}")
    # # logging.info("=====================================\n")
    # logging.info(f"seg_rgb_values[:5]\n: {seg_rgb_values[:20]* 255}")
    # logging.info("=====================================")
    
    # # return
    random_indices = random.sample(range(len(seg_rgb_values)), 30)
    for index in random_indices:    
        logging.info(f"{index} {seg_rgb_values[index] * 255}")

    # color_map = load_yml(yml_file)
    # logging.info(f"type(color_map): {type(color_map)}")
    # logging.info(f"color_map: {color_map}")

    # return
    # labels = np.array([get_label(seg_rgb, color_map) for seg_rgb in seg_rgb_values])
    
    # xyzrgbl = np.hstack((points, rgb_values, labels[:, np.newaxis]))
    # pcd = o3d.geometry.PointCloud()
    # pcd.points = o3d.utility.Vector3dVector(xyzrgbl[:, :3])
    # pcd.colors = o3d.utility.Vector3dVector(xyzrgbl[:, 3:6])
    
    # o3d.io.write_point_cloud(output_ply_file, pcd)
    
    # To include labels as a separate scalar, use the write function below
    # with open(output_ply_file, 'w') as f:
    #     f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
    #     f.write("property float x\nproperty float y\nproperty float z\n")
    #     f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
    #     f.write("property uchar label\n")
    #     f.write("end_header\n")
    #     for point, rgb, label in zip(points, (rgb_values*255).astype(np.uint8), labels):
    #         f.write(f"{point[0]} {point[1]} {point[2]} {rgb[0]} {rgb[1]} {rgb[2]} {label}\n")
        
        
if __name__ == "__main__":
    coloredlogs.install(level="INFO", force=True)
    parser = argparse.ArgumentParser()

    # Define the color map and labels
    color_map = {
        0: [0, 0, 0],
        1: [246, 4, 228],
        2: [173, 94, 48],
        3: [68, 171, 117],
        4: [162, 122, 174],
        5: [121, 119, 148],
        6: [253, 75, 40],
        7: [170, 60, 100],
        8: [60, 100, 179]
    }

    labels = {
        0: "void",
        1: "obstacle",
        2: "navigable_space",
        3: "vine_canopy",
        4: "vine_stem",
        5: "vine_pole",
        6: "vegetation",
        7: "tractor_hood",
        8: "sky"
    }

    # Function to check if two colors are close within a given tolerance
    def is_close_color(color1, color2, tolerance=10):
        return all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2))

    # Convert the color map to tuples
    color_map = {key: tuple(value) for key, value in color_map.items()}

    logging.info(f"color_map: {color_map}")

    module_dir = os.path.dirname(__file__)  # Get the directory where the module is located
    image_dir = "images-segmented/left/frame_1000_.jpg"
    image = Image.open(os.path.join(module_dir, image_dir))

    w, h = image.size

    logging.info(f"w: {w} h: {h}")

    for i in range(20):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        
        rgb_val = image.getpixel((x, y))
        bgr_val = rgb_val[::-1]  # Convert to BGR
        label = "not found"
        
        # Check if the pixel color is close to any color in the color_map
        for key, color in color_map.items():
            if is_close_color(bgr_val, color):
                label = labels[key]
                break
        
        print(f"Pixel at ({x}, {y}): BGR={bgr_val}, Label={label}")
