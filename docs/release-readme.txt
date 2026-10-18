Deltora Quest: 7-tsu no Houseki - English translation patch v{version}
=======================================================================

Unofficial English fan translation of Deltora Quest: 7-tsu no Houseki (Nintendo DS, Bandai Namco Games, 2007).
Names follow Emily Rodda's English Deltora Quest novels.

Source and tools: https://github.com/minhnhattonthat/deltora-quest


What you need
-------------
Your own dump of the Japanese game. This patch holds no game data; do not ask for ROMs.

  File:   {rom}
  Size:   {size} bytes
  CRC32:  {crc32}
  MD5:    {md5}
  SHA-1:  {sha1}

Any other dump (another revision, a trimmed ROM, an already patched copy) will not work. Untrimmed only.


How to patch
------------
{patch} is an xdelta3 patch. Apply it to the Japanese ROM with one of:
  - Delta Patcher (Windows/macOS/Linux): choose the ROM as "Original file", the .xdelta as "XDelta patch", Apply.
  - Rom Patcher JS (in a browser): https://www.marcrobledo.com/RomPatcher.js/
  - command line: xdelta3 -d -s "original.nds" "{patch}" "Deltora Quest (EN).nds"

Patched ROM:
  CRC32:  {pcrc32}
  SHA-1:  {psha1}


Playing
-------
Tested in DeSmuME. Start from a fresh save (New Game); savestates made with another build of the game will not
load correctly. The intro movie is skipped by touching the screen; dialogue advances on touch.


Known issues
------------
  - Some screens drawn as pictures were translated but not yet seen in game: chapter/area title cards, the battle
    "Time Left / Weapon Bonus" panel, Emily Rodda's letter, the card trade screen, store-demo screens.
    Report anything that looks wrong.
  - A few minor wording polish items remain; the whole script is translated and reviewed.


Credits
-------
Translation, tools and hacking: minhnhattonthat.
The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome:
open an issue at the GitHub address above.

Deltora Quest is (c) Emily Rodda. The game is (c) Bandai Namco Games. This project is not affiliated with them.
Unofficial fan work, free of charge. Do not sell or share patched ROMs.

Support: https://ko-fi.com/minhnhattonthat
