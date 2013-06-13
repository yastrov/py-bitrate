#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
__version__ = '1.0.1'

def ex(cmd):
    """Execute comand."""
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read().strip()
    return out

def change_bitrate(file_source, file_dest, bitrate, verbose=False):
    """Change bitrate."""
    cmd_ = 'sox  "{file_source}" -C {bitrate} "{file_dest}"'
    cmd_= cmd_.format(**{'file_source':file_source,
                        'bitrate':bitrate,
                        'file_dest':file_dest })
    if verbose:
        print(cmd_)
    ex(cmd_)

def walk(path_from, path_to, bitrate, verbose=False):
        """Walk on path and convert """
        if not os.path.isdir(path_from):
            print('Wrong path: {}'.format(path_from))
            return
        path_from = os.path.abspath(path_from)
        path_to = os.path.abspath(path_to)

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
                change_bitrate(file_source, file_dest,
                                bitrate, verbose)

def main():
    try:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("path",
                            help="path with original sound files")
        parser.add_argument("-d", "--dest",
                            #default = None,
                            help="destination path for converted sound files")
        parser.add_argument("-b", "--bitrate",
                            default=64, help="bitrate (default: 64)")
        parser.add_argument("-v", "--verbose", action="store_true",
                            help="verbose output")
        args = parser.parse_args()
        path_from = args.path
        if not args.dest:
            dest = "{}_{}".format(path_from,\
                                  args.bitrate)
        else:
            dest = args.dest
        bitrate = args.bitrate
        verbose = args.verbose
    except ImportError:
        from optparse import OptionParser
        parser = OptionParser()
        parser.add_option("path",
                        help="path with original sound files")
        parser.add_option("-d", "--dest", dest="dest",
                          default = "null",
                          help="destination path for converted sound files")
        parser.add_option("-b", "--bitrate", dest="bitrate",
                          default=64, help="bitrate (default: 64)")
        parser.add_option("-v", "--verbose", dest="verbose",
                          action="store_true", 
                          help="verbose output")
        (options, args) = parser.parse_args()
        path_from = args[0]
        if options.dest == "null":
            dest = "{}_{}".format(path_from,\
                                  options.bitrate)
        else:
            dest = options.dest
        path_from = options.source
        bitrate = options.bitrate
        verbose = options.verbose
    try:
        if path_from:
            walk(path_from, dest, bitrate, verbose)
    except KeyboardInterrupt:
        print("Stopped manually")

if __name__ == "__main__":
    main()