import numpy as np
import open3d as o3d
import yaml
import argparse

def load_ply(ply_file):
    
    pcd = o3d.io.read_point_cloud(ply_file)
    return np.asarray(pcd.points), np.asarray(pcd.colors)

def load_yml(yml_file):
    
    with open(yml_file, 'r') as f:
        color_map = yaml.safe_load(f)
        
    return {tuple(map(int, key.split(','))): value for key, value in color_map.items()}

def get_label(segmentation_rgb, color_map):
    return color_map.get(tuple((segmentation_rgb * 255).astype(int)), 0)  # Default to 0 if not found

def create_xyzrgbl_ply(rgb_ply_file, seg_ply_file, yml_file, output_ply_file):
    
    points, rgb_values = load_ply(rgb_ply_file)
    points_seg, seg_rgb_values = load_ply(seg_ply_file)
    
    assert len(points) == len(seg_rgb_values), "Number of points in RGB and segmentation PLY files do not match."
    assert np.all(points == points_seg), "Point coordinates in RGB and segmentation PLY files do not match."

    color_map = load_yml(yml_file)
    labels = np.array([get_label(seg_rgb, color_map) for seg_rgb in seg_rgb_values])
    
    # xyzrgbl = np.hstack((points, rgb_values, labels[:, np.newaxis]))
    # pcd = o3d.geometry.PointCloud()
    # pcd.points = o3d.utility.Vector3dVector(xyzrgbl[:, :3])
    # pcd.colors = o3d.utility.Vector3dVector(xyzrgbl[:, 3:6])
    
    # o3d.io.write_point_cloud(output_ply_file, pcd)
    
    # To include labels as a separate scalar, use the write function below
    with open(output_ply_file, 'w') as f:
        f.write(f"ply\nformat ascii 1.0\nelement vertex {len(points)}\n")
        f.write("property float x\nproperty float y\nproperty float z\n")
        f.write("property uchar red\nproperty uchar green\nproperty uchar blue\n")
        f.write("property uchar label\n")
        f.write("end_header\n")
        for point, rgb, label in zip(points, (rgb_values*255).astype(np.uint8), labels):
            f.write(f"{point[0]} {point[1]} {point[2]} {rgb[0]} {rgb[1]} {rgb[2]} {label}\n")

def main():
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--rgb_ply", help="Path to the RGB PLY file", required=True)
        parser.add_argument("--seg_ply", help="Path to the segmentation PLY file", required=True)
        parser.add_argument("--yml", help="Path to the YAML file containing the color map", required=True)
        parser.add_argument("--output", help="Path to the output XYZRGBL PLY file", required=True)
        args = parser.parse_args()
        
        create_xyzrgbl_ply(args.rgb_ply, args.seg_ply, args.yml, args.output)

if __name__ == "__main__":
    main()