#!/usr/bin/env python3

import logging
from windows_terminal_scheme_manager.downloader import WindowsTerminalSchemeDownloader
from windows_terminal_scheme_manager.terminal_config import WindowsTerminalConfigFile
from windows_terminal_scheme_manager.screen import SchemeManager
import click


@click.group()
@click.option('--debug', default='ERROR',
              help='sets debug level (INFO, WARNING, ERROR)')
def cli(debug='ERROR', config_file=None):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S',
        level=getattr(logging, debug)
        )


@click.command()
@click.option("--config_file", default=None,
              help='use a different file as Terminal config')
def list(config_file):
    config_file = WindowsTerminalConfigFile()
    config_file.config
    schemes = config_file.config.schemes()
    current_scheme = config_file.config.get_current_scheme()
    click.echo('Current Scheme: {}'.format(current_scheme))
    click.echo('Available Schemes: {}'.format(', '.join(schemes)))


@click.command()
@click.option("--config_file", default=None,
              help='use a different file as Terminal config')
@click.option('--profile', default=None,
              help='name of profile to change scheme for. Defaults to all profiles')
def next_scheme(profile, config_file):
    config_file = WindowsTerminalConfigFile()
    config_file.config.cycle_schemes(profile)
    config_file.write()
    current_scheme = config_file.config.get_current_scheme(profile)
    click.echo('New scheme: {}'.format(current_scheme))


@click.command()
@click.option("--config_file", default=None,
              help='use a different file as Terminal config')
@click.option('--profile', default=None,
              help='name of profile to change scheme for. Defaults to all profiles')
def previous_scheme(profile, config_file):
    config_file = WindowsTerminalConfigFile()
    config_file.config.cycle_schemes(profile, backwards=True)
    config_file.write()
    current_scheme = config_file.config.get_current_scheme(profile)
    click.echo('New scheme: {}'.format(current_scheme))


@click.command()
@click.option("--config_file", default=None,
              help='use a different file as Terminal config')
@click.argument("scheme")
def set(scheme):
    config_file = WindowsTerminalConfigFile()
    config_file.config.set_scheme(scheme)
    config_file.write()
    current_scheme = config_file.config.get_current_scheme()
    click.echo('New scheme: {}'.format(current_scheme))


@click.command()
@click.option("--config_file", default=None,
              help='use a different file as Terminal config')
def add_all_schemes(config_file):
    downloader = WindowsTerminalSchemeDownloader()
    downloader.download_and_add_schemes_to_config(
        keep_repo=True, config_file=config_file)


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
