#! /usr/bin/env python3

import json
import logging,coloredlogs
import argparse
import sys


def check_svo_index(svo_file: str, index_file: str) -> bool:
	"""
	Check if the given svo_file is already present in the index file.
	"""
	try:
		with open(index_file, 'r') as file:
			processed_files = json.load(file)
		return svo_file in processed_files
	except FileNotFoundError:
		return False  # index_file does not exist, so svo_file cannot be present
	except json.JSONDecodeError:
		return False  # index_file is not a valid JSON, so cannot check for svo_file
	

if __name__ == "__main__":
	coloredlogs.install(level="INFO",force=True)

	logging.info("=======================")
	logging.info(f"CHECKING SVO INDEX FOR SVO FILE")
	logging.info("=======================\n")


	parser = argparse.ArgumentParser(description='Process some paths and bounding box.')
	parser.add_argument('--index_file', type=str,  required = True, help='Path to svo_index.json')
	parser.add_argument('--svo_file', type=str,  required = True, help='Path to svo file')
	
	args = parser.parse_args()

	# logging.info(f"Index file: {args.index_file}")
	# logging.info(f"SVO file: {args.svo_file}")
	
	# index_file = "index/svo_index.json"
	# svo_file = "abcd.svo"

	# update = check_svo_index(svo_file, index_file)
	update = check_svo_index(args.svo_file, args.index_file)
		
	if update is True:
		logging.info(f"{args.svo_file} is already present in the index file.")
		sys.exit(1)
	else:
		logging.info(f"{args.svo_file} is not present in the index file.")
		sys.exit(0)
	
