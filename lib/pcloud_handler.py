import datetime
import logging
import os
import requests
from pathlib import Path, PurePosixPath


class PcloudHandler:
    """
    This class consolidates the pcloud functionality. On initialization a connection to pcloud account is set.
    List method allows to list all files in the specified folder. Logout method will close the connection.
    """

    def __init__(self):
        """
        On initialization a connection to pcloud account is done.
        """
        user = os.getenv('PCUser')
        passwd = os.getenv('PCPwd')
        params = dict(username=user, password=passwd, getauth=1)
        self.url_base = os.getenv('PCHome')
        method = "userinfo"
        url = self.url_base + method
        self.session = requests.Session()
        r = self.session.get(url, params=params)
        if r.status_code != 200:
            msg = "Could not connect to pcloud. Status: {s}, reason: {reason}.".format(s=r.status_code, reason=r.reason)
            logging.critical(msg)
            raise SystemExit(msg)
        # Status Code OK, so successful login
        res = r.json()
        self.auth = res["auth"]
        usedquota = res["usedquota"]
        quota = res["quota"]
        pct = (usedquota / quota) * 100
        msg = "{pct:.2f}% used.".format(pct=pct)
        logging.info(msg)

    def get_contents(self):
        """
        This method will return the result of listfolder from root path (/) with recursive flag set, so full directory
        should be returned.

        :return:
        """
        params = dict(path="/", recursive=1)
        # params = dict(path="/")
        method = "listfolder"
        url = self.url_base + method
        r = self.session.get(url, params=params)
        if r.status_code != 200:
            msg = "Could not connect to pcloud. Status: {s}, reason: {reason}.".format(s=r.status_code, reason=r.reason)
            logging.critical(msg)
            raise SystemExit(msg)
        # Status Code OK, so successful login
        res = r.json()
        return res["metadata"]

    def copyfile(self, fileid, tofolderid):
        """
        This method copies a file to a destination folder on PCloud.

        :param fileid: ID of the file to be copied.
        :param tofolderid: Target folder on PCloud.
        :return:
        """
        params = dict(fileid=fileid, tofolderid=tofolderid)
        method = "copyfile"
        url = self.url_base + method
        r = self.session.get(url, params=params)
        if r.status_code != 200:
            msg = "Could not copy file. Status: {s}, reason: {reason}.".format(s=r.status_code, reason=r.reason)
            logging.critical(msg)
            raise SystemExit(msg)
        # Status Code OK, so successful login
        res = r.json()
        return res

    def get_fileinfo(self, fileid):
        """
        Input is PCloud File Id, returns the the info related to the file.

        :param fileid: PCloud FileId of the file to be copied
        :return:
        """
        params = dict(fileid=fileid)
        method = "getfilelink"
        url = self.url_base + method
        r = self.session.get(url, params=params)
        if r.status_code != 200:
            msg = "Could not get file link. Status: {s}, reason: {reason}.".format(s=r.status_code, reason=r.reason)
            logging.critical(msg)
            raise SystemExit(msg)
        # Status Code OK, so successful login
        res = r.json()
        return res

    def get_filelink(self, fileid):
        """
        Input is PCloud File Id, returns the the PCloud path to the file.

        :param fileid: PCloud FileId of the file
        :return: URL of the file with ID fileid
        """
        res = self.get_fileinfo(fileid)
        url = f"https://{res['hosts'][0]}{res['path']}"
        logging.debug(f"URL: {url}")
        return url

    def downloadfile(self, url, path, target):
        """
        Download a file from pcloud to the local system

        :param url: URL of the file to be downloaded
        :param path: Local directory where the file need to be stored
        :param target: Filename of the downloaded file
        :return:
        """
        params = dict(url=url, path=path, target=target)
        # params = dict(url=url, target=target)
        method = "downloadfile"
        url = self.url_base + method
        r = self.session.get(url, params=params)
        if r.status_code != 200:
            msg = "Could not download file. Status: {s}, reason: {reason}.".format(s=r.status_code, reason=r.reason)
            logging.critical(msg)
            raise SystemExit(msg)
        # Status Code OK, so successful login
        res = r.json()
        return res

    def listfolder(self, folderid):
        """
        This method will get a folder ID and return json string with folder information.

        :param folderid: ID of the folder for which the info is required
        :return:
        """
        # Todo: merge method with get_contents method.
        params = dict(folderid=folderid)
        method = "listfolder"
        url = self.url_base + method
        r = self.session.get(url, params=params)
        if r.status_code != 200:
            msg = "Could not collect metadata. Status: {s}, reason: {reason}.".format(s=r.status_code, reason=r.reason)
            logging.critical(msg)
            raise SystemExit(msg)
        # Status Code OK, so successful login
        res = r.json()
        return res

    def logout(self):
        method = "logout"
        url = self.url_base + method
        params = dict(auth=self.auth)
        r = self.session.get(url, params=params)
        if r.status_code != 200:
            msg = "Could not logout from pcloud. Status: {s}, reason: {rsn}.".format(s=r.status_code, rsn=r.reason)
            logging.error(msg)
        else:
            res = r.json()
            if res["auth_deleted"]:
                msg = "Logout as required"
            else:
                msg = "Logout not successful, status code: {status}".format(status=r.status_code)
            logging.info(msg)


