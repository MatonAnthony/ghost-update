#!/usr/bin/env python3

import sys
import os
import re
import linecache
import subprocess
import zipfile
import shutil

if len(sys.argv) != 2:
    print ('''Invalid usage :
        Usage : ghost-update /path/to/your/ghost
        ''')
    sys.exit(1)

ghostPath = sys.argv[1];
packageJson = os.path.join(ghostPath, 'package.json')
tmpPath = '/tmp/ghost'

if os.path.exists(ghostPath) and os.path.isdir(ghostPath):
    if os.path.exists(packageJson):
        pattern = re.compile('"name": "ghost"')
        line = linecache.getline(packageJson, 2)

        if re.search(pattern, line) != None:
            print("Ghost instance found")
            # It's a ghost instance
            # Download ghost latest archive
            print("Downloading ghost latest version")
            subprocess.run(["curl", "-Lko", "/tmp/ghost-latest.zip",
                            "https://ghost.org/zip/ghost-latest.zip"])
            # Unzip files
            print("Unzipping ghost-latest archive")
            zip = ZipFile('/tmp/ghost-latest.zip')
            zip.extractall(tmpPath)

            # Delete old files
            print("Removal of deprecated files")
            os.remove(os.path.join(ghostPath, 'index.js'))
            os.remove(os.path.join(ghostPath, 'package.json'))
            os.remove(os.path.join(ghostPaht, 'npm-shrinkwrap.json'))
            shutil.rmtree(os.path.join(ghostPath, 'core'))

            # Putting new files in place of the old one
            print("Copying new files")
            shutil.copytree(os.path.join(tmpPath, 'core'), ghostPath, true)
            shutil.copy2(os.path.join(tmpPath, 'index.js'), ghostPath)
            shutil.copy2(os.path.join(tmpPath, 'package.json'), ghostPath)
            shutil.copy2(os.path.join(tmpPath, 'npm-shrinkwrap.json'), ghostPath)

            # Run npm to ensure dependencies are upgraded
            # Also displaying output from npm
            print("Running npm install --production")
            with Popen('npm install --production', stdout=PIPE, bufsize=1,
                       universal_newlines=True) as process :
                for line in process.stdout:
                    print(line)

            # Ghost upgrade is finished
            print("--- Upgrade finished, don't forget to re-run the daemon ---")
            exit(0)

        else:
            print ("This is not a ghost instance")
            sys.exit(1)

    else:
        print ("Invalid path")
        sys.exit(1)

