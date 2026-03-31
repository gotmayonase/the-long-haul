-- The Long Haul - Client Lua
-- Runs on: each game client (including the host in a listen server)
--
-- Responsibilities:
--   - Detect when the local player aims while holding a haul item
--   - Send a server command to REQUEST unequip (server performs the state change)
--
-- What this file does NOT do:
--   - Directly modify any game state (no setPrimaryHandItem, no inventory changes)
--   - Run logic for remote players — OnPlayerUpdate on the client only fires
--     for the LOCAL player, so remote players are handled server-side
--
-- MP architecture: client detects → sends command → server acts → engine syncs to all clients

-- Module name used in sendClientCommand / OnClientCommand matching.
-- Must match exactly what LongHaul_Server.lua listens for.
local MODULE = "TheLongHaul"

-- All haul item full type IDs.
-- Update this table if items are added or renamed.
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

-- Returns the equipped haul item for a player, or nil.
local function getEquippedHaulItem(player)
    local primary = player:getPrimaryHandItem()
    if primary and HAUL_ITEMS[primary:getFullType()] then
        return primary
    end
    -- TwoHandWeapon items occupy both slots, but check secondary as fallback.
    local secondary = player:getSecondaryHandItem()
    if secondary and HAUL_ITEMS[secondary:getFullType()] then
        return secondary
    end
    return nil
end

-- Throttle: only send the unequip command once per aim event, not every tick.
-- Reset when the player stops aiming.
local aimUnequipSent = false

-- OnPlayerUpdate fires every tick for the LOCAL player on the client.
-- Keep this handler cheap — early exits on the common path.
local function onPlayerUpdate(player)
    if not player then return end

    local haulItem = getEquippedHaulItem(player)

    if not haulItem then
        aimUnequipSent = false  -- reset throttle when no haul item held
        return
    end

    -- Drop-on-aim: request the server to unequip when the player raises a weapon.
    -- TODO:VERIFY player:isAiming() is the correct B42 method name.
    -- If TwoHandWeapon = TRUE already prevents aiming natively in B42, this whole
    -- block may be redundant — test in-game and remove if so.
    if player:isAiming() and not aimUnequipSent then
        aimUnequipSent = true
        -- Do NOT call player:setPrimaryHandItem(nil) here — that's a state change.
        -- Request the server to do it instead.
        sendClientCommand(player, MODULE, "dropHaulItem", {})
    elseif not player:isAiming() then
        aimUnequipSent = false  -- reset so next aim event triggers again
    end
end

Events.OnPlayerUpdate.Add(onPlayerUpdate)

-- Weight-based speed scaling (foundation — currently unused).
-- The static RunSpeedModifier handles base penalty automatically.
-- Uncomment and extend to add extra slowdown based on load weight.
--
-- local function getLoadPenalty(haulItem)
--     local container = haulItem:getContainer()
--     if not container then return 0 end
--     local fillRatio = container:getWeight() / container:getCapacity()
--     -- At 100% full, applies a further 0.15 penalty on top of the base modifier.
--     return fillRatio * 0.15
-- end
