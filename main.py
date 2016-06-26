#!/usr/bin/env python3

import sys
import os.path
import re
import linecache
import subprocess
import urllib.request
import zipfile

if len(sys.argv) != 2:
    print ('''Invalid usage :
        Usage : ghost-update /path/to/your/ghost
        ''')
    sys.exit(1)

ghostPath = sys.argv[1];
packageJson = os.path.join(ghostPath, 'package.json')

if os.path.exists(ghostPath) and os.path.isdir(ghostPath):
    if os.path.exists(packageJson):
        pattern = re.compile('"name": "ghost"')
        line = linecache.getline(packageJson, 2)

        if re.search(pattern, line) != None:
            # It's a ghost instance
            # Download ghost latest archive
            localName, headers = urllib.request.urlretrieve('https://ghost.org/zip/ghost-latest.zip')
            zip = ZipFile(localName)
            zip.extractall('/tmp/ghost')

        else:
            print ("This is not a ghost instance")
            sys.exit(1)

    else:
        print ("Invalid path")
        sys.exit(1)

