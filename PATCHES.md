# Asciiverse patches

EvilHack by k21971, from [k21971/EvilHack](https://github.com/k21971/EvilHack)
at release `v0.9.3`, packaged for the Asciiverse.

**The game's source is unchanged.** Everything below is build
configuration, in files of our own under `asciiverse/`.

## Build

- `asciiverse/hints` replaces `sys/unix/hints/linux` for upstream's own
  `sys/unix/setup.sh`. It keeps upstream's options, including the curses
  interface, dumplogs and score and real time on the status line, and
  leaves out what is only for a public server: `DGAMELAUNCH`,
  `LIVELOG_ENABLE`, `DUMPHTML` and `TTY_TILES_ESCCODES`. Optimised
  (`-O2`) rather than a debug build.
- Saves are not compressed: upstream's build calls `/bin/gzip`, which
  isn't at that path on every system (macOS).
- Linux builds are static (Alpine); macOS uses the system's ncurses.

## A playground for each player

NetHack-style games keep saves, bones, the score list and lock files in
one "playground" folder, normally shared by everyone on the machine and
written through a setgid binary. Here every player has their own, in
`${XDG_DATA_HOME:-~/.local/share}/evilhack`:

- The game is built without a fixed `VAR_PLAYGROUND`, and reads
  `sysconf` from the playground. The start script (`asciiverse/evilhack`)
  creates the playground, links the game data (`nhdat`, `symbols`,
  `license`, `sysconf`, `serverseed`) into it from the install, creates
  the score files and starts the game with `NETHACKDIR` pointing there.
- The system packages use the same start script as `/usr/bin/evilhack`,
  with the game in `/usr/lib/evilhack`. Nothing is setgid and there is no
  shared `/var/games` folder; scores are per player.

## sysconf

`asciiverse/sysconf` is upstream's `sys/unix/sysconf` for one local
player. The game settings and default options are upstream's. Changed:
nobody may use debug (wizard) mode, anyone may use explore mode;
dumplogs go to the playground's `dumplog/` folder; the server-only lines
(live log, HTML dumps, gdb paths) and the hardfought support line are
left out. Your own options go in `~/.evilhackrc`.
