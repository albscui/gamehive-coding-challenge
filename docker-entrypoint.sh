#!/bin/bash

ENTRYPOINT="$*"

if [ -z "$ENTRYPOINT" ]; then
    
    python /gamehivechallengr/gamehivechallengr/app.py
else
    /bin/sh -c "$ENTRYPOINT"
fi
