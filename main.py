#!/usr/bin/env python3

import os
import argparse
import re
import linecache
import subprocess
import zipfile
import shutil
import shlex


def arguments():
    """ Manage argument parsing """
    parser = argparse.ArgumentParser(
        description='Upgrade a ghost powered blog')
    parser.add_argument('path', metavar='/path/to/ghost', type=str,
                        help='The path to your ghost instance')
    parser.add_argument('-a', '--after',
                        help='Add a command to be run after the end of this '
                             'script',
                        metavar='"command to run"')
    arguments = parser.parse_args()
    return arguments


def is_ghost_instance(path):
    """ Check if the path is a ghost instance """
    if os.path.exists(path) and os.path.isdir(path):
        package_json = os.path.join(path, 'package.json')
        if os.path.exists(package_json):
            pattern = re.compile('"name": "ghost"')
            line = linecache.getline(package_json, 2)

            if re.search(pattern, line) is not None:
                return True
            else:
                return False


def prepare_update(tmpPath):
    """ Download and unzip ghost in a temporary location """
    print("Downloading ghost latest version")
    print("Downloading ghost latest version")
    subprocess.run(["curl", "-Lko", "/tmp/ghost-latest.zip",
                    "https://ghost.org/zip/ghost-latest.zip"])
    # Unzip files
    print("Unzipping ghost-latest archive")
    zip = zipfile.ZipFile('/tmp/ghost-latest.zip')
    zip.extractall(tmpPath)


def apply_core_update(tmpPath, ghostPath):
    """ Apply ghost update """
    # Delete old files
    print("Removal of deprecated files")
    os.remove(os.path.join(ghostPath, 'index.js'))
    os.remove(os.path.join(ghostPath, 'package.json'))
    os.remove(os.path.join(ghostPath, 'npm-shrinkwrap.json'))
    shutil.rmtree(os.path.join(ghostPath, 'core'))

    # Putting new files in place of the old one
    print("Copying new files")
    shutil.copytree(os.path.join(tmpPath, 'core'),
                    os.path.join(ghostPath, 'core'), True)
    shutil.copy2(os.path.join(tmpPath, 'index.js'), ghostPath)
    shutil.copy2(os.path.join(tmpPath, 'package.json'), ghostPath)
    shutil.copy2(os.path.join(tmpPath, 'npm-shrinkwrap.json'),
                 ghostPath)


def npm_update():
    """ Run npm to ensure dependencies are also upgraded """
    # Run npm to ensure dependencies are upgraded
    # Also displaying output from npm
    print("Running npm install --production")
    with subprocess.Popen(['npm', 'install', '--production'],
                          stdout=subprocess.PIPE, bufsize=1,
                          universal_newlines=True) as process:
        for line in process.stdout:
            print(line)


def after(command):
    """ Run the command asked by --after """
    with subprocess.Popen(shlex.split(command),
                          stdout=subprocess.PIPE, bufsize=1,
                          universal_newlines=True) as process:
        for line in process.stdout:
            print(line)


def run():
    """ Main function of the script """
    tmp_path = '/tmp/ghost'
    args = arguments()
    if is_ghost_instance(args.path):
        prepare_update(tmp_path)
        apply_core_update(tmp_path, args.path)
        npm_update()

        if args.after is None:
            # Ghost upgrade is finished
            print("--- Upgrade finished, don't forget to re-run "
                  "the daemon ---")
        else:
            after(args.after)

        exit(0)
    else:
        print("This is not a ghost instance")
        exit(1)

if __name__ == '__main__':
    run()
