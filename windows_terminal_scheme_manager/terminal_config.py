import os
import math
import logging
import copy
import json
import re
import sys
from functools import reduce
from operator import getitem
import random
import filecmp
from datetime import datetime
import subprocess
import platform
from functools import lru_cache
import orjson


class WindowsTerminalConfig(object):
    def __init__(self, json, comments):
        self.config = copy.deepcopy(json)
        self.comments = comments
        self._config_copy = None

    def clone(self):
        config = copy.deepcopy(self.config)
        comments = copy.deepcopy(self.comments)
        return self.__class__(config, comments)

    def get_default_config(self):
        default_guid = self.config.get('defaultProfile')
        return next((profile for profile in self.profiles()
                    if profile['guid'] == default_guid))

    def profiles(self):
        return self.get('profiles', 'list')

    def get(self, *arguments):
        return reduce(getitem, arguments, self.config)

    def get_defaults(self):
        return self.get('profiles', 'defaults')

    def add_scheme(self, scheme_dict, reuse_copy=False):
        scheme_name = scheme_dict['name']
        if scheme_name in self.schemes():
            return

        if not reuse_copy or not self._config_copy:
            self._config_copy = copy.deepcopy(self.config)
        self.config['schemes'].append(scheme_dict)
        changed_line_number, change_length = self.__get_line_number_for_change(
            self._config_copy, self.config)
        self.__increase_comment_offset_from_pos(
            start_pos=changed_line_number, increment_by=change_length)
        logging.info('Added scheme {} to config'.format(scheme_name))
        if reuse_copy:
            self._config_copy['schemes'].append(scheme_dict)

    def schemes(self):
        return [scheme['name'] for scheme in self.get('schemes')]

    def set_scheme(self, name=None, profile=None):
        schemes = self.schemes()
        if not schemes:
            logging.info('This config has no schemes :(')
            raise Exception
        if not name:
            name = random.choice(schemes)
        if profile:
            self.set_attribute_for_profile(profile, 'colorScheme', name)
            logging.info('Scheme {} set for profile {}'.format(name, profile))
        else:
            self.set_attribute_in_defaults('colorScheme', name)
            logging.info('Scheme {} set for all profiles'.format(name))

    def get_current_scheme(self, profile=None, choose_first_if_none_chosen=False):
        profile = 'DEFAULTS' if not profile else profile
        current_scheme = self.get_attribute_for_profile(profile, 'colorScheme')

        if not current_scheme and choose_first_if_none_chosen:
            all_schemes = self.schemes()
            if len(all_schemes) == 0:
                logging.info('This config has no schemes :(')
                return None
            current_scheme = all_schemes[0]

        return current_scheme

    def cycle_schemes(self, profile=None, backwards=False):
        next_scheme = self._next_scheme(profile, backwards)
        if not next_scheme:
            raise Exception("This config file does not have schemes to cycle :(")
        logging.info('Cycling schemes. Next Theme: {}'.format(next_scheme))
        self.set_scheme(next_scheme, profile)

    def _next_scheme(self, profile=None, backwards=False):
        current_scheme = self.get_current_scheme(profile)
        if not current_scheme:
            current_scheme = self.get_current_scheme(
                profile, choose_first_if_none_chosen=True)
            if not backwards:
                return current_scheme
        logging.debug("profile: {}, scheme: {}".format(profile, current_scheme))
        schemes = self.schemes()
        if len(schemes) == 0:
            return None
        next_scheme = schemes[0]
        if backwards:
            schemes = list(reversed(schemes))
        for i, scheme in enumerate(schemes):
            if scheme == current_scheme:
                logging.debug("i: {}, current_scheme: {}, new scheme pos: {}".format(
                    i, current_scheme, (i + 1) % len(schemes)))
                next_scheme = schemes[(i + 1) % len(schemes)]
                break
        return next_scheme

    def _get_profile_names(self):
        profiles = self.profiles()
        return [profile["name"] for profile in profiles]

    def set_attribute_in_defaults(self, key, value):
        self.set_attribute_for_profile('DEFAULTS', key, value)

    def get_attribute_for_profile(self, profile_name, key):
        if profile_name == 'DEFAULTS':
            profile = self.get_defaults()
        else:
            profile = next((profile for profile in self.profiles()
                            if profile['name'] == profile_name))
        return profile.get(key)

    def get_profile(self, profile_name, from_other_obj=None):
        if profile_name in ('DEFAULTS', None):
            profile = self.get_defaults()
        else:
            profile = next((profile for profile in self.profiles()
                            if profile['name'] == profile_name))
        return profile

    def set_attribute_for_profile(self, profile_name, key, value):
        profile = self.get_profile(profile_name)

        # Calculations for adding a line here, comments have to be moved
        if key not in profile:
            config_copy = self.clone()
            profile_copy = config_copy.get_profile(profile_name)
            profile_copy[key] = value

            changed_line_number, change_length = self.__get_line_number_for_change(
                self.config, config_copy.config)
            if change_length == 0:
                raise Exception("This should never happen :|")
            self.__increase_comment_offset_from_pos(start_pos=changed_line_number,
                                                    increment_by=change_length)
        profile[key] = value
        return self

    @classmethod
    def from_file(cls, path):
        logging.info("Trying to load Terminal config from {}".format(path))
        try:
            with open(path, 'r') as file:
                text = file.read()
        except OSError:
            print("Could not open config file at \"{}\"\nDoes it exist?".format(
                path
            ))
            raise

        return WindowsTerminalConfig.parse(text)

    @classmethod
    def parse(cls, config_as_string):
        logging.info("Parsing config file")
        text = WindowsTerminalConfigFile.fix_formatting(config_as_string)
        line_array = text.split('\n')

        lines_without_comments = []
        comments = {}
        for i, line in enumerate(line_array):
            if re.match(' *//|^ *$', line):
                comments[i] = line
            else:
                lines_without_comments.append(line)

        return WindowsTerminalConfig(json.loads('\n'.join(lines_without_comments)),
                                     comments)

    def __increase_comment_offset_from_pos(self, start_pos=0, increment_by=1):
        new_comments = {}
        for line_number, comment in self.comments.items():
            if line_number <= start_pos:
                new_comments[line_number] = comment
            else:
                new_comments[line_number + increment_by] = comment
        self.comments = new_comments

    @classmethod
    def _get_formatted_lines(cls, json_dict):
        dumped = orjson.dumps(json_dict, option=orjson.OPT_INDENT_2)
        return WindowsTerminalConfigFile.fix_formatting(dumped.decode()).split('\n')

    @classmethod
    def _get_first_different_line(cls, lines1, lines2):
        # This is the linear approach. Turns out this is really slow when
        # you add all 200 schemes and the config file becomes 4000+ lines...
        # return next(line_num for line_num, (line1, line2) in
        #             enumerate(zip(old_lines, new_lines))
        #             if line1 != line2)

        # Find lines that are different with binary search.
        # Works because the lines are "sorted" for this purpose
        # (unchanged lines numbers < changed line numbers)
        def binary_search(remaining_length, pos=None, counter=0):
            # The counter is just for debugging...
            counter += 1
            # if counter > 200:
            #     import ipdb; ipdb.set_trace()
            if pos is None:
                remaining_length = round(remaining_length / 2)
                pos = remaining_length
            next_distance = max(1, round(remaining_length / 2))
            # print('pos: {} remaining_length: {}'.format(pos, remaining_length))
            if pos == 0:
                return 0 if lines1[0] != lines2[0] else None
            if lines1[pos] == lines2[pos]:
                return binary_search(next_distance, pos + next_distance, counter)
            else:
                # lines[pos] are different, if thes are not, we might be done
                if lines1[pos-1] == lines2[pos-1]:
                    # Check if this is REALLY the first change
                    # We could have gotten lucky with lines like these: '    },'
                    if "".join(lines1[0:pos]) == "".join(lines2[0:pos]):
                        # print('Found it! {}'.format(pos))
                        return pos
                return binary_search(next_distance, pos - next_distance, counter)

        shortest = min(len(lines1), len(lines2))
        first_different_line_number = binary_search(shortest)
        return first_different_line_number

    def __get_line_number_for_change(self, old_json, new_json):
        old_lines = WindowsTerminalConfig._get_formatted_lines(old_json)
        new_lines = WindowsTerminalConfig._get_formatted_lines(new_json)
        # import difflib, tempfile
        # with tempfile.TemporaryFile(mode='w') as file:
        #     file.write(difflib.HtmlDiff().make_file(old_lines, new_lines))
        try:
            first_changed_line_number = WindowsTerminalConfig\
                ._get_first_different_line(old_lines, new_lines)
        except StopIteration:
            None, 0
        comments_before_line = (len(['_' for k in self.comments
                                     if k < first_changed_line_number]))
        # print('Line: ', first_changed_line_number)
        # print("Comments before line", comments_before_line)
        first_changed_line_number_with_comments =\
            first_changed_line_number + comments_before_line
        # print("With comments", first_changed_line_number_with_comments)
        length_difference = abs(len(new_lines) - len(old_lines))
        return first_changed_line_number_with_comments, length_difference

    def assemble_config(self):
        conf_string = WindowsTerminalConfigFile.fix_formatting(
            json.dumps(self.config, indent=4))
        comment_offset = 0
        assembled_config_lines = []

        for i, line in enumerate(conf_string.split("\n")):
            while (comment_for_current_line := self.comments.get(i + comment_offset)) is not None: # noqa
                assembled_config_lines.append(comment_for_current_line)
                comment_offset += 1
            assembled_config_lines.append(line)
        assembled_config = "\n".join(assembled_config_lines)
        return assembled_config


