import unittest
import os
from multiprocessing import Process
from windows_terminal_scheme_manager.downloader import WindowsTerminalSchemeDownloader
import http.server
import socketserver


def serve_schemes_zip():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    os.chdir(os.path.join('tests', 'windows_terminal_scheme_manager'))
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()


class TestWindowsTerminalSchemeDownloader(unittest.TestCase):
    TEST_ZIP = 'iTerm2-Color-Schemes-only-windowsterminal.zip'
    TEST_URL = 'http://localhost:8000/{}'.format(TEST_ZIP)
    SCHEME_PATH = os.path.join('iTerm2-Color-Schemes-master', 'windowsterminal')

    def setUp(self):
        self.downloader = WindowsTerminalSchemeDownloader(url=self.TEST_URL)

    def test_everything(self):
        p = Process(target=serve_schemes_zip)
        p.start()
        zip_file = self.downloader.download_repo()
        p.terminate()
        tmpdir, scheme_filenames = self.downloader.unpack_schemes(zip_file)
        self.assertEqual(len(scheme_filenames), 211)
        self.assertEqual(scheme_filenames[0], '3024 Day.json')
        self.assertEqual(scheme_filenames[-1], 'synthwave.json')

        schemes_path = os.path.join(tmpdir, self.SCHEME_PATH)
        new_schemes = self.downloader.get_all_schemes(schemes_path, scheme_filenames)
        self.assertEqual(len(new_schemes), 211)
        self.assertEqual(len(str(new_schemes)), 92459)
        self.assertEqual(new_schemes[0]['name'], '3024 Day')
