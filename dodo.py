from os import path
from pathlib import Path


def _source_files():
    return (
        list(Path(path.join('.', 'windows_terminal_scheme_manager')).glob('**/*.py')) +
        list(Path(path.join('.', 'tests')).glob('**/*.py')) +
        list(Path(path.join('.', 'tests')).glob('**/*.json'))
        )


def task_test():
    return {
        'file_dep': _source_files(),
        'actions': ['coverage run -m unittest discover']
    }


def task_build_msi():
    return {
        'file_dep': _source_files(),
        'targets': [path.join('.', 'dist',
                              'windows_terminal_scheme_manager-0.2.win-amd64.msi')],
        'actions': ['setup.py bdist_msi']
    }


def task_build_onefile():
    return {
        'file_dep': _source_files(),
        'targets': [path.join('.', 'dist', 'wtsm.exe')],
        'actions': [
            'pyinstaller --onefile \
            --noupx\
            --hidden-import="pkg_resources.py2_warn" \
            --name wtsm \
            {}\
            '.format(path.join(
                '.', 'windows_terminal_scheme_manager', 'scheme_manager.py'
            ))]
    }


def task_build_onefile_upx():
    task = task_build_onefile()
    task['targets'] = [path.join('.', 'dist', 'wtsm_upx.exe')]
    task['actions'][0] = task['actions'][0]\
        .replace('--noupx', '\
        --upx-dir=C:\\Users\\Gordin\\Apps\\upx-3.96-win64 \
        --upx-exclude=vcruntime140.dll \
        --upx-exclude=python38.dll \
    ').replace('--name wtsm', '--name wtsm_upx')
    return task
