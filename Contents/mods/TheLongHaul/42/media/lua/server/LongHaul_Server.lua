-- The Long Haul - Server Lua
-- Runs on: the dedicated server, OR the host in a listen server
--
-- Responsibilities:
--   - Receive client commands and perform authoritative state changes
--   - Any game state modification lives here, not in client Lua
--
-- Why this matters for MP:
--   Changes made server-side are automatically propagated to all connected
--   clients by PZ's engine. Changes made client-side only are visible locally
--   and will desync in multiplayer.

-- Module name — must match the MODULE constant in LongHaul_Client.lua exactly.
local MODULE = "TheLongHaul"

-- All haul item full type IDs (duplicated from client for server-side validation).
-- The server must re-validate that the player is actually holding a haul item
-- before acting — never trust the client's word alone.
local HAUL_ITEMS = {
    ["LongHaul.StickTravois"]               = true,
    ["LongHaul.LashedTravois"]              = true,
    ["LongHaul.DragSledge"]                 = true,
    ["LongHaul.ShoulderYoke"]               = true,
    ["LongHaul.PaddedYoke"]                 = true,
    ["LongHaul.StoneWheelbarrow"]           = true,
    ["LongHaul.MetalAxledStoneWheelbarrow"] = true,
    ["LongHaul.WoodenWheelbarrow"]          = true,
    ["LongHaul.ReinforcedWheelbarrow"]      = true,
}

local function isHaulItem(item)
    return item ~= nil and HAUL_ITEMS[item:getFullType()] ~= nil
end

-- Command handlers — one function per command name.
-- Each receives the player (IsoPlayer) and args table sent by the client.
local commands = {}

-- dropHaulItem: unequip the haul item from the player's hands.
-- Called when the client detects the player is aiming while holding a haul item.
commands.dropHaulItem = function(player, args)
    -- Server-side validation: confirm the player is actually holding a haul item.
    -- This prevents a malicious client from triggering unequip arbitrarily.
    local primary   = player:getPrimaryHandItem()
    local secondary = player:getSecondaryHandItem()

    if isHaulItem(primary) or isHaulItem(secondary) then
        -- TODO:VERIFY player:setPrimaryHandItem(nil) is the correct B42 server-side
        -- unequip method. Alternative if this doesn't work: force-add the item back
        -- to the player's main inventory via player:getInventory():AddItem(item)
        -- after removing from hands.
        player:setPrimaryHandItem(nil)
        player:setSecondaryHandItem(nil)
    end
end

-- Central OnClientCommand dispatcher.
-- All client→server communication for this mod flows through here.
local function onClientCommand(module, command, player, args)
    if module ~= MODULE then return end

    local handler = commands[command]
    if handler then
        handler(player, args)
    else
        print("[TheLongHaul] Unknown client command: " .. tostring(command))
    end
end

Events.OnClientCommand.Add(onClientCommand)
