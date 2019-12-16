import shutil
import tempfile
import urllib.request
import json
import os
import zipfile
import re
import shutil
import logging

class WindowsTerminalSchemeDownloader(object):
    def download_repo(self):
        schemes_repo_url = 'https://github.com/mbadolato/iTerm2-Color-Schemes/archive/master.zip'
        logging.info("Downloading schemes from {}".format(schemes_repo_url))
        with urllib.request.urlopen(schemes_repo_url) as response:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                shutil.copyfileobj(response, tmp_file)
        logging.info("Successfully Downloaded Schemes")
        return tmp_file

    def unpack_schemes(self, repo_zip):
        zip_scheme_path = 'iTerm2-Color-Schemes-master/windowsterminal/'
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
            scheme_array.append(self.get_scheme_from_file(path + scheme_path.replace('/', '\\')))
        logging.info("Loaded all new schemes")
        return scheme_array

    def read_terminal_config_file(self):
        settings_path = '%LOCALAPPDATA%\\Packages\\' \
        'Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\profiles.json'
        logging.info("Trying to load Terminal config from {}".format(os.path.expandvars(settings_path)))
        with open(os.path.expandvars(settings_path), 'r') as file:
            line_array = file.read().split('\n')
        logging.info("Loaded Terminal config file")
        lines = iter(line_array)
        lines_before = []
        lines_after = []
        scheme_lines = ["{"]

        while not re.match(' *"schemes":', line := next(lines)):
            lines_before.append(line)

        scheme_lines.append(line)
        while not re.match(' *]', line := next(lines)):
            if not re.match(' *//', line):
                scheme_lines.append(line)
        scheme_lines.append(']}')
        schemes = json.loads('\n'.join(scheme_lines))
        
        for line in lines:
            lines_after.append(line)

        logging.info("Finished parsing Terminal config file")
        return [lines_before, schemes['schemes'], lines_after]

    def write_terminal_config_file(self, config, path='%LOCALAPPDATA%\\Packages\\' \
        'Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\profiles.json'):
        logging.info("Trying to write Terminal config file to {}".format(path))
        with open(os.path.expandvars(path), 'w') as file:
            file.write(config)
        logging.info("Finished writing Terminal config file")

    def json_to_config(self, before, schemes, after):
        logging.info("Reassembling config file")
        scheme_string = json.dumps({'schemes': schemes}, indent=4, sort_keys=True)[1:-2]
        config = '\n'.join(before) + scheme_string + ',\n' + '\n'.join(after)
        return config

    def add_schemes_to_scheme_array(self, old, new):
        logging.info("Combining {} existing schemes with {} new ones".format(len(old), len(new)))
        combined = [x for x in old]
        scheme_names = [t['name'] for t in old]
        for scheme in new:
            if not scheme['name'] in scheme_names:
                combined.append(scheme)
        logging.info("Combined all schemes. Config file will have {} schemes".format(len(combined)))
        return combined

    def download_and_add_schemes_to_config(self, repo_path=None, keep_repo=False):
        # optional parameter is only there to test stuff without downloading the zip every time...
        if not repo_path:
            repo_zip = self.download_repo()
            schemes_path, schemes = self.unpack_schemes(repo_zip)
            schemes_path += '\\iTerm2-Color-Schemes-master\\windowsterminal\\'
        else:
            schemes = self.scheme_filenames(repo_path)
            schemes_path = repo_path + 'iTerm2-Color-Schemes-master\\windowsterminal\\'
        print("Repo Path: {}".format(schemes_path))
        new_schemes = self.get_all_schemes(schemes_path, schemes)
        lines_before, old_schemes, lines_after = downloader.read_terminal_config_file()
        combined_schemes = self.add_schemes_to_scheme_array(old_schemes, new_schemes)
        self.write_terminal_config_file(self.json_to_config(lines_before, combined_schemes, lines_after))
        if not keep_repo:
            logging.info("Removing temporary repo directory")
            shutil.rmtree(schemes_path)
        else:
            logging.info("Keeping temporary repo directory")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    downloader = WindowsTerminalSchemeDownloader()
    downloader.download_and_add_schemes_to_config(repo_path='C:\\Users\\Gordin\\AppData\\Local\\Temp\\tmpyteiipoy\\', keep_repo=True)
    # downloader.download_and_add_schemes_to_config(keep_repo=True)