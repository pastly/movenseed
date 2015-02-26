# movenseed
Recursive file linker handy for continued seeding of moved, renamed, and reorganized files

Requires python 3.  
Tested using python 3.4.2 on Ubuntu 14.10 x64

## Usage

    movenseed.py [-h] -s {prework,postwork} [-H dir [dir ...]] [-T dir [dir ...]] [-t torrentfile] [--skip-filesize] [--skip-filehash] [--no-make-subdirectory] [--hard] [-v]

* `-h/--help` Print help and quit.
* `-s/--stage` Tell movenseed what stage you would like to execute.
* `-H/--here` Provide a list of HERE directories.
* `-T/--there` Provide a list of THERE directories.
* `-t/--torrent` Provide torrent files for generating size information in a single HERE directory.
* `--skip-filesize` Only generate hash info or to only check file hashes.
* `--skip-filehash` Only generate size info or to only check file sizes. For best results, this should only be used when prework had to be run with a torrentfile only.
* `--no-make-subdirectory` **Not recommended.** During prework with a torrentfile and a HERE, skip making a directory for a torrentfile containing more than one file reference.
* `--hard` Make hard links instead of symbolic links. Probably only works on Linux and definitely doesn't work across filesystems.
* `-v/--verbose` Print out lots of fun information. Default is to run pretty darn quiet.

## Details and Examples

### Prework

This stage will recursively read all files inside a given HERE folder and its subfolders and store information on them. This information can be used in the postwork stage to reconstruct the folder. Prework does not expect and will not take THERE directories.

* `./movenseed.py -s prework -H /music/BandName/Album`
  * This will prepare the given directory for changes. Stores file size and hash information in sizes.mns and hashes.mns respectively.
* `./movenseed.py -s prework -H /music/BandName/Album /music/BandName/Album2`
  * Similar to above, but this time will do the prework stage on two directories. Each has its own sizes.mns and hashes.mns
* `./movenseed.py -s prework -H /music/BandName/*`
* `./movenseed.py -s prework -H Documents/Work\ Files/`
* `./movenseed.py -s prework -H ../projects`

If given torrentfiles and a single HERE directory, prework will generate size (not hash) information for a HERE directory that is missing its files. For torrents that would download multiple files, a subdirectory under HERE will be made for it (unless `--no-make-subdirectory` is specified). Multiple torrentfiles can be given. This isn't recommended with a mix of torrents for a single file and torrents for multiple files because the placement and contents of the sizes.mns may be unexpected, especially if you are crazy enough to give `--no-make-subdirectory`.

* `./movenseed.py -s prework -t torrents/family-pics-1.torrent -H /media/pics/family`
    * Generates size information based on information from the given torrent and puts it a subdirectory of HERE. For example: "/media/pics/family/family pics 1/sizes.mns"
* `./movenseed.py -s prework -t torrents/family-pics-*.torrent -H /media/pics/family`
    * If multiple torrentfiles are given (and each is for multiple files) this will make a subdirectory for each inside of HERE.
* `./movenseed.py -s prework -t torrents/xtreme-linux.iso.torrent -H /media/linuxes`
    * Since the torrentfile would only download a single file, size information is placed in /media/linuxes/sizes.mns"

### Postwork

This stage expects at least one HERE directory and at least one THERE directory. Postwork will scan each file in a THERE directory to see if it has the same file size an hash as a file that used to be in a HERE directory. If so, movenseed will symbolically link to them inside their old HERE directory. This obviously works even with renamed and reorganized files.

* `./movenseed.py -s postwork -H /music/BandName/Album -T /public/allmusic/Album`
  * Scans every file in the THERE directory (and any subdirectories). Any files missing from the HERE directory will be linked towards their renamed-selves in THERE if found.
* `./movenseed.py -s postwork -H /music/* -T /public/allmusic`
* `./movenseed.py -s postwork -H Documents/Work\ Files -T /public/meeting-notes /backup/work`

## Notes

* You may start to see poor performance when specifying many HEREs and THEREs. Try to be as specific as you can with THERE folders. It may also be good to know that a THERE is rescanned for each HERE. Future implementations may change this behavior.
* This script works best when it was run before files were moved and renamed. In its current implementation, it will refuse to run if --skip-filehash is provided and sizes.mns contains non-unique sizes. Future implementations may have an interactive mode to let the user make decisions for same-sized files.
