"""
This script will compare a source and a target directory. Starting from a source directory and observation id and a
target directory and observation id, the script checks if every directory and file in source are also in target. Files
need to have same size.
"""

import argparse
import logging
import os
from lib import my_env
from retired import sqlstore
from retired.sqlstore import Directory, File
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


def compare_files(src_dir_id, src_obs_id, tgt_dir_id, tgt_obs_id):
    """
    This method will compare files in a source directory with files in a target directory. Every file in source needs
    to be available in target with same file size.
    :param src_dir_id: ID of the source directory
    :param src_obs_id: ID of the source observation
    :param tgt_dir_id: ID of the target directory
    :param tgt_obs_id: ID of the target observation
    :return:
    """
    files = sql_eng.query(File).filter(File.directory_id == src_dir_id,
                                       File.observation_id == src_obs_id).all()
    for file in files:
        # Find the file in target set
        try:
            target_file = sql_eng.query(File).filter(File.directory_id == tgt_dir_id, File.name == file.name,
                                                     File.observation_id == tgt_obs_id).one()
        except NoResultFound:
            logging.error("Path {path} file {name} not in target set!".format(path=file.path, name=file.name))
            msg = "File not found,{f}".format(f=os.path.join(file.path, file.name))
            issue_list.append(msg)
        except MultipleResultsFound:
            logging.error("Path {path} file {name} multiple results found.".format(path=file.path, name=file.name))
        else:
            if file.size != target_file.size:
                logging.error("Path {path} file {name} Source size: {ss} target size: {ts}".format(path=file.path,
                                                                                                   name=file.name,
                                                                                                   ss=file.size,
                                                                                                   ts=target_file.size))
                msg = "File size not ok,{f}".format(f=os.path.join(file.path, file.name))
                issue_list.append(msg)
            else:
                logging.debug("Path {path} file {name} on source and target!".format(path=file.path, name=file.name))


def get_directory_id(root, obs_id):
    """
    This method will return the directory ID for a specific root directory (terminology from os.walk).
    :param root: Full path name for which the directory ID needs to be found.
    :param obs_id: ID of the observation set in which directory needs to be found.
    :return: id of the directory record
    """
    path, name = os.path.split(root)
    try:
        dir_rec = sql_eng.query(Directory).filter(Directory.path == path, Directory.name == name,
                                                  Directory.observation_id == obs_id).one()
    except NoResultFound:
        msg = "Directory {sd} for observation {sid} not found.".format(sd=root, sid=obs_id)
        raise SystemExit(msg)
    except MultipleResultsFound:
        msg = "Directory {sd} and observation {sid} return multiple rows.".format(sd=root, sid=obs_id)
        raise SystemExit(msg)
    return dir_rec.id


def handle_subdirs(src_dir_id, src_obs_id, tgt_dir_id, tgt_obs_id):
    """
    This method will find call to compare files, then find all source subdirectories for a source directory.
    Each subdirectory must be found as a target subdirectory. When found, then each file in the source subdirectory
    will be compared with the file in the target subdirectory.
    :param src_dir_id: ID of the source directory
    :param src_obs_id: ID of the source observation
    :param tgt_dir_id: ID of the target directory
    :param tgt_obs_id: ID of the target observation
    :return:
    """
    compare_files(src_dir_id, src_obs_id, tgt_dir_id, tgt_obs_id)
    subdirs = sql_eng.query(Directory).filter(Directory.parent_id == src_dir_id,
                                              Directory.observation_id == src_obs_id).all()
    for subdir in subdirs:
        try:
            target_subdir = sql_eng.query(Directory).filter(Directory.name == subdir.name,
                                                            Directory.parent_id == tgt_dir_id,
                                                            Directory.observation_id == tgt_obs_id).one()
        except NoResultFound:
            logging.error("Path {path} subdir {name} not found on target.".format(path=subdir.path, name=subdir.name))
            msg = "Directory not found,{f}".format(f=os.path.join(subdir.path, subdir.name))
            issue_list.append(msg)
        except MultipleResultsFound:
            logging.error("Path {path} subdir {name} not found on target.".format(path=subdir.path, name=subdir.name))
        else:
            # Target subdir found, compare files then handle child directories
            handle_subdirs(subdir.id, subdir.observation_id, target_subdir.id, target_subdir.observation_id)


parser = argparse.ArgumentParser(
    description="Compare source and target directories."
)
parser.add_argument('-s', '--source_dir_id', type=int, required=True,
                    help='Please provide the source directory ID.')
parser.add_argument('-i', '--source_obs_id', type=int, required=True,
                    help='Please provide the observation id for the source.')
parser.add_argument('-t', '--target_dir_id', type=int, required=True,
                    help='Please provide the target directory ID.')
parser.add_argument('-j', '--target_obs_id', type=int, required=True,
                    help='Please provide the observation id for the target.')
args = parser.parse_args()
cfg = my_env.init_env("pcloud", __file__)
logging.info("Start application")
logging.info("Arguments: {a}".format(a=args))
source_dir_id = args.source_dir_id
source_obs_id = args.source_obs_id
target_dir_id = args.target_dir_id
target_obs_id = args.target_obs_id
sql_eng = sqlstore.init_session(os.getenv('DB'))
issue_list = []

# Get source_rec_id
# source_dir_id = get_directory_id(source_dir, source_obs_id)
# target_dir_id = get_directory_id(target_dir, target_obs_id)

handle_subdirs(source_dir_id, source_obs_id, target_dir_id, target_obs_id)
if issue_list:
    with open(os.path.join(os.getenv('LOGDIR'), "pcloud_issues.csv"), "w") as fh:
        for issue in issue_list:
            fh.write(issue + "\n")
else:
    logging.info('No differences found.')
logging.info("End application")
