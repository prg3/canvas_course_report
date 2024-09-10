#!/usr/bin/env bash

DOW=$(date +%u)

if [ -f "today.pickle" ] ; then
    cp -f today.pickle yesterday.pickle
    if [ $DOW -eq 1 ] ; then
        cp -f today.pickle lastweek.pickle
    fi
fi

python3 scraper.py
