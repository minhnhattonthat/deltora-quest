-- Log script-command handler calls (event engine, docs/re/events.md). Needs --debugger.
-- Command table (arm9 0x020B9xxx): {name, signature, handler, flags}. Handlers take a call context in r0;
-- 0x02028D34(ctx, i) returns integer argument i. 0x0203AF14(game, stage, sub) is the native stage set.
local CMDS = {
  [0x0203E7A8] = "StageSet2", [0x0203E0E4] = "LoadExecEvent", [0x0203E72C] = "StageSet",
  [0x02042DC0] = "ChangeStage", [0x02047878] = "CallStaffRoll",
}
for addr, name in pairs(CMDS) do
  L.on_exec(addr, function() L.log(string.format("f%d %s", L.frame, name)) end)
end
L.on_exec(0x0203AF14, function()
  L.log(string.format("f%d   stage_set(%d, %d)", L.frame, memory.getregister("arm9.r1"), memory.getregister("arm9.r2")))
end)
