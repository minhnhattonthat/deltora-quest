-- Is the ITCM tail (0x01FFFB00-0x01FFFFFF, past the game's 0x7B00-byte ITCM block) ever non-zero? Logs at FROM.. every 300 frames.
local lo, hi = 0x01FFFB00, 0x01FFFFFF
L.on_frame(function(n)
  if n % 300 ~= 0 then return end
  local nz, first = 0, nil
  for a = lo, hi do
    if memory.readbyte(a) ~= 0 then nz = nz + 1; first = first or a end
  end
  L.log(string.format("f%d itcm tail nonzero=%d first=%s", n, nz, first and string.format("%08X", first) or "-"))
end)
