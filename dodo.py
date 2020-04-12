from os import path
from pathlib import Path


def _source_files():
    return list(Path(path.join('.', 'windows_terminal_scheme_manager'))
                .glob('**/*.py'))


def task_build_onefile():
    return {
        'file_dep': _source_files(),
        'targets': [path.join('.', 'dist', 'scheme_manager.exe')],
        'actions': [
            'pyinstaller --onefile --hidden-import="pkg_resources.py2_warn" {}'
            .format(path.join(
                '.', 'windows_terminal_scheme_manager', 'scheme_manager.py'
            ))]
    }


def task_test():
    return {
        'file_dep': _source_files(),
        'actions': ['coverage run -m unittest discover']
    }
