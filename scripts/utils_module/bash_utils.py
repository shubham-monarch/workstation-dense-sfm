import json
import logging, coloredlogs
from typing import List
import os
import random
from  scripts.utils_module import io_utils

def generate_config_from_json(json_path : str):
	with open(json_path, 'r') as f:
		data = json.load(f)
		logging.info(f"json_path: {json_path}")
		logging.info(f"type(data): {type(data)} len(data): {len(data)}")
		# print(f"json_path: {json_path}")
		# print(f"type(data): {type(data)} len(data): {len(data)}")
		for pair in data:
			print(pair) 


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
	
