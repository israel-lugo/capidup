# Capidup

[![license](https://img.shields.io/badge/license-GPLv3+-blue.svg)](LICENSE)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/15155f1c5c454678923f5fb79401d151)](https://www.codacy.com/app/israel-lugo/capidup)

Quickly find duplicate files in directories

Capidup recursively crawls through all the files in a list of directories and
identifies duplicate files. Duplicate files are files with the exact same
content, regardless of their name, location or timestamp.

This program is designed to be quite fast. It uses a smart algorithm to detect
and group duplicate files using a single pass on each file (that is, Capidup
doesn't need to compare each file to every other).

## Usage

Using Capidup is quite simple:

```bash
$ capidup /media/sdcard/DCIM ~/photos
/media/sdcard/DCIM/DSC_1137.JPG
/home/user/photos/Lake001.jpg
------------------------------
/media/sdcard/DCIM/DSC_1138.JPG
/home/user/photos/Lake002.jpg
------------------------------
/home/user/photos/Woman.jpg
/home/user/photos/portraits/Janet.jpg
------------------------------
```

Here we find out that /media/sdcard/DCIM/DSC_1137.JPG is a duplicate of
~/photos/Lake001.jpg, DSC_1138.JPG is a duplicate of Lake002.jpg, and
~/photos/Woman.jpg is a duplicate of photos/portraits/Janet.jpg.

## Algorithm

Capidup crawls the directories and gathers the list of files. Then, it takes a
3-step approach:

 1. Files are grouped by size (files of different size must obviously be
    different).
 
 1. Within files of the same size, they are further grouped by the MD5 of the
    first few KBytes. Naturally, if the first few KB are different, the files
    are different.
 
 1. Within files with the same initial MD5, they are finally grouped by the MD5
    of the entire file. Files with the same MD5 are considered duplicates.

## Considerations

There is a *very small* possibility of false positives. For any given file,
there is a 1 in 2<sup>64</sup> (1:18,446,744,073,709,551,616) chance of some
other random file being detected as its duplicate by mistake.

The reason for this is that two different files may have the same hash: this is
called a collision. Capidup uses MD5 (which generates 128 bit hashes) for
detecting whether the files are equal. It cannot distinguish between a case
where both files are equal and a case where they just happen to generate the
same MD5 hash.

The odds of this happening by accident, though, for two files of the same size,
are really very low. For normal home use, dealing with movies, music, source
code or other documents, this problem can be disregarded.

## Security

There is one case when care should be taken: when comparing files which might
have been intentionally manipulated by a malicious attacker.

While the chance of two random files having the same MD5 hash are really very
low (as stated above), it *is* possible for a malicious attacker to purposely
manipulate a file to have the same MD5 as another. The MD5 algorithm is not
secure against intentional disception.

This may be of concern for example when comparing things such as program
installers. A malicious attacker could infect an installer with malware, and
manipulate the rest of the file in such a way that it still has the same MD5 as
the original. Comparing the two files, Capidup would show them as duplicates
when they are not.

## Future plans

Future plans for Capidup include having a configurable option to use a
different hashing algorithm, such as SHA1 which has a larger hash size of 160
bits, or SHA2 which allows hashes up to 512 bits and has no publicly known
collision attacks. SHA2 is currently used for most cryptographic purposes,
where security is essential. False positives, random or maliciously provoked,
would be practically impossible. Duplicate detection will of course be slower,
depending on the chosen algorithm.

For the extremely paranoid case, there could be an additional setting which
would check files with two different hashing algorithms. The tradeoff in speed
would not be worthwhile for any normal use case, but the possibility could be
there.

