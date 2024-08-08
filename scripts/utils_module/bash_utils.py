import json
import logging, coloredlogs
from typing import List
import os
import random
from  scripts.utils_module import io_utils
import pyzed.sl as sl
import logging, coloredlogs

# logging.getLogger('ZED').addHandler(logging.NullHandler())
logging.getLogger().addHandler(logging.NullHandler())

# logging.basicConfig(level=logging.CRITICAL)
# logging.basicConfig(filename='log_filename.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

logger = logging.getLogger('sl')
logger.disabled = True

def generate_config_from_json(json_path : str):
	with open(json_path, 'r') as f:
		data = json.load(f)
		logging.info(f"json_path: {json_path}")
		logging.info(f"type(data): {type(data)} len(data): {len(data)}")
		# print(f"json_path: {json_path}")
		# print(f"type(data): {type(data)} len(data): {len(data)}")
		for pair in data:
			print(pair) 


def get_baseline(svo_path : str, svo_root = None) -> float:
	# logger = logging.getLogger('sl')
	# logger.disabled = True
	# logging.getLogger('ZED').setLevel(logging.CRITICAL)	
	if svo_root is None:
		svo_root = 'input-backend/svo-files'

	svo_path = os.path.join(svo_root, svo_path)

	input_type = sl.InputType()
	input_type.set_from_svo_file(svo_path)

	init = sl.InitParameters(input_t=input_type, svo_real_time_mode=False, sdk_verbose=False)
	init.coordinate_units = sl.UNIT.METER   

	zed = sl.Camera()
	status = zed.open(init)

	zed_baseline = None
	if status != sl.ERROR_CODE.SUCCESS:
		logging.error(f"Error while opening the SVO file: {repr(status)} --> [USING BASELINE AS 0.13]")
		zed_baseline = 0.13

	else:
		camera_information = zed.get_camera_information()
		zed_baseline =   camera_information.camera_configuration.calibration_parameters.get_camera_baseline()
		
	zed.close()
	
	print (zed_baseline)
	# os.environ['ZED_BASELINE'] = str(zed_baseline) 

def generate_config_files_from_json(json_path : str, input_root = None, output_root = None):
	
	if not os.path.exists(json_path) or not os.path.isfile(json_path):
		logging.error(f"Invalid json file path: {json_path}")
		# print(f"Invalid json file path: {json_path}")
		print (" ")
		return
	
	config_files = []
	
	# arr to be returned to the bash script
	bash_arr = []

	if input_root is None:
		input_root = 'output-backend/vo'
	
	svo_file = os.path.relpath(json_path, input_root)
	svo_file = svo_file.replace('.json', '.svo')
	# print(f"svo_file: {svo_file}")
	
	if output_root is None:
		output_root = 'output-backend/config'
	
	try:
		with open(json_path, 'r') as f:
			data = json.load(f)
			config_dict = dict()
			logging.info(f"json_path: {json_path}")
			logging.info(f"type(data): {type(data)} len(data): {len(data)}")
			
			for pair in data:
				config_dict['SVO_FILENAME']=svo_file
				config_dict['SVO_START_IDX']=pair[0]
				config_dict['SVO_END_IDX']=pair[1]

				config_path = os.path.join(output_root, svo_file)
				
				# print(f"config_path: {config_path}")
				config_path = config_path.replace('.svo', f"_{pair[0]}_{pair[1]}.json")
				# print(f"config_path: {config_path}")
				
				config_files.append(config_path)

				# io_utils.delete_folders([os.path.dirname(config_path)])
				io_utils.create_folders([os.path.dirname(config_path)])

				with open(config_path, 'w') as f:
					json.dump(config_dict, f, indent=4)
					logging.info(f"Data written to {config_path}")
					# print(f"Data written to {config_path}")
	
	except Exception as e:
		logging.error(f"Error while processing json file: {e}")
		exit(1)

	bash_arr = ' '.join(config_files)	
	print(bash_arr)
	
def get_file_list(input_path : str) -> List[str]:
	'''
	recursively lists all the svo-files inside a folder
	
	:param input_path: [str] => path to the input w.r.t [input-backend folder]
	
	: output => [List[str]] => ' ' separated list of svo files
	'''
	
	svo_path_abs = []
	# svo_path_rel = []
	if os.path.isfile(input_path):
		svo_path_abs.append(input_path)
		# svo_path_rel.append(os.path.relpath(input_path, ROOT_INPUT))
	elif os.path.isdir(input_path):
		for dirpath, dirnames, filenames in os.walk(input_path):
			for filename in filenames:
				if filename.endswith('.svo'):
					svo_path_abs.append(os.path.join(dirpath, filename))
					# svo_path_rel.append(os.path.relpath(os.path.join(dirpath, filename), ROOT_INPUT))
	
	random.shuffle(svo_path_abs)
	# logging.info(f"svo_path_abs: {svo_path_abs}")
	# print(f"svo_path_abs: {svo_path_abs}")
	bash_arr = ' '.join(svo_path_abs)
	print (bash_arr)
	
