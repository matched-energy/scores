#!/bin/zsh

source venv/bin/activate
export PYTHONPATH=${PYTHONPATH}:$DEV/matched

# export DROPBOX_DATA=/Users/jbloggs/Dropbox/data
export MATCHED_DATA=${DROPBOX_DATA}/matched-data