-- Text viewer: each new string the game draws is replaced by the next one of STRS, so any line can be checked in a
-- real window from one savestate. Driven by tools/debug/show.py, which writes STRS (Lua file of encoded bodies,
-- FFFD included) and passes it with --script before this file. Needs --debugger: JIT misses this exec hook.
-- Hook: arm9 0x0204DACC = string renderer, r0 = window; [w+0x20] string ptr, [w+0x24] length in units incl. FFFD.
local BUF = BUF or 0x023C0000  -- unused at every dump checked so far (docs/re/debug.md)
local k, mine = 0, {}
L.on_exec(0x0204DACC, function()
  local w = memory.getregister("arm9.r0")
  local p = memory.readdword(w + 0x20)
  if mine[p] or not STRS or k >= #STRS then return end
  k = k + 1
  local s, a = STRS[k], BUF + (k - 1) * 0x800
  for i = 1, #s do memory.writebyte(a + i - 1, s[i]) end
  memory.writedword(w + 0x20, a)
  memory.writedword(w + 0x24, #s / 2)  -- Lua 5.1: no // operator; #s is even
  mine[a] = true
  L.log(string.format("f%d window %08X shows %s", L.frame, w, STR_IDS and STR_IDS[k] or "?"))
end)
