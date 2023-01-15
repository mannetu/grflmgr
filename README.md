# grflmgr
Version 0.1

## Install
    git clone https://www.github.com/mannetu/grflmgr
    cd grflmgr 
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    mkdir data/maptiles

Create the directory for dropping activities to import or provide your own activities folder in `config.ini`. Currently only `.fit` and `.gpx` files are supported.

    mkdir data/activities

## Run
    python3 grflmgr/app.py