def convert_fn(fn, pcloud_root, local_root):
    """
    This function accepts a tuple of PCloud File parts and returns the Local Filename.
    
    :param fn: Filename (or directory name) as discovered in Pcloud, so get PurePosixPath parts.
    :param pcloud_root: PCloud root directory - use PurePosixPath parts.
    :param local_root: Local Target root directory - use local machine Path parts.
    :return: Filename (directory name) on the local target as a string - use local machine Path parts.
    """
    fn_parts = list(PurePosixPath(fn).parts)
    pcloud_parts = list(PurePosixPath(pcloud_root).parts)
    local_parts = list(Path(local_root).parts)
    # Replace PCloud anchor with Local anchor
    pcloud_parts[0] = local_parts[0]
    # Verify that pcloud_parts is in fn_parts, so File is in scope
    # Compare without anchor
    fn_comp = fn_parts[1:]
    pcloud_comp = pcloud_parts[1:]
    logging.debug(f"For File {fn} Compare Parts {fn_comp} with Root {pcloud_comp}")
    if (len(fn_comp) >= len(pcloud_comp)) and (fn_comp[0:len(pcloud_comp)] == pcloud_comp):
        fn_naked = fn_parts[len(pcloud_parts):]
        fn_newparts = local_parts + fn_naked
        fn_new = Path(*fn_newparts)
        logging.debug(f"Source: {fn} - Target: {fn_new}")
        return str(fn_new)
    else:
        # logging.error(f"File {fn} is not in scope of PCloud {pcloud_root}")
        return False


def get_file(url, ffn):
    """
    This function gets a file from URL url and keeps it on location in ffn.

    :param url: URL where to get the file.
    :param ffn:
    :return: True if file has been downloaded, False otherwise
    """
    ffn_obj = Path(ffn)
    ffn_path = ffn_obj.parent
    fn = ffn_obj.name
    logging.info(f"Get path: {ffn_path} - File: {fn}")
    ffn_path.mkdir(parents=True, exist_ok=True)
    with open(ffn, 'wb') as handle:
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            msg = f"Could not get file link. Status: {r.status_code}, reason: {r.reason}."
            logging.critical(msg)
            raise SystemExit(msg)
        # Chunk size should be at least 1MB, to avoid switching getting content and writing to disk.
        for block in r.iter_content(chunk_size=1024 * 1024):
            if not block:
                break
            handle.write(block)


def item2key(pcloud_dict, path, contents, parent_dir=None, local_dir=None):
    """
    Recursive function to reduce the PCloud inventory and convert the directories and files in scope into a dictionary.
    Files are added as keys to the dictionary, Directories are further explored by calling this function again.

    :param pcloud_dict: Dictionary containing Directories and Files in scope for the sync process. The dictionary is
    created in the recursive process.
    :param path: Current path under investigation
    :param contents: Directories and files in scope for the sync process.
    :param parent_dir: PCloud Parent directory to start sync process. If None, comparing current and previous pcloud
    inventory.
    :param local_dir: Directory on the local PC that is target directory. If None, comparing current and previous pcloud
    inventory.
    :return: nothing - the information is build in the pcloud_dict dictionary.
    """
    for item in contents:
        fn = PurePosixPath(path).joinpath(item['name'])
        if parent_dir:
            key = convert_fn(fn, parent_dir, local_dir)
        else:
            key = fn
        if item['isfolder']:
            if key:
                pcloud_dict[key] = dict(
                    fn=fn,
                    isfolder=item['isfolder'],
                    created=item['created'],
                    modified=item['modified']
                )
            item2key(pcloud_dict, fn, item['contents'], parent_dir, local_dir)
        elif key:
            pcloud_dict[key] = dict(
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


def get_local_contents(local_path):
    """
    This function collects directories and files on the local device.

    :param local_path: Root folder of the local path.
    :return: Dictionary to keep directories and files on local device.
    """
    local_dict = {}
    for root, dirs, files in os.walk(local_path):
        local_dict[root] = dict(
            isfolder=True,
            modified=datetime.datetime.fromtimestamp(int(os.path.getmtime(root))).strftime("%Y-%m-%d %H:%M:%S")
        )
        for file in files:
            key = os.path.join(root, file)
            local_dict[key] = dict(
                isfolder=False,
                size=os.path.getsize(os.path.join(root, file)),
                modified=datetime.datetime.fromtimestamp(int(os.path.getmtime(os.path.join(root, file))))
                .strftime("%Y-%m-%d %H:%M:%S")
            )
    return local_dict
