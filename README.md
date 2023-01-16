# grflmgr
Version 0.2 

## Change Log
* Filepaths in config.ini based on user's home directory
* Database directory is automatically created if not yet existing

## Install
    git clone https://www.github.com/mannetu/grflmgr
    cd grflmgr 
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt

Provide path to your folder for activity files import in `config.ini`

Currently only `.fit` and `.gpx` files are supported.

## Run
    python3 grflmgr/app.py