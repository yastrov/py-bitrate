#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess as sp
import sys
import shutil
import traceback
__version__ = '1.0.6'

def ex(cmd):
    """
    Execute comand (must be a string) in shell.
    """
    assert type(cmd) != list
    with sp.Popen(cmd, shell=True,
                    stdout=sp.PIPE,
                    stdin=sp.PIPE) as p:
        #Official sp.Popen.wait() is prototype
        try:
            out, err = p.communicate()
            return out, err
        except OSError as e:
            p.kill()
            p.wait()
            print("Execution failed:", e)
            return None

def change_bitrate(file_source, file_dest,
                    bitrate, verbose=False):
    """
    Change bitrate with SoX audio convert utility.
    """
    cmd_ = 'sox "{file_source}" -C {bitrate} "{file_dest}"'
    cmd_= cmd_.format(**{'file_source':file_source,
                        'bitrate':bitrate,
                        'file_dest':file_dest })
    if verbose:
        print(cmd_)
    out, err = ex(cmd_)
    if verbose and out:
        print(out, err)   

def walk(path_from, path_to):
    """
    Walk on path with name path_from.
    path_to - is path for new files.
    (It is best place for construct new path.)
    Return file_source, file_dest and new_dir.
    file_dest - filename for copy of file_source.
    new_dir - path for file_source.
    """
    if not os.path.isdir(path_from):
        print('Wrong path: {}'.format(path_from))
        sys.exit(1)
    path_from = os.path.abspath(path_from)
    path_to = os.path.abspath(path_to)
    for root, dirs, files in os.walk(path_from):
        new_dir = root.replace(path_from, path_to, 1)
        for name in sorted(files):
            file_source = os.path.join(root, name)
            file_dest = os.path.join(new_dir, name)
            yield (file_source, file_dest, new_dir)

def go(path_from, path_to, bitrate, verbose=False):
    """
    Logick main function for programm.
    path_from - path with audio files for convert.
    path_to - new path for save result audio files.
    bitrate - bitrate for new file.
    verbose - set True for output every command.
    """
    #Single file
    if os.path.isfile(path_from):
        try:
            change_bitrate(path_from, path_to,
                                bitrate, verbose)
        except OSError as e:
            print("Execution failed:", e)
            print("Error in copy:\n{}\nto:\n{}".\
                    format(path_from, path_to))
        except KeyboardInterrupt:
            print("The file may be corrupt: {}".\
                    format(path_to))
            sys.exit(1)
        except Exception as e:
            print(e)
        sys.exit()
    # Path
    if not os.path.exists(path_to):
        os.mkdir(path_to)
    for fs, fd, ndir in walk(path_from, path_to):
        try:
            if not os.path.exists(ndir):
                os.mkdir(ndir)
            if os.path.exists(fd):
                continue
            elif not fs.endswith('.mp3'):
                shutil.copy2(fs, fd)
            else:
                change_bitrate(fs, fd,
                                bitrate, verbose)
        except OSError as e:
            print("Execution failed:", e)
            print("Error in copy:\n{}\nto:\n{}".\
                    format(fs, fd))
            traceback.print_exc()
        except KeyboardInterrupt:
            print("The file may be corrupt: {}".\
                    format(fs))
            sys.exit(1)
        except Exception as e:
            print(e)
            traceback.print_exc()

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path",
                        help="path with original sound files (required)")
    parser.add_argument("-d", "--dest",
                        help="destination path for converted sound files")
    parser.add_argument("-b", "--bitrate",
                        default=32, help="bitrate (default: 64)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose output")
    parser.add_argument("--version", action="store_true",
                        help="print version")
    args = parser.parse_args()
    if args.version:
        print(__version__)
    if not args.dest:
        if os.path.isfile(args.path):
            l = args.path.split('.')
            s = l[-2] + "_{}".format(args.bitrate)
            l[-2] = s
            dest = '.'.join(l)
        else:
            dest = "{}_{}".format(args.path,\
                                    args.bitrate)
    else:
        dest = args.dest
    try:
        if path_from:
            go(path_from, dest,
                args.bitrate,
                args.verbose)
        else:
            print("Please, set path with files!")
    except KeyboardInterrupt:
        print("Stopped manually")
    except Exception as e:
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    main()