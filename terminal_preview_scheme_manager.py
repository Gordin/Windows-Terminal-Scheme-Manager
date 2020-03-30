#!/usr/bin/env python3

import logging
from preview_scheme_manager.downloader import WindowsTerminalSchemeDownloader
from preview_scheme_manager.terminal_config import WindowsTerminalConfigFile
from preview_scheme_manager.screen import SchemeManager
import click

@click.group()
@click.option('--debug', default='ERROR', help='sets debug level (INFO, WARNING, ERROR)')
def cli(debug='ERROR'):
    logging.basicConfig(level=getattr(logging, debug))

@click.command()
# @click.argument('list')
def list():
    config = WindowsTerminalConfigFile()
    schemes = config.get_schemes()
    current_scheme = config.get_current_scheme()
    click.echo('Current Scheme: {}'.format(current_scheme))
    click.echo('Available Schemes: {}'.format(', '.join(schemes)))

@click.command()
@click.option('--profile', default=None, help='name of profile to change scheme for. Defaults to all profiles')
def next_scheme(profile):
    config = WindowsTerminalConfigFile()
    config.cycle_schemes(profile)
    config.write()
    current_scheme = config.get_current_scheme(profile)
    click.echo('New scheme: {}'.format(current_scheme))

@click.command()
@click.option('--profile', default=None, help='name of profile to change scheme for. Defaults to all profiles')
def previous_scheme(profile):
    config = WindowsTerminalConfigFile()
    config.cycle_schemes(profile, backwards=True)
    config.write()
    current_scheme = config.get_current_scheme(profile)
    click.echo('New scheme: {}'.format(current_scheme))

@click.command()
@click.argument("scheme")
def set(scheme):
    config = WindowsTerminalConfigFile()
    config.set_scheme(scheme)
    config.write()
    current_scheme = config.get_current_scheme(profile)
    click.echo('New scheme: {}'.format(current_scheme))


@click.command()
def add_all_schemes():
    downloader = WindowsTerminalSchemeDownloader()
    downloader.download_and_add_schemes_to_config(keep_repo=True)

@click.command()
def ui():
    ui = SchemeManager()
    ui.run()

cli.add_command(locals()['list'])
cli.add_command(next_scheme)
cli.add_command(previous_scheme)
cli.add_command(locals()['set'])
cli.add_command(add_all_schemes)
cli.add_command(ui)

if __name__ == "__main__":
    cli()