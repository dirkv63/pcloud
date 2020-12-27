"""
This script will collect the inventory of pcloud and keeps it in a json file.
"""

import datetime
import json
import logging
import os
from lib import my_env
from lib import pcloud_handler


cfg = my_env.init_env("pcloud", __file__)
logging.info("Start application")
now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
pc = pcloud_handler.PcloudHandler()
res = pc.get_contents()
ffn = os.path.join(os.getenv('DATADIR'), f'pcloud{now}.json')
with open(ffn, 'w') as fh:
    json.dump(res, fh)
pc.logout()
logging.info("End application")
