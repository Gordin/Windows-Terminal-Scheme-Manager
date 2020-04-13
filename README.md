## Installation

### Windows
If you have Python 3.8 installed, use the latest realese Installer.
Otherwise download `wtsm.exe` and run it directly, it includes Python

## Usage

Install requirements with `pipenv install` (`--dev` to run tests/debug)
To run from source: `pipenv run python .\windows_terminal_scheme_manager\scheme_manager.py`

Download and add a lot of schemes to your config with `add-all-schemes`
Open ui to skip through schemes with `ui` or use cli commands

## Tests

Run the tests with `pipenv run doit test`
To debug with ipdb use this instead `pipenv run coverage run -m unittest discover`

## Building

Run `pipenv run doit`