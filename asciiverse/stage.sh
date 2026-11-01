#!/bin/sh
# Lays out the av archive in stage/: the start script at the top, and the
# game in lib/ with its data files and our sysconf. The start script makes
# the player's own playground and links these files into it.
set -eu
i=build/install
rm -rf stage && mkdir -p stage/lib
cp asciiverse/evilhack stage/evilhack
cp "$i/evilhack" "$i/recover" "$i/nhdat" "$i/license" "$i/symbols" \
   "$i/serverseed" stage/lib/
cp asciiverse/sysconf stage/lib/sysconf
cp doc/Guidebook.txt stage/
cp LICENSE README.md PATCHES.md doc/evilhack-changelog.md stage/
