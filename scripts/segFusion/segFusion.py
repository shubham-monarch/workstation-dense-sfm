from segmentation.pidnet import PIDNet, get_seg_model
from segmentation.utils import input_transform
import torch
import cv2
import numpy as np
import open3d as o3d
import torch.nn.functional as F


class Config:
	def __init__(self, farm_type = 'vineyards'):
		
		if farm_type == 'vineyard_mapping':
			self.seg_model = 'pidnet_large'
			self.num_classes = 5
			self.seg_pretrained = './segmentation/pretrained/2024.06.14.V.PID.V1.0_4cls.pt'
			self.imgnet_pretrained = False
		elif farm_type == 'vineyards':
			self.seg_model = 'pidnet_large'
			self.num_classes = 5
			self.seg_pretrained = './segmentation/pretrained/2024.06.14.V.PID.V1.0_4cls.pt'
			self.imgnet_pretrained = False
		elif farm_type == 'dairy':
			self.seg_model = 'pidnet_large'
			self.num_classes = 5
			self.seg_pretrained = './segmentation/pretrained/2024.06.14.D.PID.V1.0_4cls.pt'
			self.imgnet_pretrained = False
		
class SegInfer:
	def __init__(self, config):
		
		self.config = config
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

	def img2seg(self, img, viz=False):
		
		img = input_transform(img)
		img = img.transpose((2, 0, 1)).copy()
		img = torch.from_numpy(img).unsqueeze(0).cuda()
		size = img.size()
		pred_val = self.seg_model(img)
		pred = F.interpolate(input=pred_val[0], size=size[-2:], mode='bilinear', align_corners=True)
		seg_mask = torch.argmax(pred, dim=1).squeeze(0).cpu().numpy()

		if viz:
			# seg_mask = cv2.resize(seg_mask, (img.size(2), img.size(3)), interpolation=cv2.INTER_NEAREST)
			seg_mask_ = np.array(seg_mask, dtype=np.uint8)*5
			seg_mask_ = cv2.applyColorMap(seg_mask_, cv2.COLORMAP_RAINBOW)
			seg_mask_ = cv2.cvtColor(seg_mask_, cv2.COLOR_BGR2RGB)
			# seg_mask_ = cv2.addWeighted(img, 0.5, seg_mask, 0.5, 0)
			cv2.imwrite('seg_mask.jpg', seg_mask_)
		
		return seg_mask
	
	def run(self, img):
		
		img, mask = self.mask_bottom_center(img)
		cmap = self.mavis_cmap()
		seg_mask = self.img2seg(img)

		return seg_mask

def main():
	
	config = Config()
	inferencer = SegInfer(config=config)
	img = cv2.imread('test.jpg')
	seg_mask = inferencer.run(img)


if __name__ == '__main__':
	main()