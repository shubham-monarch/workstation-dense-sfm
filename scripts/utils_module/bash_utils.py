import json
import logging, coloredlogs
from typing import List
import os
import random

def generate_config_from_json(json_path : str):
     with open(json_path, 'r') as f:
        data = json.load(f)
        # Now `data` contains the list of lists from the JSON file
        # Example usage:
        for pair in data:
            print(pair) 
        

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
	
