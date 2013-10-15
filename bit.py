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

__paths__ = {}

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

def mkdir(path_to, new_dir):
    """
    Create all paths beyond
    path_to and new_dir
    """
    if __paths__.get(new_dir, False):
        return
    dr = new_dir.replace(path_to, '', 1)
    l = dr.split(os.path.sep)
    for x in filter(len, l):
        path_to = os.path.join(path_to, x)
        if not os.path.exists(path_to):
            os.mkdir(path_to)
            __paths__[path_to] = True

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
            end = path_from.split('.')[-1]
            if end in lst_for_sox:
                change_bitrate(path_from, path_to,
                                bitrate, verbose)
            else:
                print('Invalid filetype: {}'.format(end))
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
                mkdir(path_to, ndir)
            if os.path.exists(fd):
                continue
            end = fs.split('.')[-1]
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