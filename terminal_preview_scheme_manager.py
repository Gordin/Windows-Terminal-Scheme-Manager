import logging
from preview_scheme_manager.downloader import WindowsTerminalSchemeDownloader
from preview_scheme_manager.terminal_config import WindowsTerminalConfigFile

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = WindowsTerminalConfigFile()
    config.cycle_schemes("Arch")

def download_schemes():
    downloader = WindowsTerminalSchemeDownloader()
    # downloader.download_and_add_schemes_to_config(repo_path='C:\\Users\\Gordin\\AppData\\Local\\Temp\\tmpyteiipoy\\', keep_repo=True)
    downloader.download_and_add_schemes_to_config(keep_repo=True)
    # input("Press any key to exit")
