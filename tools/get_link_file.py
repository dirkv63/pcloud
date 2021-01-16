"""
This script gets a link to a file with file ID. This link then can  be used to download the file.
"""

from lib import my_env, pcloud_handler
import argparse
import os

# Configure command line arguments
parser = argparse.ArgumentParser(
    description="Get File Link."
)
parser.add_argument('-f', '--fileid', type=str, required=True,
                    help='Please provide the file ID.')
args = parser.parse_args()
cfg = my_env.init_env("pcloud", __file__)
pc = pcloud_handler.PcloudHandler()

url = pc.get_filelink(args.fileid)
print(url)
path = '/home/dirk/temp/pcloudtest/p2/p3'
target = 'MondovinoLes106.odt'
target_ffn = os.path.join(path, target)
pcloud_handler.get_file(url, target_ffn)
