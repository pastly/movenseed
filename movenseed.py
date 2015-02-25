#!/usr/bin/env python3
import os
import hashlib
import argparse

global skip_filesize

# filename      path to a file whose contents should be digested
def hash_file(filename):
    # I have not done any testing on performance of various algos and blocksizes
    algo = hashlib.sha1()
    blocksize = 2**20
    with open(filename, "rb") as file:
        while True:
            buf = file.read(blocksize)
            if not buf:
                break
            algo.update(buf)
    return algo.hexdigest()

# filelist      list of filenames
# root_dirname  absolute path of a --here
# size_info     list of strings
# hash_info     list of strings
def prework_do_files(filelist, root_dirname, size_info, hash_info):
    for file in filelist:
        # may be unecessary check in most use cases, but this fixed python
        # trying to read a symbolic link to nowhere
        if os.path.isfile(file):
            file_size = os.path.getsize(file)
            file_hash = hash_file(file)
            # - convert file to relative path for storing in *.mns
            # - the path is relative to root_dirname (abs dir of a --here)
            # - root_dirname will not end in a slash, so must do +1 to remove
            # slash too
            file = os.path.realpath(file)[len(root_dirname)+1:]
            size_info.append(str(file_size) + "\t" + file + "\n")
            hash_info.append(file_hash + "\t" + file + "\n")

# dirname       a --here or subdir of --here
# root_dirname  absolute path of a --here
# size_info     list of strings
# hash_info     list of strings
def prework_do_directory(dirname, root_dirname, size_info, hash_info):
    contained_files = []
    contained_directories = []
    # get contained directories and files in dirname
    for item in os.listdir(dirname):
        # make item include dirname (not necessarily into absolute path)
        item = dirname + "/" + item
        if os.path.isfile(item):
            contained_files.append(item)
        elif os.path.isdir(item):
            contained_directories.append(item)
    # process any contained files in this dir
    prework_do_files(contained_files, root_dirname, size_info, hash_info)
    # then recursively process any contained dirs
    for dir in contained_directories:
        prework_do_directory(dir, root_dirname, size_info, hash_info)

# passed_source_dirname     a --here
def prework(passed_source_dirname):
    # lists to store strings in the following formats
    size_info = [] # "3212<tab>rel/path/from/here/to/file"
    hash_info = [] # "3668c223[...]<tab>rel/path/from/here/to/file"
    # start off the recursive processing of directories
    prework_do_directory(
        passed_source_dirname,
        os.path.realpath(passed_source_dirname),
        size_info,
        hash_info
     )
     # write all those lines to files in a --here
    with open(passed_source_dirname+"/sizes.mns", "w") as size_outfile:
        for item in size_info:
            size_outfile.write(item)
    with open(passed_source_dirname+"/hashes.mns", "w") as hash_outfile:
        for item in hash_info:
            hash_outfile.write(item)

# heres         list of --here's
# torrentfile   name of a torrentfile
def dispatch_prework(heres, torrentfile):
    # choose what type of prework to do based on what options exists
    if (not heres and torrentfile):
        print("Not yet implemented")
    elif (heres):
        for here in heres:
            prework(here)
    else:
        print("How did you get this far without getting caught?")

# filelist      list of filenames in a --there or a subdir of -there
# here          absolute path to a --here
# size_info     dictionary (key: filename, val: size) of files in --here
# hash_info     dictionary (key: filename, val: hash) of files in --here
def postwork_do_files(filelist, here, size_info, hash_info):
    for therefile in filelist:
        # try to find therefile's size in size_info if not skipping filesize
        global skip_filesize
        if (
        skip_filesize or
        str(os.path.getsize(therefile)) in size_info.values()
        ):
            # hash therefile if size if found
            therehash = hash_file(therefile)
            # try to find hash. this time use .items() because we want the key
            # in addition to the values
            for herefile, herehash in hash_info.items():
                if therehash == herehash:
                    # found, so make herefile an absolute path
                    herefile = here+"/"+herefile
                    # if it already exists or is a valid symlic, don't replace
                    if os.path.isfile(herefile):
                        continue
                    # check if !isfile() but islink(), meaning it is a broken
                    # symlic and should be replaced
                    elif os.path.islink(herefile):
                        os.remove(herefile)
                    # make directory for the symlic to go in if needed
                    if not os.path.isdir(os.path.dirname(herefile)):
                        os.mkdir(os.path.dirname(herefile))
                    # finally! make the link
                    os.symlink(therefile, herefile)
                    break

