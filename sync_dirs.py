#!/opt/envs/pcloud/bin/python3
"""
This script syncs directories from pcloud to local drive. All files on pcloud will be on local drive as well.
Local drive can have more files.
"""

import argparse
import json
import logging
import os
import webbrowser
from lib import my_env, pcloud_handler
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Compare source (PCloud) and target (Local) directories."
)
parser.add_argument('-s', '--source_dir', type=str, required=True,
                    help='Please provide the PCloud source directory.')
parser.add_argument('-t', '--target_dir', type=str, required=True,
                    help='Please provide the Local target directory ID.')
parser.add_argument('-a', '--action', type=str, required=False, default='view', choices=['view', 'run'],
                    help='Please provide the action: view changes or run to synchronize target with source')
args = parser.parse_args()
cfg = my_env.init_env("pcloud", __file__)
pc = pcloud_handler.PcloudHandler()
logging.info("Start application")
logging.info("Arguments: {a}".format(a=args))
source_dir = args.source_dir
target_dir = args.target_dir
pcloud_tree = {}
fp = os.getenv('DATADIR')
# Get youngest pcloud inventory file
inventory_files = [file for file in os.listdir(fp) if '.json' == file[-len('.json'):]]
inventory_files.sort(reverse=True)
ffn_current = inventory_files[0]
with open(os.path.join(fp, ffn_current), 'r') as fh:
    pcloud_contents = json.load(fh)
pcloud_handler.item2key(pcloud_tree, pcloud_contents['path'], pcloud_contents['contents'], source_dir, target_dir)
local_tree = pcloud_handler.get_local_contents(target_dir)
new_items = []
modified_items = []
removed_items = []
for k in pcloud_tree:
    if k in local_tree:
        if 'size' in pcloud_tree[k] and pcloud_tree[k]['size'] != local_tree[k]['size']: modified_items.append(k)
    else:
        new_items.append(k)
for k in local_tree:
    if k not in pcloud_tree: removed_items.append(k)
report = f'<html><body><h3>New: {len(new_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Created</th></tr>'
for k in new_items:
    report += f'<tr><td>{k}</td><td>{pcloud_tree[k]["created"][:-6]}</td></tr>'
report += '</table>'
report += f'<h3>Modified: {len(modified_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Modified</th></tr>'
for k in modified_items:
    report += f'<tr><td>{k}</td><td>{pcloud_tree[k]["modified"][:-6]}</td></tr>'
report += '</table>'
report += f'<h3>Removed: {len(removed_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Modified</th></tr>'
for k in removed_items:
    report += f'<tr><td>{k}</td><td>{local_tree[k]["modified"]}</td></tr>'
report += '</table></body></html>'
ffn = os.path.join(fp, 'report.html')
with open(ffn,'w') as fh:
    fh.write(report)
webbrowser.open(ffn)

if args.action == 'run':
    for k in new_items + modified_items:
        if pcloud_tree[k]['isfolder']:
            Path(k).mkdir(parents=True, exist_ok=True)
        else:
            pcloud_handler.get_file(pc.get_filelink(pcloud_tree[k]['fileid']), k)
            logging.info(f"File {k} Contents: {pcloud_tree[k]}")

logging.info("End application")
