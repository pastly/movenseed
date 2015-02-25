# movenseed
Recursive file linker handy for continued seeding of moved, renamed, and reorganized files

Requires python 3.  
Tested using python 3.4.2 on ubuntu 14.10 x64

## Usage

    movenseed.py [-h] -s {prework,postwork} [-H dir [dir ...]] [-T dir [dir ...]] [-t torrentfile] [--skip-filesize] [--hard] [-v]

* Use -h/--help anywhere to print help and quit
* Use -s/--stage to tell movenseed what stage you would like to execute
* Use -H/--here to provide a list of HERE directories
* Use -T/--there to provide a list of THERE directories
* __(NOT implemented yet)__ Use -t/--torrent to provide a torrent file instead of a HERE directory during prework
* Use --skip-filesize to only check file hashes during postwork
* Use --hard to make hard links instead of symbolic links
* Use -v/--verbose to print out lots of fun information

## Details and Examples

### Prework

This stage will recursively read all files inside a given folder and its subfolders and store information on them. This information can be used in the Postwork stage to reconstruct the folder. Prework expects only HERE directories.

* `./movenseed.py -s prework -H /music/BandName/Album`
  * This will prepare the given directory for changes. Stores file size and hash information in sizes.mns and hashes.mns respectively.
* `./movenseed.py -s prework -H /music/BandName/Album /music/BandName/Album2`
  * Similar to above, but this time will do the prework stage on two directories. Each has its own sizes.mns and hashes.mns
* `./movenseed.py -s prework -H /music/BandName/*`
* `./movenseed.py -s prework -H Documents/Work\ Files/`
* `./movenseed.py -s prework -H ../projects`

### Postwork

This stage expects at least one HERE directory and at least one THERE directory. Postwork will scan each file in a THERE directory to see if it has the same file size an hash as a file that used to be in a HERE directory. If so, movenseed will symbolically link to them inside their old HERE directory. This obviously works even with renamed and reorganized files.

* `./movenseed.py -s postwork -H /music/BandName/Album -T /public/allmusic/Album`
  * Scans every file in the THERE directory (and any subdirectories). Any files missing from the HERE directory will be linked towards their renamed-selves in THERE if found.
* `./movenseed.py -s postwork -H /music/* -T /public/allmusic`
* `./movenseed.py -s postwork -H Documents/Work\ Files -T /public/meeting-notes /backup/work`

## Notes

* You may start to see poor performance when specifying many HEREs and THEREs. Try to be as specific as you can with THERE folders. It may also be good to know that a THERE is rescanned for each HERE. Future implementations may change this behavior.
* This script works best when it was run before files were moved and renamed. Duh, because doing prework with a .torrent isn't implemented yet. Even when it is, if the scan of the .torrent file returns two or more files of the same size, I will either have the script refuse to run or require manual interaction.
