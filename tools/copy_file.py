"""
This script copies a file ID to a specific location.
"""

from lib import my_env, pcloud_handler
import argparse
import pprint

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Copy file to directory."
)
parser.add_argument('-f', '--fileid', type=str, required=True,
                    help='Please provide the file ID.')
parser.add_argument('-t', '--target', type=str, required=True,
                    help='Please provide the folder ID.')
args = parser.parse_args()
cfg = my_env.init_env("pcloud", __file__)
pc = pcloud_handler.PcloudHandler()

res = pc.copyfile(args.fileid, args.target)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(res)
