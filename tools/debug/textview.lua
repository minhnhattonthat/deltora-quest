-- Text viewer: the next text windows the game opens show STRS[1], STRS[2], ... instead of their own line.
-- Driven by tools/debug/show.py, which writes STRS and passes it with --script before this file.
-- An entry is {file=2179, index=5} (the game loads that line itself: real header, name tag, portrait) or a list of
-- encoded bytes (raw text, FFFD included; keeps the original line's header). Needs --debugger: JIT misses exec hooks.
-- Hooks (docs/re/debug.md): 0x0204D234(r0 window, r1 file, r2 index) loads a message; it returns to 0x0204C290 or
-- 0x0204C410, where [w+0x20] string ptr and [w+0x24] length (units incl. FFFD) are set and nothing has used them yet.
local BUF = BUF or 0x023C0000  -- unused at every dump checked so far (docs/re/debug.md)
local k, raw = 0, nil
L.on_exec(0x0204D234, function()
  local f, i = memory.getregister("arm9.r1"), memory.getregister("arm9.r2")
  if not STRS or k >= #STRS then L.log(string.format("f%d load %d_%03d", L.frame, f, i)); return end
  k = k + 1
  local s = STRS[k]
  if s.file then
    memory.setregister("arm9.r1", s.file)
    memory.setregister("arm9.r2", s.index)
    raw = nil
  else
    raw = s
  end
  L.log(string.format("f%d load %d_%03d -> %s", L.frame, f, i, STR_IDS and STR_IDS[k] or "?"))
end)
local function swap()
  if not raw then return end
  local w, a = memory.getregister("arm9.r4"), BUF + (k - 1) * 0x800
  for i = 1, #raw do memory.writebyte(a + i - 1, raw[i]) end
  memory.writedword(w + 0x20, a)
  memory.writedword(w + 0x24, #raw / 2)  -- Lua 5.1: no // operator; #raw is even
  -- [w+0x54] = most lines on any page (the loader set it from the original line; it sizes the window bitmap)
  local lines, most = 1, 1
  for i = 1, #raw - 1, 2 do
    local c = raw[i] + raw[i + 1] * 256
    if c == 0xFFFF then lines = lines + 1 elseif c == 0xFFFE then lines = 1 end
    if lines > most then most = lines end
  end
  memory.writedword(w + 0x54, most)
  raw = nil
end
L.on_exec(0x0204C290, swap)
L.on_exec(0x0204C410, swap)
-- shoot each injected window SHOT_AFTER frames after it loads: text_<k>_<delay>.png
local loaded = {}
local SHOT_AFTER = SHOT_AFTER or {60, 120}
L.on_frame(function(n)
  if k > 0 and not loaded[k] then loaded[k] = n end
  for j, f in pairs(loaded) do
    for _, d in ipairs(SHOT_AFTER) do
      if n == f + d then L.shot(string.format("text_%02d_%03d.png", j, d)) end
    end
  end
end)
