-- Dump main RAM and video state at frame DUMP_AT (default 1700): <out>/ram_<frame>.bin, dump_<frame>.*.bin
local at = DUMP_AT or 1700
L.on_frame(function(n)
  if n == at then
    L.dump_ram(string.format("ram_%06d.bin", n))
    L.dump_ppu(string.format("dump_%06d", n))
    L.log("dumped at " .. n)
  end
end)