class WindowsTerminalConfigFile(object):
    if platform.system() == "Windows":
        APPDATA = os.path.expandvars('%LOCALAPPDATA%')
    else:
        LOCALAPPDATA = subprocess.check_output(
            ["powershell.exe", "[Environment]::GetFolderPath('LocalApplicationData')"],
            encoding='utf-8').strip()
        APPDATA = subprocess.check_output(
            ["wslpath", LOCALAPPDATA], encoding='utf-8').strip()
    DEFAULT_CONFIG_DIR = os.path.join(
        APPDATA, 'Packages', 'Microsoft.WindowsTerminal_8wekyb3d8bbwe', 'LocalState')
    DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, 'profiles.json')
    DEFAULT_BACKUP_PATH = DEFAULT_CONFIG_DIR
    DEFAULT_BACKUP_FILENAME = 'profiles_{}.json'
    BACKUP_DATE_FORMAT = '%Y%m%d%H%M'
    BRACKET_REGEX = re.compile(r":\s*\n\s*([\[\{])")
    EMPTY_ARRAY_REGEX = re.compile(r"([ \t]*)(\"[^\[\n\"]+\"\: )\[[\t ]*\](,?)")
    EMPTY_OBJECT_REGEX = re.compile(r"([ \t]*)(\"[^{\n\"]+\"\: ){[\t ]*}(,?)")

    def __init__(self, path=None):
        if path is None:
            path = self.__class__.DEFAULT_CONFIG_PATH
        if not os.path.exists(os.path.expandvars(path)):
            sys.exit('Config file not found ({})'.format(path))
        self.path = os.path.expandvars(path)
        self.config = WindowsTerminalConfig.from_file(self.path)

    def backup_config_file(self, dest=DEFAULT_BACKUP_PATH):
        destination_template = os.path.expandvars(os.path.join(
            dest, self.DEFAULT_BACKUP_FILENAME))

        try:
            config_mtime = datetime.fromtimestamp(os.stat(self.path).st_mtime)
        except FileNotFoundError:
            logging.info("No file found at {}, nothing to backup".format(self.path))
            return
        backup_path = destination_template.format(config_mtime.strftime(
            self.BACKUP_DATE_FORMAT))
        logging.info("Backing up Terminal config file to {}".format(backup_path))
        with open(self.path, 'r') as file:
            with open(backup_path, 'w') as backup_file:
                backup_file.write(file.read())

        filecmp.cmp(self.path, backup_path)
        logging.info("Backed up and checked Terminal config file to {}".format(
            backup_path))

    def remove_backups(self, dest=DEFAULT_BACKUP_PATH):
        regex = r"^profiles_\d{12}.json$"
        backups_dir = os.path.expandvars(dest)
        with os.scandir(backups_dir) as files:
            for file in files:
                if file.is_file() and re.match(regex, file.name):
                    logging.debug("Deleting backup file {}".format(file.name))
                    os.remove(os.path.join(backups_dir, file.name))
                    logging.info("Deleted backup file {}".format(file.name))

    def reload(self):
        self.config = WindowsTerminalConfig.from_file(self.path)
        return self.config

    def test_write(self, path=DEFAULT_CONFIG_PATH.replace(
                   'profiles.json', 'profiles_test.json')):
        old_path = self.path
        self.path = path
        self.write()
        self.path = old_path

    def write(self):
        assembled_config = self.config.assemble_config()
        self.backup_config_file()
        logging.info("Trying to write Terminal config file to {}".format(self.path))
        with open(self.path, 'w') as file:
            file.write(assembled_config)
        logging.info("Finished writing Terminal config file")

    @classmethod
    def fix_formatting(cls, lines):
        logging.debug('Fixing Formatting')
        # Removes newlines before opening [ and {
        lines = cls.BRACKET_REGEX.sub(': \\1', lines)
        # Splits empty arrays in 2 lines
        lines = cls.EMPTY_ARRAY_REGEX.sub('\\1\\2[\n\\1]\\3', lines)
        # Splits empty objects in 2 lines
        lines = cls.EMPTY_OBJECT_REGEX.sub('\\1\\2{\n\\1}\\3', lines)
        logging.debug('Formatting fixed')
        return lines
