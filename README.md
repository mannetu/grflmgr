# grflmgr
Version 0.3 

## Change Log
* Data is stored in SQLite database

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