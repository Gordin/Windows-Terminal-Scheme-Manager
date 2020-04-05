import logging
import re
import json
import os

class WindowsTerminalSchemeChanger(object):
    def __init__(self):
        self.settings_path = '%LOCALAPPDATA%\\Packages\\' \
            'Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\profiles.json'


    def read_terminal_config_file(self):
        logging.info("Trying to load Terminal config from {}".format(os.path.expandvars(self.settings_path)))
        with open(os.path.expandvars(self.settings_path), 'r') as file:
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
