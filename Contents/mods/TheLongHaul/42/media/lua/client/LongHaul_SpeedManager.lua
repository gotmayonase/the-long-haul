-- The Long Haul - Speed Manager
-- Handles dynamic behavior for haul items:
--   1. Drop-on-aim: automatically unequips haul items when the player aims
--   2. Foundation for future weight-based speed scaling
--
-- The static RunSpeedModifier defined on each item handles the base speed
-- penalty automatically. This file extends that with dynamic behavior.

local LongHaul = {}

-- All haul item full type IDs. Update this table if items are added/renamed.
LongHaul.HAUL_ITEMS = {
    ["LongHaul.StickTravois"]         = true,
    ["LongHaul.LashedTravois"]        = true,
    ["LongHaul.DragSledge"]           = true,
    ["LongHaul.ShoulderYoke"]         = true,
    ["LongHaul.PaddedYoke"]           = true,
    ["LongHaul.StoneWheelbarrow"]     = true,
    ["LongHaul.WoodenWheelbarrow"]    = true,
    ["LongHaul.ReinforcedWheelbarrow"] = true,
}

-- Returns the equipped haul item, or nil if the player isn't holding one.
local function getEquippedHaulItem(player)
    local primary = player:getPrimaryHandItem()
    if primary and LongHaul.HAUL_ITEMS[primary:getFullType()] then
        return primary
    end
    -- TwoHandWeapon items occupy both slots, but check secondary as a fallback.
    local secondary = player:getSecondaryHandItem()
    if secondary and LongHaul.HAUL_ITEMS[secondary:getFullType()] then
        return secondary
    end
    return nil
end

-- Drop-on-aim: unequip the haul item when the player raises a weapon.
-- This prevents the awkward situation of trying to aim while dragging a sledge.
-- TwoHandWeapon already blocks most actions, but aiming can still be triggered.
--
-- NOTE: Test whether TwoHandWeapon = TRUE already prevents aiming in B42.
-- If it does, this handler is redundant but harmless. If not, this ensures
-- the item is dropped cleanly rather than causing animation conflicts.
local function onPlayerUpdate(player)
    if not player then return end

    local haulItem = getEquippedHaulItem(player)
    if not haulItem then return end

    -- Drop on aim
    if player:isAiming() then
        -- Transfer item back to main inventory from hands
        -- TODO:VERIFY this is the correct unequip method in B42.
        -- Alternative: player:getInventory():DropItem(haulItem)
        player:setPrimaryHandItem(nil)
        player:setSecondaryHandItem(nil)
    end
end

-- Weight-based speed scaling (foundation — currently unused).
-- The static RunSpeedModifier handles base penalty. Uncomment and extend
-- this to add extra slowdown when the container is heavily loaded.
--
-- local function getLoadPenalty(haulItem)
--     local container = haulItem:getContainer()
--     if not container then return 0 end
--     local fillRatio = container:getWeight() / container:getCapacity()
--     -- Returns an additional speed penalty (0.0 to 0.15) based on load.
--     -- At 100% full, adds a further 0.15 slowdown on top of the base modifier.
--     return fillRatio * 0.15
-- end

Events.OnPlayerUpdate.Add(onPlayerUpdate)
