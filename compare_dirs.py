#!/opt/envs/pcloud/bin/python3
"""
This script compares a directory on PCloud with a directory on the local host..
"""

import argparse
import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lib import my_env
from pprint import pprint


def item2key(pc_dict, path, contents):
    for item in contents:
        fn = f"{path}/{item['name']}"
        if item['isfolder']:
            if source_dir in fn:
                pc_dict[fn] = dict(
                    isfolder=item['isfolder'],
                    created=item['created'],
                    modified=item['modified']
                )
            item2key(pc_dict, f"{path}/{item['name']}", item['contents'])
        else:
            if source_dir in fn:
                pc_dict[fn] = dict(
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
        fn = root
        local_dict[root] = dict(isfolder=True)
        for file in files:
            local_dict[file] = dict(
                isfolder=False,
                size=os.path.getsize(os.path.join(root, file))
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
get_local_pc(local_tree, args.target_dir)
pprint(local_tree)
raise Exception('OK for Now')
new_items = []
modified_items = []
removed_items = []
for k in pc_current:
    if k in pc_prev:
        if 'hash' in pc_current[k] and pc_current[k]['hash'] != pc_prev[k]['hash']: modified_items.append(k)
    else:
        new_items.append(k)
for k in pc_prev:
    if k not in pc_current: removed_items.append(k)
report = f'<h3>New: {len(new_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Created</th></tr>'
for k in new_items:
    report += f'<tr><td>{k}</td><td>{pc_current[k]["created"][:-6]}</td></tr>'
report += '</table>'
report += f'<h3>Modified: {len(modified_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Modified</th></tr>'
for k in modified_items:
    report += f'<tr><td>{k}</td><td>{pc_current[k]["modified"][:-6]}</td></tr>'
report += '</table>'
report += f'<h3>Removed: {len(removed_items)} items</h3>'
report += '<table border="1" cellpadding="4"><tr><th>File</th><th>Modified</th></tr>'
for k in removed_items:
    report += f'<tr><td>{k}</td><td>{pc_prev[k]["modified"][:-6]}</td></tr>'
report += '</table>'

gmail_user = os.getenv('GMAIL_USER')
gmail_pwd = os.getenv('GMAIL_PWD')
recipient = os.getenv('RECIPIENT')

msg = MIMEMultipart()
msg["Subject"] = "PCloud Report"
msg["From"] = gmail_user
msg["To"] = recipient

msg.attach(MIMEText(report, 'html'))

smtp_server = os.getenv('SMTP_SERVER')
smtp_port = os.getenv('SMTP_PORT')
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(gmail_user, gmail_pwd)
text = msg.as_string()
server.sendmail(gmail_user, recipient, text)
logging.debug("Mail sent!")
server.quit()

logging.info("End application")
