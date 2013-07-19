#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess as sp
import sys
import shutil
__version__ = '1.0.3'

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
        except KeyboardInterrupt:
            print("The file may be corrupt: {}".\
                    format(fs))
            sys.exit(1)
        except Exception as e:
            print(e)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path",
                        help="path with original sound files (required)")
    parser.add_argument("-d", "--dest",
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
    try:
        if path_from:
            go(path_from, dest, bitrate, verbose)
        else:
            print("Please, set path with files!")
    except KeyboardInterrupt:
        print("Stopped manually")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()