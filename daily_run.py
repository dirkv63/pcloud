#!/opt/envs/pcloud/bin/python3
"""
This script collect pcloud data, compares with previous run and send a difference report.
"""

# Allow lib to library import path.
import os
import logging
from lib import my_env
from lib.my_env import run_script

scripts = [
    "get_pcloud_file",
    "analyze_pcloud_file"
]

cfg = my_env.init_env("pcloud", __file__)
logging.info("Start Application")
(fp, filename) = os.path.split(__file__)
for script in scripts:
    logging.info("Run script: {s}.py".format(s=script))
    run_script(fp, "{s}.py".format(s=script))
logging.info("End Application")
