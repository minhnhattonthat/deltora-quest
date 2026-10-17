-- Log every call of the string renderer (arm9 0x0204DACC, r0 = window): frame, caller (lr), string pointer and length.
L.on_exec(0x0204DACC, function()
  local w = memory.getregister("arm9.r0")
  L.log(string.format("f%d draw lr=%08X win=%08X str=%08X len=%d pitch=%d", L.frame, memory.getregister("arm9.r14"), w,
    memory.readdword(w + 0x20), memory.readdword(w + 0x24), memory.readdword(w + 0x40)))
end)
