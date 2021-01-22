#!/opt/envs/pcloud/bin/python3
"""
This script will analyze the inventory of pcloud.
"""

import json
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lib import my_env
from lib import pcloud_handler


def item2key(pc_dict, path, contents):
    for item in contents:
        fn = f"{path}/{item['name']}"
        if item['isfolder']:
            pc_dict[fn] = dict(
                isfolder=item['isfolder'],
                created=item['created'],
                modified=item['modified']
            )
            item2key(pc_dict, f"{path}/{item['name']}", item['contents'])
        else:
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

cfg = my_env.init_env("pcloud", __file__)
logging.info("Start application")
pc_prev = {}
pc_current = {}
fp = os.getenv('DATADIR')
inventory_files = [file for file in os.listdir(fp) if '.json' == file[-len('.json'):]]
inventory_files.sort(reverse=True)
[ffn_current, ffn_prev] = inventory_files[:2]
# ffn = '/home/dirk/development/python/pcloud/data/pcloud20201227161239.json'
with open(os.path.join(fp, ffn_current), 'r') as fh:
    pc_contents = json.load(fh)
pcloud_handler.item2key(pc_current, pc_contents['path'], pc_contents['contents'])
# ffn = '/home/dirk/development/python/pcloud/data/pcloud20201227144214.json'
with open(os.path.join(fp, ffn_prev), 'r') as fh:
    pc_contents = json.load(fh)
pcloud_handler.item2key(pc_prev, pc_contents['path'], pc_contents['contents'])
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
msg["Subject"] = f"PCloud: {len(new_items)} New - {len(modified_items)} Modified - {len(removed_items)} Removed"
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
