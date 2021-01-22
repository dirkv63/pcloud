"""
This script will collect the inventory of pcloud.
"""

import datetime
import logging
import os
import time
from email.utils import parsedate
from lib import my_env
from lib import pcloud_handler
from retired import sqlstore
from retired.sqlstore import Directory, File, Observation


def handle_item(item, directory_id):
    props = dict(
        name=item["name"],
        pcloud_id=item["id"],
        observation_id=observation_id
    )
    if item["isfolder"]:
        parent_dir_name = dirname_dict["d{pid}".format(pid=item["parentfolderid"])]
        dirname_dict[item["id"]] = parent_dir_name + "/" + item["name"]
        props["path"] = parent_dir_name
        props["parent_id"] = directory_id
        dirobj = Directory(**props)
        sql_eng.add(dirobj)
        sql_eng.flush()
        sql_eng.refresh(dirobj)
        dirobj_id = dirobj.id
        for obj in item["contents"]:
            handle_item(obj, directory_id=dirobj_id)
    else:
        props["contenttype"] = item["contenttype"]
        props["directory_id"] = directory_id
        props["size"] = item["size"]
        props["hash"] = str(item["hash"])
        props["path"] = dirname_dict["d{pid}".format(pid=item["parentfolderid"])]
        created = parsedate(item["created"])
        props["created"] = int(time.mktime(created))
        fileobj = File(**props)
        sql_eng.add(fileobj)
    return


cfg = my_env.init_env("pcloud", __file__)
logging.info("Start application")
sql_eng = sqlstore.init_session(os.getenv('DB'))
now = datetime.datetime.now()
observation = Observation(
    timestamp=now.strftime("%Y-%m-%d %H:%M:%S"),
    remark="PCloud Inventory"
)
sql_eng.add(observation)
sql_eng.flush()
sql_eng.refresh(observation)
observation_id = observation.id
pc = pcloud_handler.PcloudHandler()
res = pc.get_contents()
# Handle Directory metadata
dir_obj = Directory(
    name=res["name"],
    pcloud_id=res["id"],
    observation_id=observation_id
)
dirname_dict = {res["id"]: res["name"]}
sql_eng.add(dir_obj)
sql_eng.flush()
sql_eng.refresh(dir_obj)
# Then handle Directory contents
dir_obj_id = dir_obj.id
for init_obj in res["contents"]:
    handle_item(init_obj, directory_id=dir_obj_id)
sql_eng.commit()
pc.logout()
logging.info("End application")
