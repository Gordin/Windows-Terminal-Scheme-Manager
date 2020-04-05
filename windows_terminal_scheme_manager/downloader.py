import logging
import shutil
import tempfile
import urllib.request
import json
import os
import zipfile
import re
import shutil
from windows_terminal_scheme_manager.terminal_config import WindowsTerminalConfigFile

class WindowsTerminalSchemeDownloader(object):
    DEFAULT_SCHEMES_URL = 'https://github.com/mbadolato/iTerm2-Color-Schemes/archive/master.zip'

    def __init__(self, url=DEFAULT_SCHEMES_URL):
        self.url = url

    def download_repo(self):
        logging.info("Downloading schemes from {}".format(self.url))
        with urllib.request.urlopen(self.url) as response:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(response, tmp_file)
        logging.info("Successfully Downloaded Schemes")
        return tmp_file

    def unpack_schemes(self, repo_zip, zip_scheme_path ='iTerm2-Color-Schemes-master/windowsterminal/'):
        tmpdir = tempfile.mkdtemp()
        logging.info("Unpacking Schemes to temporary directory '{}'".format(tmpdir))
        z = zipfile.ZipFile(repo_zip.name, 'r')
        p = zipfile.Path(z, at=zip_scheme_path)
        scheme_filenames = [x.name for x in (p.iterdir())]
        for name in scheme_filenames:
            logging.debug("Extracting {}".format(name))
            z.extract(zip_scheme_path + name, path=tmpdir)
        logging.info("Unpacking Schemes completed")
        return tmpdir, scheme_filenames

    def scheme_filenames(self, repo_path):
        logging.info("Trying to get scheme filenames from '{}'".format(repo_path))
        return list(os.walk(repo_path))[2][2]

    def get_scheme_from_file(self, filename):
        with open(filename, 'r') as file:
            scheme = json.load(file)
            logging.debug("Loaded scheme '{}'".format(filename))
        return scheme

    def get_all_schemes(self, path, schemes):
        scheme_array = []
        logging.info("Loading all schemes from json files")
        for scheme_path in schemes:
            scheme_array.append(
                self.get_scheme_from_file(os.path.join(path, scheme_path))
            )
        logging.info("Loaded all new schemes")
        return scheme_array

    def download_and_add_schemes_to_config(self, repo_path=None, keep_repo=False, config_file=None):
        # optional parameter is only there to test stuff without downloading the zip every time...
        if not repo_path:
            repo_zip = self.download_repo()
            schemes_path, schemes = self.unpack_schemes(repo_zip)
            logging.info('Run with this to skip re-downloading next time: --repo_path {}'.format(schemes_path))
            schemes_path = os.path.join(schemes_path, 'iTerm2-Color-Schemes-master', 'windowsterminal')
        else:
            schemes = self.scheme_filenames(repo_path)
            schemes_path = os.path.join(repo_path, 'iTerm2-Color-Schemes-master', 'windowsterminal')
        logging.debug("Repo Path: {}".format(schemes_path))
        new_schemes = self.get_all_schemes(schemes_path, schemes)
        config_file = WindowsTerminalConfigFile(path=config_file)
        config = config_file.config
        old_scheme_names = config_file.config.schemes()
        for new_scheme in new_schemes:
            if new_scheme['name'] in old_scheme_names:
                logging.debug('Not adding scheme {} (already in config)'.format(new_scheme['name']))
                continue
            config.add_scheme(new_scheme, reuse_copy=True)
        config_file.write()
        if not keep_repo:
            logging.info("Removing temporary repo directory")
            shutil.rmtree(schemes_path)
        else:
            logging.info("Keeping temporary repo directory")