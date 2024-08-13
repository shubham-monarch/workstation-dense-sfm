import torch
import cv2
import numpy as np
import open3d as o3d
import torch.nn.functional as F
from scripts.utils_module import io_utils
import logging, coloredlogs
from scripts.segFusion.segmentation.pidnet import PIDNet, get_seg_model, get_seg_model_new
from scripts.segFusion.segmentation.utils import input_transform
import os
import argparse
import yaml


class Config:
	def __init__(self, farm_type = 'vineyards'):
		
		self.farm_type = farm_type
		if farm_type == 'vineyard_mapping':
			self.seg_model = 'pidnet_large'
			self.num_classes = 5
			self.seg_pretrained = './segmentation/pretrained/2024.06.14.V.PID.V1.0_4cls.pt'
			self.imgnet_pretrained = False
		elif farm_type == 'vineyards':
			self.seg_model = 'pidnet_large'
			self.num_classes = 5
			self.seg_pretrained = './segmentation/pretrained/2023.10.24.V.PID.V1.1.pt'
			self.imgnet_pretrained = False
			self.image_size = [3, 1024, 1024]
			self.ori_image_size = [3, 1920, 1080]
		elif farm_type == 'dairy':
			self.seg_model = 'pidnet_large'
			self.num_classes = 5
			self.seg_pretrained = './segmentation/pretrained/2023.10.24.V.PID.V1.1.pt'
			self.imgnet_pretrained = False
		
class SegInfer:
	def __init__(self, config):
		
		self.config = config
		self.farm_type = config.farm_type
		if self.farm_type == 'vineyard_mapping':
			self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
			self.seg_model = get_seg_model(config, config.imgnet_pretrained)
			model_state_file = config.seg_pretrained
			pretrained_dict = torch.load(model_state_file)
			if 'state_dict' in pretrained_dict:
				pretrained_dict = pretrained_dict['state_dict']
			model_dict = self.seg_model.state_dict()
			pretrained_dict = {k[6:]: v for k, v in pretrained_dict.items()
								if k[6:] in model_dict.keys()}
			model_dict.update(pretrained_dict)
			self.seg_model.load_state_dict(model_dict)
			self.seg_model = self.seg_model.cuda()
			self.seg_model.eval()
		elif self.farm_type == 'vineyards':
			self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
			self.seg_model = get_seg_model_new(config, config.imgnet_pretrained)
			self.seg_model = self.seg_model.cuda()
			self.seg_model.eval()
		elif self.farm_type == 'dairy':
			self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
			self.seg_model = get_seg_model_new(config, config.imgnet_pretrained)
			self.seg_model = self.seg_model.cuda()
			self.seg_model.eval()
		else:
			raise ValueError("Invalid farm type")
	
	def mask_bottom_center(self, image):
		
		height, width = image.shape[:2]
		mask_top = int(height * (2/3))
		mask_bottom = height
		mask_left = int(width * (0.5/3.5))
		mask_right = int(width * (3/3.5))
		mask = np.zeros((height, width), dtype=np.uint8)+255
		mask[mask_top:mask_bottom, mask_left:mask_right] = 0
		masked_image = cv2.bitwise_and(image, image, mask=mask)
	
		return masked_image, mask
	
	def mavis_cmap(self):
			
		cmap = {}
	
		cmap[-1] = [0, 0, 0]
		cmap[0] = [0, 0, 0]
		cmap[1] = [246, 4, 228] 
		cmap[2] = [173, 94, 48] 
		cmap[3] = [68, 171, 117] 
		cmap[4] = [162, 122, 174] 
		cmap[5] = [121, 119, 148] 
		cmap[6] = [253, 75, 40] 
		cmap[7] = [170, 60, 100] 
		cmap[8] = [60, 100, 179]
		cmap[9] = [170, 100, 60]
	
		return cmap
	
	def load_cmap(self, cmap_file):
		
		with open(cmap_file, 'r') as f:
			config = yaml.safe_load(f)
		
		cmap = config['color_map']

		return cmap
		

	def img2seg(self, img):
		
		img = input_transform(img)
		img = img.transpose((2, 0, 1)).copy()
		img = torch.from_numpy(img).unsqueeze(0).cuda()
		size = img.size()
		pred_val = self.seg_model(img)
		pred = F.interpolate(input=pred_val[0], size=size[-2:], mode='bilinear', align_corners=True)
		seg_mask = torch.argmax(pred, dim=1).squeeze(0).cpu().numpy()
		if self.farm_type == 'vineyard_mapping':
			cmap = self.load_cmap('Mavis.yaml')
			colored_seg_mask = np.zeros((seg_mask.shape[0], seg_mask.shape[1], 3), dtype=np.uint8)
			for label, color in cmap.items():
				colored_seg_mask[seg_mask == label] = color
		
		else:
			cmap = self.mavis_cmap()
			colored_seg_mask = np.zeros((seg_mask.shape[0], seg_mask.shape[1], 3), dtype=np.uint8)
			for label, color in cmap.items():
				colored_seg_mask[seg_mask == label] = color
		
		return colored_seg_mask
	
	def run(self, img):
		
		img, mask = self.mask_bottom_center(img)
		cmap = self.mavis_cmap()
		seg_mask = self.img2seg(img)

		return seg_mask

def segment(path_RGB : str, path_SEGMENTED : str) -> None:
	'''
	writes the segmented image to the img_seg path
	
	:param path_RGB: path to the rgb image
	:param path_SEGMENTED: path to the segmented image
	'''
	config = Config()
	inferencer = SegInfer(config=config)
	img_RGB= cv2.imread(path_RGB)
	img_SEGMENTED = inferencer.run(img_RGB)

	cv2.imwrite(path_SEGMENTED, img_SEGMENTED)
	
def generate_segmented_images(input_dir : str, output_dir : str) -> None:
	'''
	generate [images-segmented] at the same level as [images]
	
	:param input_dir: path to the [images] folder
	:param output_dir: path to the [images-segmented] folder
	'''
	for root, dirs, files in os.walk(input_dir):
		output_root = root.replace(input_dir, output_dir, 1)
		
		io_utils.create_folders([output_root])

		for file in files:
			if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):		
				input_path = os.path.join(root, file)
				output_path = os.path.join(output_root, file)
				
				segment(input_path, output_path)		
				break	

# TODO: 
# swap images / images-segmented / images-rgb

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument("--input_path", type=str, default="./images")
	parser.add_argument("--farm_type", type=str, default="vineyards")

	args = parser.parse_args()

	images_RGB = args.input_path
	farm_type = args.farm_type

	coloredlogs.install(level="INFO", force = True)

	base_folder = os.path.dirname(images_RGB)
	images_SEG = os.path.join(base_folder, "images-segmented")
	
	logging.info(f"base_folder: {base_folder}")
	logging.info(f"images_RGB: {images_RGB}")
	logging.info(f"images_SEG: {images_SEG}")

	# generate [images-segmented] at the same level as [images] 
	generate_segmented_images(images_RGB, images_SEG)