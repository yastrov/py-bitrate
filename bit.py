#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from optparse import OptionParser

def ex(cmd):
    """Execute comand."""
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read().strip()
    return out

def change_bitrate(file_source, file_dest, bitrate):
    """Change bitrate."""
    cmd_ = 'sox  "{file_source}" -C {bitrate} "{file_dest}"'
    cmd_= cmd_.format(**{'file_source':file_source,
                        'bitrate':bitrate,
                        'file_dest':file_dest })
    print(cmd_)
    ex(cmd_)

def walk(path_from, path_to, bitrate):
        """Walk on path and convert """
        path_from = os.path.abspath(path_from)
        path_to = os.path.abspath(path_to)
        if not os.path.isdir(path_from):
            raise Exception('Wrong path')
        for root, dirs, files in os.walk(path_from):
            new_dir = root.replace(path_from, path_to, 1)
            for name in files:
                if not name.endswith('.mp3'):
                    continue
                if not os.path.exists(new_dir):
                    os.mkdir(new_dir)
                file_source = os.path.join(root, name)
                file_dest = os.path.join(new_dir, name)
                if os.path.exists(file_dest):
                    continue
                change_bitrate(file_source, file_dest, bitrate)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-s", "--path-source", dest="path_from",
                    help="path with original sound files")
    parser.add_option("-d", "--path-dest", dest="path_to",
                    default = "null",
                    help="destination path for converted sound files")
    parser.add_option("-b", "--bitrate", dest="bitrate",
                    default=64, help="bitrate (default: 64)")
    (options, args) = parser.parse_args()
    if options.path_to == "null":
        options.path_to = "%s_%s" %(options.path_from,\
                                options.bitrate)
    walk(options.path_from, options.path_to, options.bitrate)