"""
This procedure will rebuild the sqlite database
"""

import logging
from lib import my_env
from lib import sqlstore

cfg = my_env.init_env("pcloud", __file__)
logging.info("Start application")
pcloud = sqlstore.DirectConn(cfg)
pcloud.rebuild()
logging.info("sqlite database pcloud rebuild")
logging.info("End application")
