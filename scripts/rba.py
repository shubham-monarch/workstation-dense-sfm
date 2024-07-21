#! /usr/bin/env python3

import logging,coloredlogs
import argparse

def main(output_folder):
    
    

    pass


if __name__ == "__main__":
    coloredlogs.install(level="DEBUG", force=True)  # install a handler on the root logger

    parser = argparse.ArgumentParser(description='Script to process a SVO file')
    parser.add_argument('--rba_output', type=str, required = True, help='Path to the rba output file')
    args = parser.parse_args()  
    
    main(args.rba_output)