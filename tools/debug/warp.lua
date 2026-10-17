-- Warp at New Game: the title script calls StageSet2(0, 3) and LoadExecEvent(2608, 99), which then loads the
-- opening (1811). This swaps the stage for (CH, AREA) and the opening for event script EV at entry EVE.
-- Use from a new-game route (tools/routes/new_game.txt); needs --debugger. Background: docs/re/events.md.
local CH, AREA, EV, EVE, EVN = CH or 1, AREA or 1, EV, EVE or 0, EVN or 2  -- EVN: which LoadExecEvent to swap
local loads = 0
L.on_exec(0x0203AF14, function()  -- stage_set(game, chapter, area)
  if memory.getregister("arm9.r1") == 0 and memory.getregister("arm9.r2") == 3 and loads <= 1 then
    memory.setregister("arm9.r1", CH)
    memory.setregister("arm9.r2", AREA)
    L.log(string.format("f%d stage -> %d,%d", L.frame, CH, AREA))
  end
end)
L.on_exec(0x02039C1C, function()  -- LoadExecEvent: r0 = script file just read
  loads = loads + 1
  if loads == EVN and EV then
    L.log(string.format("f%d event %d -> %d", L.frame, memory.getregister("arm9.r0"), EV))
    memory.setregister("arm9.r0", EV)
  end
end)
L.on_exec(0x02039C2C, function()  -- second int: entry
  if loads == EVN and EV then memory.setregister("arm9.r0", EVE) end
end)
