#!/bin/sh
# Builds EvilHack and installs it into build/install (the game, nhdat,
# license, symbols, serverseed, recover). Linux: run inside alpine:3.22 for
# a fully static binary (ncursesw linked in); macOS: run on the runner with
# CC_ARCH set to x86_64 or arm64, linking the system's ncurses. Other Linux
# (local testing) links ncursesw shared.
#   docker run --rm -v "$PWD":/src -w /src alpine:3.22 sh asciiverse/build.sh
# Uses upstream's sys/unix/setup.sh with our own hints (asciiverse/hints).
# Needs bison and flex: the parser sources in sys/share are older than
# the grammars.
set -eu

if [ -f /etc/alpine-release ]; then
  apk add --no-cache build-base linux-headers bison flex ncurses-dev ncurses-static >/dev/null
  curses="-lncursesw"
  lflags="-static"
elif [ "$(uname)" = Darwin ]; then
  curses="-lncurses"
  lflags="${CC_ARCH:+-arch $CC_ARCH}"
else
  curses="$(pkg-config --libs ncursesw)"
  lflags=""
fi
cc="cc${CC_ARCH:+ -arch $CC_ARCH}"

# setup.sh writes the Makefiles from the hints; hints paths are relative
# to the top of the tree.
(cd sys/unix && sh setup.sh ../../asciiverse/hints)

inst="$PWD/build/install"
rm -rf "$inst" && mkdir -p "$inst"
make clean >/dev/null 2>&1 || true
make CC="$cc" AV_CURSESLIB="$curses" AV_LFLAGS="$lflags" all
make CC="$cc" AV_CURSESLIB="$curses" AV_LFLAGS="$lflags" \
  INSTDIR="$inst" VARDIR="$inst" SHELLDIR= install
strip "$inst/evilhack" "$inst/recover"
