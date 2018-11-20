"""
This script will collect the inventory of a PC directory.
"""

import argparse
import datetime
import logging
import os
from lib import my_env
from lib import sqlstore
from lib.sqlstore import Directory, File, Observation


parser = argparse.ArgumentParser(
    description="Collect directory contents from PC."
)
parser.add_argument('-d', '--directory', type=str, required=True,
                    help='Please provide the directory for which inventory is required.')
args = parser.parse_args()
cfg = my_env.init_env("pcloud", __file__)
logging.info("Start application")
logging.info("Arguments: {a}".format(a=args))
dir_start = args.directory
sql_eng = sqlstore.init_session(cfg["Main"]["db"])
now = datetime.datetime.now()
observation = Observation(
    timestamp=now.strftime("%Y-%m-%d %H:%M:%S"),
    remark="PC Inventory {dir}".format(dir=dir_start)
)
sql_eng.add(observation)
sql_eng.flush()
sql_eng.refresh(observation)
observation_id = observation.id
# Handle Directory metadata
ini_path, ini_name = os.path.split(dir_start)
dir_obj = Directory(
    name=ini_name,
    path=ini_path,
    observation_id=observation_id
)
sql_eng.add(dir_obj)
sql_eng.flush()
sql_eng.refresh(dir_obj)
# Then handle Directory contents
dir_obj_id = dir_obj.id
for root, dirs, files in os.walk(dir_start):
    path, dir_name = os.path.split(root)
    dir_obj = Directory(
        name=dir_name,
        path=path,
        observation_id=observation_id
    )
    sql_eng.add(dir_obj)
    sql_eng.flush()
    sql_eng.refresh(dir_obj)
    dir_obj_id = dir_obj.id
    for fn in files:
        props = dict(
            name=fn,
            observation_id=observation_id,
            directory_id=dir_obj_id,
            size=os.path.getsize(os.path.join(root, fn)),
            path=root
        )
        fileobj = File(**props)
        sql_eng.add(fileobj)
sql_eng.commit()
logging.info("End application")
