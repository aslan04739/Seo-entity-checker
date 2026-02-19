#!/bin/bash
# SEO Crawler Desktop Launcher for macOS

cd "$(dirname "$0")"
/usr/bin/python3 analyze2.py &
disown
