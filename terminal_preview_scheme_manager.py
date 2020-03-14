#!/usr/bin/env python3

import logging
from preview_scheme_manager.downloader import WindowsTerminalSchemeDownloader
from preview_scheme_manager.terminal_config import WindowsTerminalConfigFile
from preview_scheme_manager.screen import SchemeManager
import click

@click.group()
def cli():
    pass

@click.command()
# @click.argument('list')
def list():
    config = WindowsTerminalConfigFile()
    schemes = config.get_schemes()
    current_scheme = config.get_current_scheme()
    # import ipdb; ipdb.set_trace()
    click.echo('Current Scheme: {}'.format(current_scheme))
    click.echo('Available Schemes: {}'.format(', '.join(schemes)))

@click.command()
def cycle():
    config = WindowsTerminalConfigFile()
    config.cycle_schemes("Arch")
    config.write()
    click.echo('Cycled scheme.')

@click.command()
def add_all_schemes():
    downloader = WindowsTerminalSchemeDownloader()
    downloader.download_and_add_schemes_to_config(keep_repo=True)

@click.command()
def ui():
    ui = SchemeManager()
    ui.run()

cli.add_command(locals()['list'])
cli.add_command(cycle)
cli.add_command(add_all_schemes)
cli.add_command(ui)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli()

def download_schemes():
    downloader = WindowsTerminalSchemeDownloader()
    # downloader.download_and_add_schemes_to_config(repo_path='C:\\Users\\Gordin\\AppData\\Local\\Temp\\tmpyteiipoy\\', keep_repo=True)
    downloader.download_and_add_schemes_to_config(keep_repo=True)
    # input("Press any key to exit")
