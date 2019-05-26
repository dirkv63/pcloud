"""
This script collects info about a folder. It reads the folder ID from command line then collects and prints the folder
information.
"""

from lib import my_env, pcloud_handler
import argparse
import pprint

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Get folder information."
)
parser.add_argument('-i', '--folderid', type=str, required=True,
                    help='Please provide the folder ID.')
args = parser.parse_args()
cfg = my_env.init_env("pcloud", __file__)
pc = pcloud_handler.PcloudHandler(cfg)
res = pc.listfolder(args.folderid)
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(res)
