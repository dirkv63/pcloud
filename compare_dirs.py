#!/opt/envs/pcloud/bin/python3
"""
This script compares a directory on PCloud with a directory on the local host. A report is created with the differences.
"""

import argparse
import json
import logging
import os
import datetime
import webbrowser
from lib import my_env
from pprint import pprint


def item2key(pc_dict, path, contents):
    for item in contents:
        fn = f"{path}/{item['name']}"
        if item['isfolder']:
            if source_dir in fn:
                key = fn.replace(source_dir, target_dir)
                pc_dict[key] = dict(
                    fn=fn,
                    isfolder=item['isfolder'],
                    created=item['created'],
                    modified=item['modified']
                )
            item2key(pc_dict, f"{path}/{item['name']}", item['contents'])
        else:
            if source_dir in fn:
                key = fn.replace(source_dir, target_dir)
                pc_dict[key] = dict(
                    fn=fn,
                    isfolder=item['isfolder'],
                    created=item['created'],
                    modified=item['modified'],
                    fileid=item['fileid'],
                    size=item['size'],
                    hash=item['hash'],
                    contenttype=item['contenttype']
                )
    return


def get_local_pc(local_dict, local_path):
    for root, dirs, files in os.walk(local_path):
        local_dict[root] = dict(isfolder=True)
        for file in files:
            key = os.path.join(root,file)
            local_dict[key] = dict(
                isfolder=False,
                size=os.path.getsize(os.path.join(root, file)),
                modified=datetime.datetime.fromtimestamp(int(os.path.getmtime(os.path.join(root, file))))
                    .strftime("%Y-%m-%d %H:%M:%S")
            )
    return

parser = argparse.ArgumentParser(
    description="Compare source (PCloud) and target (Local) directories."
)
parser.add_argument('-s', '--source_dir', type=str, required=True,
                    help='Please provide the PCloud source directory.')
parser.add_argument('-t', '--target_dir', type=str, required=True,
                    help='Please provide the Local target directory ID.')
args = parser.parse_args()
cfg = my_env.init_env("pcloud", __file__)
logging.info("Start application")
logging.info("Arguments: {a}".format(a=args))
source_dir = args.source_dir
target_dir = args.target_dir
pc_tree = {}
fp = os.getenv('DATADIR')
inventory_files = [file for file in os.listdir(fp) if '.json' == file[-len('.json'):]]
inventory_files.sort(reverse=True)
ffn_current = inventory_files[0]
with open(os.path.join(fp, ffn_current), 'r') as fh:
    pc_contents = json.load(fh)
item2key(pc_tree, pc_contents['path'], pc_contents['contents'])
pprint(pc_tree)
local_tree = {}
get_local_pc(local_tree, target_dir)
pprint(local_tree)
new_items = []
modified_items = []
removed_items = []
for k in pc_tree:
    if k in local_tree:
        if 'size' in pc_tree[k] and pc_tree[k]['size'] != local_tree[k]['size']: modified_items.append(k)
    else:
        new_items.append(k)
for k in local_tree:
    if k not in pc_tree: removed_items.append(k)
report = f'<html><body><h3>New: {len(new_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Created</th></tr>'
for k in new_items:
    report += f'<tr><td>{k}</td><td>{pc_tree[k]["created"][:-6]}</td></tr>'
report += '</table>'
report += f'<h3>Modified: {len(modified_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Modified</th></tr>'
for k in modified_items:
    report += f'<tr><td>{k}</td><td>{pc_tree[k]["modified"][:-6]}</td></tr>'
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
logging.info("End application")
