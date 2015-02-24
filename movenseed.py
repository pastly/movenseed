#!/usr/bin/env python3
import os
import hashlib

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

def prework_do_files(filelist, size_info, hash_info):
    # filelist should contain absolute paths for best results
    for file in filelist:
        # may be unecessary check in most use cases, but this fixed python
        # trying to read a symbolic link to nowhere
        if os.path.isfile(file):
            file_size = os.path.getsize(file)
            file_hash = hash_file(file)
            size_info.append(str(file_size) + "\t" + file + "\n")
            hash_info.append(file_hash + "\t" + file + "\n")

def prework_do_directory(dirname, size_info, hash_info):
    contained_files = []
    contained_directories = []
    for (path, dirs, files) in os.walk(dirname):
        contained_files.extend(files)
        contained_directories.extend(dirs)
        break
    contained_files = [dirname+"/"+f for f in contained_files]
    contained_directories = [dirname+"/"+d for d in contained_directories]
    prework_do_files(contained_files, size_info, hash_info)
    for dir in contained_directories:
        #if os.path.isdir(dir):
        prework_do_directory(dir, size_info, hash_info)

def prework(source_dirname):
    size_info = []
    hash_info = []
    prework_do_directory(source_dirname, size_info, hash_info)
    with open(source_dirname+"/sizes.mns", "w") as size_outfile:
        for item in size_info:
            size_outfile.write(item)
    with open(source_dirname+"/hashes.mns", "w") as hash_outfile:
        for item in hash_info:
            hash_outfile.write(item)



if __name__ == "__main__":
    prework("/tmp")
