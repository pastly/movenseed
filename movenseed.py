#!/usr/bin/env python3
import os
import hashlib
import argparse

def hash_file(filename):
    #algo = hashlib.md5()
    algo = hashlib.sha1()
    blocksize = 2**20
    with open(filename, "rb") as file:
        while True:
            buf = file.read(blocksize)
            if not buf:
                break
            algo.update(buf)
    return algo.hexdigest()

def prework_do_files(filelist, root_dirname, size_info, hash_info):
    # filelist should contain absolute paths for best results
    for file in filelist:
        # may be unecessary check in most use cases, but this fixed python
        # trying to read a symbolic link to nowhere
        if os.path.isfile(file):
            file_size = os.path.getsize(file)
            file_hash = hash_file(file)
            file = os.path.realpath(file)[len(root_dirname)+1:]
            size_info.append(str(file_size) + "\t" + file + "\n")
            hash_info.append(file_hash + "\t" + file + "\n")

def prework_do_directory(dirname, root_dirname, size_info, hash_info):
    contained_files = []
    contained_directories = []
    for _, dirs, files in os.walk(dirname):
        contained_files.extend(files)
        contained_directories.extend(dirs)
    contained_files = [dirname+"/"+f for f in contained_files]
    contained_directories = [dirname+"/"+d for d in contained_directories]
    prework_do_files(contained_files, root_dirname, size_info, hash_info)
    for dir in contained_directories:
        #if os.path.isdir(dir):
        prework_do_directory(dir, root_dirname, size_info, hash_info)

def prework(passed_source_dirname, absolute_source_dirname):
    size_info = []
    hash_info = []
    prework_do_directory(passed_source_dirname, absolute_source_dirname, size_info, hash_info)
    with open(absolute_source_dirname+"/sizes.mns", "w") as size_outfile:
        for item in size_info:
            size_outfile.write(item)
    with open(absolute_source_dirname+"/hashes.mns", "w") as hash_outfile:
        for item in hash_info:
            hash_outfile.write(item)

def dispatch_prework(heres, torrentfile):
    if (not heres and torrentfile):
        print("Not yet implemented")
    elif (heres):
        for here in heres:
            prework(here, os.path.realpath(here))
    else:
        print("How did you get this far without getting caught?")

if __name__ == "__main__":
    descrip = '''
Advanced file linker.'''
    epil = '''
Prework requires either a torrentfile OR at least one here.
Postwork requires at least one here AND at least one there.'''
    parser = argparse.ArgumentParser(
        description=descrip,
        epilog=epil,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('-j', '--job', choices=['prework','postwork'], required=True)
    parser.add_argument('-H', '--here', metavar='dir', nargs='+')
    parser.add_argument('-T', '--there', metavar='dir', nargs='+')
    parser.add_argument('-t', '--torrent', metavar='torrentfile')
    args = parser.parse_args()
    if (args.job == 'prework'):
        if (not args.here and not args.torrent):
            print("Need --here or --torrent")
        elif (args.there):
            print("--there doesn't make sense with prework")
        else:
            dispatch_prework(args.here, args.torrent)
    else:
        if (not args.here or not args.there):
            print("Need --here and --there")
        elif (args.torrent):
            print("--torrent doesn't make sense with postwork")
        else:
            print(args.here)
            print(args.there)
    #a = "/tmp/testing/"
    #b = os.path.realpath(a)
    #prework(a, b)
