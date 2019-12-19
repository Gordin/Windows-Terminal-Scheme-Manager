import os
import logging
import json
import re
from functools import lru_cache, reduce
from operator import getitem
import random

class WindowsTerminalConfigFile(object):
    DEFAULT_CONFIG_PATH = '%LOCALAPPDATA%\\Packages\\Microsoft.WindowsTerminal_8wekyb3d8bbwe\\LocalState\\profiles.json'

    def __init__(self, path=DEFAULT_CONFIG_PATH):
        if not os.path.exists(os.path.expandvars(path)):
            raise FileNotFoundError('Config file not found ({})'.format(path))
        self.path = path
        self.schemes = []

    def _read_config_file(self):
        logging.info("Trying to load Terminal config from {}".format(os.path.expandvars(self.path)))
        with open(os.path.expandvars(self.path), 'r') as file:
            line_array = file.read().split('\n')
        logging.info("Loaded Terminal config file")
        lines = iter(line_array)
        self.schemes = []
        lines_before = []
        lines_after = []
        scheme_lines = ["{"]

        while not re.match(' *"schemes":', line := next(lines)):
            self.__check_for_scheme(line)
            lines_before.append(line)
        self._before_schemes = lines_after

        scheme_lines.append(line)
        while not re.match(' *]', line := next(lines)):
            if not re.match(' *//', line):
                scheme_lines.append(line)
        scheme_lines.append(']}')
        self._schemes = json.loads('\n'.join(scheme_lines))
        
        for line in lines:
            lines_after.append(line)
        self._after_schemes = lines_after

        logging.info("Finished parsing Terminal config file")
        return [lines_before, self._schemes['schemes'], lines_after]

    def __check_for_scheme(self, line):
        match = re.match(' *"colorScheme": *"(.*)",', line)
        if match:
            self.schemes.append({"colorScheme": match[1]})
            return match[1]
        return None
    
    @lru_cache()
    def __parse_without_comments(self, reload=False):
        if not reload and hasattr(self, 'config'):
            return
        logging.info("Trying to load Terminal config from {}".format(os.path.expandvars(self.path)))
        with open(os.path.expandvars(self.path), 'r') as file:
            line_array = file.read().split('\n')
        
        lines_without_comments = []
        self.comments = {}
        for i, line in enumerate(line_array):
            if re.match(' *//|^ *$', line):
                self.comments[i] = line
            else:
                lines_without_comments.append(line)
        
        self.config = json.loads('\n'.join(lines_without_comments))
    
    def __assemble_config(self):
        conf_string = json.dumps(self.config, indent=4)
        comment_offset = 0
        assembled_config_lines = []

        for i, line in enumerate(conf_string.split("\n")):
            while (comment_for_current_line := self.comments.get(i + comment_offset)) != None:
                assembled_config_lines.append(comment_for_current_line)
                comment_offset += 1
            assembled_config_lines.append(line)
        
        self.assembled_config = "\n".join(assembled_config_lines)
    
    def reload(self):
        self.__parse_without_comments(reload=True)
    
    def test_write(self, path=DEFAULT_CONFIG_PATH.replace('profiles.json', 'profiles_test.json')):
        self.__parse_without_comments()
        old_path = self.path
        self.path = path
        self.write()
        self.path = old_path
    
    def write(self):
        self.__assemble_config()
        logging.info("Trying to write Terminal config file to {}".format(self.path))
        with open(os.path.expandvars(self.path), 'w') as file:
            file.write(self.assembled_config)
        logging.info("Finished writing Terminal config file")
    
    def get(self, *arguments):
        self.__parse_without_comments()
        return reduce(getitem, arguments, self.config)

    def profiles(self):
        return self.get('profiles')
    
    def _get_profile_names(self):
        profiles = self.profiles()
        return [profile["name"] for profile in profiles]

    def set_attribute_for_all_profiles(self, key, value):
        names = self._get_profile_names()
        for name in names:
            self.set_attribute_for_profile(name, key, value)

    def get_attribute_for_profile(self, profile_name, key):
        profile = next((profile for profile in self.get('profiles') if profile['name'] == profile_name))
        return profile[key]
    
    def set_attribute_for_profile(self, profile_name, key, value):
        profile = next((profile for profile in self.get('profiles') if profile['name'] == profile_name))
        profile[key] = value

    @lru_cache()
    def get_schemes(self):
        self.__parse_without_comments()
        return [scheme['name'] for scheme in self.get('schemes')]
    
    def set_scheme(self, name=None, profile=None):
        schemes = self.get_schemes()
        if not name:
            name = random.choice(schemes)
        if profile:
            self.set_attribute_for_profile(profile, 'colorScheme', name)
        else:
            self.set_attribute_for_all_profiles('colorScheme', name)
    
    def get_current_scheme(self, profile=None):
        if not profile:
            profile = self._get_profile_names()[0]
        return self.get_attribute_for_profile(profile, 'colorScheme')
    
    def cycle_schemes(self, profile=None, backwards=False):
        current_scheme = self.get_current_scheme(profile)
        schemes = self.get_schemes()
        if backwards:
            schemes.reverse()
        for i, scheme in enumerate(schemes):
            if scheme == current_scheme:
                if i < len(schemes):
                    next_scheme = schemes[i+1]
                else:
                    next_scheme = schemes[0]
                break
        self.set_scheme(next_scheme, profile)
        self.write()
        

if __name__ == "__main__":
    conf = WindowsTerminalConfigFile()
    conf.__parse_without_comments()
    import ipdb; ipdb.set_trace()
    print(conf.config)
