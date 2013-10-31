#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import subprocess as sp
import sys
import shutil
import traceback
__version__ = '1.0.8'

lst_for_sox = """8svx aif aifc aiff aiffc al amb amr-nb amr-wb anb 
au avr awb caf cdda cdr cvs cvsd cvu dat dvms f32 f4 f64 
f8 fap flac fssd gsm gsrt hcom htk ima ircam la lpc lpc10 
lu mat mat4 mat5 maud mp2 mp3 nist ogg paf prc pvf raw s1 
s16 s2 s24 s3 s32 s4 s8 sb sd2 sds sf sl sln smp snd 
sndfile sndr sndt sou sox sph sw txw u1 u16 u2 u24 u3 u32 
u4 u8 ub ul uw vms voc vorbis vox w64 wav wavpcm wv wve xa
 xi""".split()

def ex(cmd):
    """
    Execute comand (must be a string) in shell.
    """
    assert isinstance(cmd, str)
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
    if out is not b'' or \
        err is not None:
        print(out, err)   

def walk(path_from, path_to):
    """
    Walk on path with name path_from.
    path_to - is path for new files.
    (It is best place for construct new path.)
    Return file_source, file_dest and new_dir.
    file_dest - filename for copy of file_source.
    """
    if not os.path.isdir(path_from):
        msg = 'Wrong path: {}'.format(path_from)
        raise Exception(msg)
    path_from = os.path.abspath(path_from)
    path_to = os.path.abspath(path_to)
    for root, dirs, files in os.walk(path_from):
        new_dir = root.replace(path_from, path_to, 1)
        for name in sorted(files):
            file_source = os.path.join(root, name)
            file_dest = os.path.join(new_dir, name)
            yield (file_source, file_dest)

def mkdir(new_dir):
    """
    Create new_dir and all prev dirs.
    """
    _path = os.path.dirname(new_dir)
    if os.path.exists(_path):
        return
    _p_list = []
    if _path.endswith(os.path.sep):
        _path = _path[:-1] 
    while not os.path.exists(_path):
        _p_list.append( os.path.basename(_path) )
        _path = os.path.dirname(_path)
    _p_list.reverse()
    while _p_list:
        _path = os.path.join(_path, _p_list.pop(0))
        os.mkdir(_path)

def change_file(fs, fd, bitrate, verbose=False):
    """
    Change bitrate for one file.
    """
    try:
        if os.path.exists(fd):
            return
        end = os.path.splitext(fs)[1][1:]
        if end in lst_for_sox:
            change_bitrate(fs, fd,
                            bitrate, verbose)
        else:
            shutil.copy2(fs, fd)
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

def go(path_from, path_to, bitrate, verbose=False):
    """
    Logick main function for programm.
    path_from - path with audio files for convert.
    path_to - new path for save result audio files,
    must be in exist directory.
    (Or filename, if path_from is filename.)
    bitrate - bitrate for new file.
    verbose - set True for output every command.
    """
    #Single file
    if os.path.isfile(path_from):
        change_file(path_from, path_to,
            bitrate, verbose)
        sys.exit()
    # Path
    for fs, fd in walk(path_from, path_to):
        mkdir(fd)
        change_file(fs, fd, bitrate, verbose)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Convert audiofiles with SoX.')
    parser.add_argument("path",
                        help="path with original sound files (required)")
    parser.add_argument("-d", "--dest",
                        help="destination path for converted sound files")
    parser.add_argument("-b", "--bitrate",
                        default=32, help="bitrate (default: 64)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="verbose output")
    parser.add_argument("--version", action='version',
                        version='%(prog)s {}'.format(__version__),
                        help="print version")
    args = parser.parse_args()
    if args.dest:
        dest = args.dest
    else:
        if os.path.isfile(args.path):
            l = args.path.split('.')
            s = l[-2] + "_{}".format(args.bitrate)
            l[-2] = s
            dest = '.'.join(l)
        else:
            dest = "{}_{}".format(args.path,\
                                    args.bitrate)
    try:
        go(args.path, dest,
                args.bitrate,
                args.verbose)
    except KeyboardInterrupt:
        print("Stopped manually")
    except Exception as e:
        print(e)
        traceback.print_exc()

if __name__ == "__main__":
    main()