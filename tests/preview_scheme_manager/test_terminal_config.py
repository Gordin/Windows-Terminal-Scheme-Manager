import unittest
import os
import tempfile
from preview_scheme_manager.terminal_config import WindowsTerminalConfigFile

class TestWindowsTerminalConfigFile(unittest.TestCase):

    TESTFILES_PATH = os.path.join('.', 'tests', 'preview_scheme_manager')
    DEFAULT_CONFIG_PATH = os.path.join(TESTFILES_PATH, 'default_profiles.json')
    FIXED_CONFIG_PATH = os.path.join(TESTFILES_PATH, 'fixed_default_profiles.json')
    SCHEME_EXAMPLE = {
        'name': '3024 Day',
        'black': '#090300', 'red': '#db2d20', 'green': '#01a252',
        'yellow': '#fded02', 'blue': '#01a0e4', 'purple': '#a16a94',
        'cyan': '#b5e4f4', 'white': '#a5a2a2',
        'brightBlack': '#5c5855', 'brightRed': '#e8bbd0',
        'brightGreen': '#3a3432', 'brightYellow': '#4a4543',
        'brightBlue': '#807d7c', 'brightPurple': '#d6d5d4',
        'brightCyan': '#cdab53', 'brightWhite': '#f7f7f7',
        'background': '#f7f7f7', 'foreground': '#4a4543'}

    @classmethod
    def setUpClass(cls):
        cls._read_config()

    @classmethod
    def _read_test_file(cls, filename):
        with open(os.path.join(cls.TESTFILES_PATH, filename), 'r') as file:
            text = file.read()
        return text

    @classmethod
    def _read_config(cls):
        with open(cls.DEFAULT_CONFIG_PATH, 'r') as file:
            cls.config_text = file.read()
            cls.config_lines = cls.config_text.split('\n')
        with open(cls.FIXED_CONFIG_PATH, 'r') as file:
            cls.fixed_text = file.read()
            cls.fixed_lines = cls.config_text.split('\n')

    def setUp(self):
        self.obj = WindowsTerminalConfigFile(path=self.DEFAULT_CONFIG_PATH)
        self.config = self.obj.config
        self.obj.reload()

    def _choose_config_file(self, filename):
        path = os.path.join(self.TESTFILES_PATH, filename)
        self.obj = WindowsTerminalConfigFile(path=path)
        self.config = self.obj.config
        with open(path, 'r') as file:
            return file.read()

    def _switch_to_profile_with_schemes(self):
        return self._choose_config_file('profile_with_schemes.json')

    def _switch_to_profile_with_set_schemes(self):
        return self._choose_config_file('schemes_with_set_scheme.json')

    def assertFileEqualString(self, filename, text):
        with open(filename) as file:
            written_text = file.read()
            # print('File:')
            # print(written_text.strip())
            # print('String:')
            # print(text.strip())
            self.assertEqual(text.strip(), written_text.strip())

    def assertActiveScheme(self, scheme, profile):
        gcs = self.config.get_current_scheme
        self.assertIsNotNone(profile)
        self.assertEqual(gcs(profile=profile), scheme)

    def assertDefaultScheme(self, scheme):
        gcs = self.config.get_current_scheme
        self.assertEqual(gcs(profile=None), scheme)

    def test_fix_formatting(self):
        fixed_text = self.obj.fix_formatting(self.config_text)
        self.assertNotRegex(fixed_text, r':\s*\[ *\]')
        self.assertNotRegex(fixed_text, r':\s*\{ *\}')
        self.assertNotRegex(fixed_text, r":\s*\n\s*([\[\{])")

    def test_load_and_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_path = os.path.join(tmpdir, 'test_load_and_write.json')
            self.obj.test_write(path=test_path)
            self.assertFileEqualString(test_path, self.fixed_text)

            new_config_text = self._switch_to_profile_with_schemes()
            self.obj.test_write(path=test_path)
            self.assertFileEqualString(test_path, new_config_text)

    def test_get_schemes(self):
        schemes = self.config.schemes()
        self.assertEqual(schemes, [])
        self._switch_to_profile_with_schemes()
        schemes = self.config.schemes()
        self.assertEqual(schemes, ['Monokai Soda', '3024 Day', 'AlienBlood'])

    def test_get_current_scheme(self):
        gcs = self.config.get_current_scheme
        self.assertIsNone(gcs())
        self.assertIsNone(gcs('Windows PowerShell'))

        self._switch_to_profile_with_set_schemes()
        # gcs = self.obj.get_current_scheme
        self.assertDefaultScheme('Monokai Soda')
        self.assertActiveScheme(None, profile='Windows PowerShell')
        self.assertActiveScheme('3024 Day', profile='cmd')

    def test_set_scheme(self):
        with self.assertRaises(Exception):
            self.config.set_scheme('Monokai Soda')

        self._switch_to_profile_with_schemes()
        self.assertDefaultScheme(None)
        self.assertActiveScheme(None, 'cmd')

        self.config.set_scheme('3024 Day')
        self.assertDefaultScheme('3024 Day')
        self.assertActiveScheme(None, 'cmd')

        self.config.set_scheme('Monokai Soda', 'cmd')
        self.assertDefaultScheme('3024 Day')
        self.assertActiveScheme('Monokai Soda', 'cmd')

    # def test_next_scheme(self):
    #     self.assertIsNone(self.obj._next_scheme())

    #     self._switch_to_profile_with_schemes()
    #     next_scheme = self.obj._next_scheme

    #     self.obj.set_scheme('AlienBlood')
    #     self.assertActiveScheme('AlienBlood')
    #     self.assertEqual(next_scheme(), 'Monokai Soda')
    #     self.assertEqual(next_scheme(backwards=True), '3024 Day')

    #     self.obj.set_scheme('Monokai Soda')
    #     self.assertActiveScheme('Monokai Soda')
    #     self.assertEqual(next_scheme(), '3024 Day')
    #     self.assertEqual(next_scheme(backwards=True), 'AlienBlood')

    # def test_add_scheme(self):
    #     self.assertEqual(len(self.obj.schemes), 0)
    #     self.assertEqual(len(self.obj.config['schemes']), 0)

    #     self.obj.add_scheme_to_config(self.SCHEME_EXAMPLE)
    #     self.obj.add_scheme_to_config(self.SCHEME_EXAMPLE)

    #     schemes = self.obj.schemes
    #     scheme_dict = self.obj.config['schemes']
    #     self.assertEqual(len(schemes), 1)
    #     self.assertEqual(len(scheme_dict), 1)
    #     self.assertEqual(scheme_dict[0]['name'], '3024 Day')
    #     self.assertEqual(schemes[0], '3024 Day')

    # def test_add_scheme_and_write(self):
    #     self.obj.add_scheme_to_config(self.SCHEME_EXAMPLE)
    #     add_schemes_testfile = TestWindowsTerminalConfigFile._read_test_file('add_schemes.json')
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         test_path = os.path.join(tmpdir, 'test_add_scheme.json')
    #         self.obj.test_write(path=test_path)
    #         self.assertFileEqualString(test_path, add_schemes_testfile)

    # def test_write_new_scheme(self):
    #     self._choose_config_file('schemes_without_set_scheme.json')
    #     self.obj.set_scheme('Monokai Soda')
    #     self.assertActiveScheme('Monokai Soda')
    #     self.obj.set_scheme('3024 Day', profile="cmd")
    #     self.assertActiveScheme('3024 Day', profile="cmd")
    #     add_schemes_testfile = TestWindowsTerminalConfigFile._read_test_file('schemes_with_set_scheme.json')
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         test_path = os.path.join(tmpdir, 'test_write_new_scheme.json')
    #         self.obj.test_write(path=test_path)
    #         self.assertFileEqualString(test_path, add_schemes_testfile)

    # def test_cycle_scheme(self):
    #     self._switch_to_profile_with_schemes()
    #     self.obj.cycle_schemes()
    #     add_schemes_testfile = TestWindowsTerminalConfigFile._read_test_file('schemes_with_set_scheme.json')
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         test_path = os.path.join(tmpdir, 'test_cycle_scheme.json')
    #         self.obj.test_write(path=test_path)
    #         self.assertFileEqualString(test_path, add_schemes_testfile)
