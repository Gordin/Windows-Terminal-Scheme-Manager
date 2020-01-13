## Usage

Before Using this make sure your profiles.json is formatted like this:
```
"key": [
    {
        "key": "value"
    }
],
```
and not like this:
```
"key":
    [
        {
            "key": "value"
        }
    ],
```
The default config is inconsistent with this and if you don't do this the script WILL mess up the position of the comments in the file

## Tests

Run the tests with `python -m unittest discover'

## Building
To build an executable with pyinstaller you need to install the dev version of pyinstaller because python 3.8 isn't supported yet

`pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip`

Build with

`pyinstaller --onedir .\terminal_preview_sheme_downloader.py`
