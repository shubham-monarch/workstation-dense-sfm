#! /usr/bin/env python3

import json
import logging,coloredlogs


def update_svo_index(svo_file: str, index_file: str) -> bool:
    try:
        # Attempt to open and read the index file; if it doesn't exist, use an empty list
        try:
            with open(index_file, 'r') as file:
                processed_files = json.load(file)
        except FileNotFoundError:
            processed_files = []
        
        # Check if svo_file is already in the list
        if svo_file in processed_files:
            return False  # svo_file is already in the index, no update needed
        
        # If svo_file is not in the list, append it
        processed_files.append(svo_file)
        
        # Write the updated list back to the index file
        with open(index_file, 'w') as file:
            json.dump(processed_files, file)
        
        return True  # svo_file was added to the index
    except Exception as e:
        print(f"An error occurred: {e}")
        return False  # An error occurred


if __name__ == "__main__":
    coloredlogs.install(level="INFO",force=True)
    index_file = "index/svo_index.json"
    svo_file = "abcd.svo"

    update = update_svo_index(svo_file, index_file)
        