# here          absolute path to a --here
# dirname       absolute path to a --there or a sub of --there
# size_info     dictionary (key: filename, val: size) of files in --here
# hash_info     dictionary (key: filename, val: hash) of files in --here
def postwork_do_directory(here, dirname, size_info, hash_info):
    contained_files = []
    contained_directories = []
    # get contained directories and files in dirname
    for item in os.listdir(dirname):
        # item is given as a relative path to dirname, so make absolute again
        item = dirname + "/" + item
        if os.path.isfile(item):
            contained_files.append(item)
        elif os.path.isdir(item):
            contained_directories.append(item)
    # process any contained files
    postwork_do_files(contained_files, here, size_info, hash_info)
    # then recursively process and contained dirs
    for dir in contained_directories:
        postwork_do_directory(here, dir, size_info, hash_info)

# here      absolute path to a single --here
# theres    list of untouched --theres
# size_info     dictionary (key: filename, val: size) of files in --here
# hash_info     dictionary (key: filename, val: hash) of files in --here
def postwork(here, theres, size_info, hash_info):
    for there in theres:
        # make sure there is a directory
        if (not os.path.isdir(there)):
            print(there+" is not a directory")
            continue
        # change there into absolute path, as no relativity needed here
        #we are evil and siths deal in absolutes
        there = os.path.realpath(there)
        # start the recursion!
        postwork_do_directory(here, there, size_info, hash_info)

# heres     list of --heres
# theres    list of --theres
def dispatch_postwork(heres, theres):
    for here in heres:
        # immediately convert here to absolute path as relativness is unneeded
        here = os.path.realpath(here)
        # makes dicts for size and hash info.
        # TODO: consider storing in list of tuples or similar as keys are never
        # used as a key
        size_info = dict() # key: filename, val: size
        hash_info = dict() # key: filename, val: hash
        # make sure size file and hash file are where they are expected
        size_filename = here+"/sizes.mns"
        hash_filename = here+"/hashes.mns"
        if (
        not os.path.isfile(size_filename) or
        not os.path.isfile(hash_filename)
        ):
            print("Could not find sizes.mns or hashes.mns in " + here)
            continue
        # read in all that glorious size and hash info
        with open(size_filename, "r") as size_file:
            for line in size_file:
                # size and filename are seperated by a tab
                # partition all but the last char on a line (a \n) on the first
                # occurence of a tab
                size, _, filename = line[:-1].partition('\t')
                size_info[filename] = size
        with open(hash_filename, "r") as hash_file:
            for line in hash_file:
                # hash and filename are seperated by a tab
                # partition all but the last char on a line (a \n) on the first
                # occurence of a tab
                hash, _, filename = line[:-1].partition('\t')
                hash_info[filename] = hash
        # send off all this jazz to postwork
        postwork(here, theres, size_info, hash_info)

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
    parser.add_argument(
        '-s', '--stage',
        choices=['prework','postwork'],
        required=True
    )
    parser.add_argument('-H', '--here', metavar='dir', nargs='+')
    parser.add_argument('-T', '--there', metavar='dir', nargs='+')
    parser.add_argument('-t', '--torrent', metavar='torrentfile')
    parser.add_argument('--skip-filesize', action='store_const', const=1)
    args = parser.parse_args()

    global skip_filesize
    skip_filesize = (True if args.skip_filesize else False)

    if (args.stage == 'prework'):
        if (not args.here and not args.torrent):
            print("Need --here or --torrent")
            print("Aborting")
        elif (args.there):
            print("--there doesn't make sense with prework")
            print("Aborting")
        else:
            dispatch_prework(args.here, args.torrent)
    else:
        if (not args.here or not args.there):
            print("Need --here and --there")
            print("Aborting")
        elif (args.torrent):
            print("--torrent doesn't make sense with postwork")
            print("Aborting")
        else:
            dispatch_postwork(
                args.here,
                args.there
            )
