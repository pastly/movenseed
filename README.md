# movenseed
Recursive file linker handy for continued seeding of moved, renamed, and reorganized files

Requires python 3.  
Tested using python 3.4.2 on Ubuntu 14.10 x64

## Usage

    movenseed.py [-h] -s {prework,postwork} [-H dir [dir ...]] [-T dir [dir ...]] [-t torrentfile] [--skip-filesize] [--skip-filehash] [--no-make-subdirectory] [--hard] [-v]

* `-h/--help` anywhere to print help and quit
* `-s/--stage` to tell movenseed what stage you would like to execute
* `-H/--here` to provide a list of HERE directories
* `-T/--there` to provide a list of THERE directories
* `-t/--torrent` to provide a torrent file for generating size information in a single HERE directory
* `--skip-filesize` to only generate hash info or to only check file hashes
* `--skip-filehash` to only generate size info or to only check file sizes. For best results, this should only be used when prework had to be run with a torrentfile only.
* `--no-make-subdirectory` during prework with a torrentfile and a HERE to skip making a directory for a torrentfile containing more than one file reference.
* `--hard` to make hard links instead of symbolic links
* `-v/--verbose` to print out lots of fun information

## Details and Examples

### Prework

This stage will recursively read all files inside a given HERE folder and its subfolders and store information on them. This information can be used in the Postwork stage to reconstruct the folder. Prework expects only HERE directories.

* `./movenseed.py -s prework -H /music/BandName/Album`
  * This will prepare the given directory for changes. Stores file size and hash information in sizes.mns and hashes.mns respectively.
* `./movenseed.py -s prework -H /music/BandName/Album /music/BandName/Album2`
  * Similar to above, but this time will do the prework stage on two directories. Each has its own sizes.mns and hashes.mns
* `./movenseed.py -s prework -H /music/BandName/*`
* `./movenseed.py -s prework -H Documents/Work\ Files/`
* `./movenseed.py -s prework -H ../projects`

If given a torrentfile and a single HERE directory, Prework will generate size information for a HERE directory that is missing its files. Without the --no-make-subdirectory option, prework will create a subdirectory in HERE using the name contained in the torrentfile and place sizes.mns in that. If the torrentfile is only for a single file, the flag is ignored and no subdirectory is made

* `./movenseed.py -s prework -t torrents/family-pics-1.torrent -H /media/pics/family`
    * Generates size information based on information from the given torrent and puts it a subdirectory of HERE. For example: "HERE/family pics 1"
 * `./movenseed.py -s prework -t torrents/xtreme-linux.iso.torrent -H /media/linuxes`
    * Similar to the above, but does not make a subdirectory in HERE since the torrentfile would only download a single file. 

### Postwork

This stage expects at least one HERE directory and at least one THERE directory. Postwork will scan each file in a THERE directory to see if it has the same file size an hash as a file that used to be in a HERE directory. If so, movenseed will symbolically link to them inside their old HERE directory. This obviously works even with renamed and reorganized files.

* `./movenseed.py -s postwork -H /music/BandName/Album -T /public/allmusic/Album`
  * Scans every file in the THERE directory (and any subdirectories). Any files missing from the HERE directory will be linked towards their renamed-selves in THERE if found.
* `./movenseed.py -s postwork -H /music/* -T /public/allmusic`
* `./movenseed.py -s postwork -H Documents/Work\ Files -T /public/meeting-notes /backup/work`

## Notes

* You may start to see poor performance when specifying many HEREs and THEREs. Try to be as specific as you can with THERE folders. It may also be good to know that a THERE is rescanned for each HERE. Future implementations may change this behavior.
* This script works best when it was run before files were moved and renamed. In its current implementation, it will refuse to run if --skip-filehash is provided and sizes.mns contains non-unique sizes. Future implementations may have an interactive mode to let the user make decisions for same-sized files.
