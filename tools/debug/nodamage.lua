-- No damage: every frame, set the player's HP to its max. HP is 20.12 fixed point at player object + 0xBC, max at
-- + 0xC0 (getters 0x0208B79C / 0x0208B7A4; hearts = (HP >> 12) / 10, drawn by 0x02095D24).
-- shortcut: the player object sat at 0x0221EC14 in the ch1 boss fight (boss_ch1); other stages may place it
-- elsewhere: pass HP_ADDR (object + 0xBC) after checking a RAM dump.
local hp = HP_ADDR or 0x0221ECD0
L.on_frame(function()
  memory.writedword(hp, memory.readdword(hp + 4))
end)
