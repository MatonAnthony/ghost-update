#!/usr/bin/env python3

import sys
import os
import argparse
import re
import linecache
import subprocess
import zipfile
import shutil
import shlex

# Argument parser
parser = argparse.ArgumentParser(description='Upgrade a ghost powered blog')
parser.add_argument('path', metavar='/path/to/ghost', type=str,
                    help='The path to your ghost instance')
parser.add_argument('-a', '--after', help='Add a command to be run after the'
                                          'end of this script',
                    metavar='"command to run"')
arguments = parser.parse_args()

arguments.path = arguments.path
packageJson = os.path.join(arguments.path, 'package.json')
tmpPath = '/tmp/ghost'

if os.path.exists(arguments.path) and os.path.isdir(arguments.path):
    if os.path.exists(packageJson):
        pattern = re.compile('"name": "ghost"')
        line = linecache.getline(packageJson, 2)

        if re.search(pattern, line) is not None:
            print("Ghost instance found")
            # It's a ghost instance
            # Download ghost latest archive
            print("Downloading ghost latest version")
            subprocess.run(["curl", "-Lko", "/tmp/ghost-latest.zip",
                            "https://ghost.org/zip/ghost-latest.zip"])
            # Unzip files
            print("Unzipping ghost-latest archive")
            zip = zipfile.ZipFile('/tmp/ghost-latest.zip')
            zip.extractall(tmpPath)

            # Delete old files
            print("Removal of deprecated files")
            os.remove(os.path.join(arguments.path, 'index.js'))
            os.remove(os.path.join(arguments.path, 'package.json'))
            os.remove(os.path.join(arguments.path, 'npm-shrinkwrap.json'))
            shutil.rmtree(os.path.join(arguments.path, 'core'))

            # Putting new files in place of the old one
            print("Copying new files")
            shutil.copytree(os.path.join(tmpPath, 'core'),
                            os.path.join(arguments.path, 'core'), True)
            shutil.copy2(os.path.join(tmpPath, 'index.js'), arguments.path)
            shutil.copy2(os.path.join(tmpPath, 'package.json'), arguments.path)
            shutil.copy2(os.path.join(tmpPath, 'npm-shrinkwrap.json'),
                         arguments.path)

            # Run npm to ensure dependencies are upgraded
            # Also displaying output from npm
            print("Running npm install --production")
            with subprocess.Popen(['npm', 'install', '--production'],
                                  stdout=subprocess.PIPE, bufsize=1,
                                  universal_newlines=True) as process:
                for line in process.stdout:
                    print(line)

            if arguments.after is None:
                # Ghost upgrade is finished
                print("--- Upgrade finished, don't forget to re-run "
                      "the daemon ---")
                exit(0)
            else:
                # Run the command asked by --after
                with subprocess.Popen(shlex.split(arguments.after),
                                      stdout=subprocess.PIPE, bufsize=1,
                                      universal_newlines=True) as process:
                    for line in process.stdout:
                        print(line)

        else:
            print("This is not a ghost instance")
            sys.exit(1)

    else:
        print("Invalid path")
        sys.exit(1)
