# Project Zomboid Modding Guide (Build 42)

A practical, ground-up guide to modding Project Zomboid targeting **Build 42.15+** (unstable branch). Written as actual mod development happened — expect real examples, verified techniques, and honest notes about what still needs confirming in-game.

> **Why this guide exists:** Official documentation for B42 is sparse. The PZwiki lags behind. B42 made sweeping changes to the modding API that broke most B41 tutorials. This guide is an attempt to document the current reality.

---

## Table of Contents

1. [Build 42 vs Build 41 — What Changed](#build-42-vs-build-41--what-changed)
2. [Mod Folder Structure](#mod-folder-structure)
3. [Item Scripting](#item-scripting)
4. [Recipe Scripting (craftRecipe)](#recipe-scripting-craftrecipe)
5. [Container Mechanics](#container-mechanics)
6. [Lua Scripting](#lua-scripting)
7. [Key Gotchas and Verified IDs](#key-gotchas-and-verified-ids)
8. [Testing Workflow](#testing-workflow)
9. [Resources](#resources)

---

## Build 42 vs Build 41 — What Changed

If you find a modding tutorial online, there's a good chance it's for Build 41. B42 introduced several **breaking changes** that will silently fail or crash your mod if you follow old guides.

### The Three Big Breaks

#### 1. Mod Folder Structure
B41 mods had a flat `media/` folder at the mod root. B42 introduced versioned subfolders.

```
# B41 (old)
MyMod/
└── media/
    └── scripts/

# B42 (new — required)
MyMod/
└── 42/
    └── media/
        └── scripts/
```

The game now only loads files from the versioned folder matching the current build. You can support both builds simultaneously with separate `41/` and `42/` folders, but **if you only have `media/` at the root, your mod will not load in B42.**

One exception: a `common/` folder at the same level as `42/` is loaded by both builds. Use it for Lua that works on both. For any new B42-only mod, ignore `common/` and just use `42/`.

#### 2. Item Type Declaration
Every item must declare what kind of item it is. The property name and format changed completely.

```
# B41 (old — will break in B42)
Type = Container

# B42 (new — required)
ItemType = base:container
```

Common `ItemType` values:
- `base:container` — holds other items
- `base:normal` — generic item (materials, components)
- `base:food` — food item
- `base:weapon` — weapon
- `base:clothing` — wearable item

#### 3. Recipe System
The entire recipe system was replaced. Old `recipe { }` blocks no longer work.

```
# B41 (old — will not work in B42)
recipe Make Wooden Plank {
    TreeBranch=2,
    keep Saw,
    Result:WoodenPlank,
    Time:50.0,
    Category:Carpentry,
    SkillRequired:Woodwork=2,
}

# B42 (new)
craftRecipe MakeWoodenPlank
{
    timedAction   = Making,
    Time          = 50,
    category      = Carpentry,
    SkillRequired = Woodwork:2,

    inputs
    {
        item 2 [Base.TreeBranch],
        item 1 tags[base:saw] mode:keep,
    }

    outputs
    {
        item 1 Base.WoodenPlank,
    }
}
```

### Minor Breaking Changes by Sub-Version

#### 42.15
- **Translation files changed format.** Old: `.txt` files with language code in filename (`ItemName_EN.txt`). New: `.json` files without language code (`ItemName.json`), all UTF-8. Any mod with the old format will have broken translations in 42.15+.
- Fixed: mod folder detection — only one of `common/` or `42/` needs to exist.
- Added: `.glb` model file support in mod watcher.

#### 42.14
- `Base.223Bullets`, `Base.BoxBullets223`, `Base.CartonBullets223` removed. Replaced with 5.56 equivalents. Only affects ammo mods.
- New thread-equivalent items added: `Base.DentalFloss`, `Base.FishingLine` now accepted by `tags[base:thread]`.

---

## Mod Folder Structure

### Minimal Structure (B42 only)

```
MyMod/
├── workshop.txt                          ← Steam Workshop metadata
├── preview.png                           ← Workshop thumbnail
└── Contents/
    └── mods/
        └── MyMod/
            └── 42/
                ├── mod.info              ← Required. Mod identity.
                ├── poster.png            ← Optional thumbnail inside mod
                └── media/
                    ├── scripts/          ← Item + recipe .txt files
                    ├── lua/
                    │   ├── client/       ← Lua that runs on the client
                    │   └── server/       ← Lua that runs on the server
                    ├── textures/         ← Icons: item_YourIcon.png
                    └── models/           ← 3D models (.fbx, .b3d, .glb)
```

For local testing (non-Workshop), your mod goes in `~/Zomboid/mods/MyMod/` with the same internal structure.

### mod.info

```
name=My Mod Display Name
id=MyModID
author=YourName
description=What your mod does, shown in the mod list.
poster=poster.png
```

- `name` and `id` are required. Everything else is optional but recommended.
- `id` is used to reference this mod in dependencies: `require=SomeOtherModID`
- As of 42.15, mod name and description can be translated — see the Translation section.

### workshop.txt

```
version=1
workshopid=0
title=My Mod Display Name
description=Workshop description (can be longer than mod.info).
visibility=public
tags=Build 42;Items;Recipes
```

Set `workshopid=0` until you've published to Workshop — it gets assigned on first publish.

### Module Naming

When you define items and recipes, you declare a `module`. Items are then referenced as `ModuleName.ItemID` everywhere in the game (recipes, Lua, loot tables, etc.).

Two approaches:

**Use `module Base`** — your items join the vanilla Base namespace. Simpler references (`Base.MyItem`), but higher risk of ID collision with other mods. Fine for small mods.

**Use a custom module** — `module MyMod { }` means items are `MyMod.MyItem`. Safer, recommended for anything you plan to publish. Add `imports { Base }` inside your module block to reference vanilla items in recipes.

```
module MyMod
{
    imports
    {
        Base
    }

    item MyItem { ... }

    craftRecipe MakeMyItem
    {
        inputs { item 1 [Base.Plank], }   // vanilla item via import
        outputs { item 1 MyMod.MyItem, }  // our item via module name
    }
}
```

---

## Item Scripting

Scripts go in `42/media/scripts/` as `.txt` files. You can have multiple files — the game loads all of them. Splitting items and recipes into separate files (`items.txt`, `recipes.txt`) is a common convention.

### Basic Item Template

```
module MyMod
{
    item MyItemID
    {
        DisplayName         = My Item Display Name,
        DisplayCategory     = MyCategory,
        ItemType            = base:normal,
        Weight              = 1.0,
        Icon                = MyIcon,
    }
}
```

### Container Item Properties

The full set of properties relevant to bags, packs, and hauling items:

| Property | Type | Description |
|---|---|---|
| `ItemType` | string | `base:container` for anything that holds items |
| `Capacity` | int | Maximum encumbrance the container can hold. Hard-capped at 100 in vanilla B42. |
| `WeightReduction` | int | Percentage reduction applied to contents weight. `60` means contents weigh 40% of normal. |
| `RunSpeedModifier` | float | Speed multiplier when equipped. `0.5` = half speed. The game **stacks** all modifiers from all equipped/worn items additively (all differences from 1.0 are summed). |
| `TwoHandWeapon` | bool | Forces both hand slots to be occupied. Blocks attacking while held. |
| `Weight` | float | The item's own weight when carried. |
| `Tags` | string | Semicolon-separated tags controlling what can go inside and item behavior. `base:holdgeneral` allows general items. |
| `CloseSound` | string | Sound played when closing. `CloseSack` is a safe vanilla default. |
| `OpenSound` | string | Sound played when opening. `OpenSack` is a safe vanilla default. |
| `PutInSound` | string | Sound played when placing items inside. `StoreItemSack` is a safe default. |
| `ReplaceInPrimaryHand` | string | `ModelName AnimationName` — model and animation when held in right hand. |
| `ReplaceInSecondHand` | string | Model and animation when held in left hand. |
| `WorldStaticModel` | string | Model name when the item is dropped on the ground. |
| `Icon` | string | Filename of the icon (without extension). File must be in `media/textures/item_YourIcon.png`. |

### Two-Handed Hauling Item Pattern

This is the standard pattern for any item meant to simulate dragging/pushing:

```
item DragSledge
{
    DisplayName         = Drag Sledge,
    DisplayCategory     = Container,
    ItemType            = base:container,
    Weight              = 5.0,
    Icon                = WoodenPlank,          // placeholder until custom art
    Capacity            = 50,
    WeightReduction     = 65,
    RunSpeedModifier    = 0.45,                 // 45% of normal speed
    TwoHandWeapon       = TRUE,                 // blocks both hand slots + combat
    CloseSound          = CloseSack,
    OpenSound           = OpenSack,
    PutInSound          = StoreItemSack,
    Tags                = base:holdgeneral,
}
```

**Key design levers:**
- `RunSpeedModifier` is your primary balance tool. Lower = slower = more primitive.
- `TwoHandWeapon = TRUE` is what prevents combat while hauling. This is intentional game balance, not a bug.
- `Capacity` cap: vanilla B42 caps at 100. Items with very high carry needs require a Lua workaround.
- `WeightReduction` at 65–80% means the weight of contents is dramatically reduced, letting you move more than you could carry in a backpack.

### RunSpeedModifier Reference (this mod)

| Item | Modifier | Effective Speed |
|---|---|---|
| Stick Travois | 0.35 | 35% — barely walking |
| Lashed Travois | 0.40 | 40% |
| Drag Sledge | 0.45 | 45% |
| Stone Wheelbarrow | 0.50 | 50% — slow jog |
| Metal-Axled Stone Wheelbarrow | 0.55 | 55% |
| Wooden Wheelbarrow | 0.65 | 65% |
| Reinforced Wheelbarrow | 0.70 | 70% |
| Shoulder Yoke | 0.85 | 85% — near-normal |
| Padded Yoke | 0.90 | 90% |

---

## Recipe Scripting (craftRecipe)

### Full Syntax Reference

```
craftRecipe UniqueRecipeID
{
    timedAction     = Making,
    Time            = 300,
    category        = Carpentry,
    SkillRequired   = Woodwork:3;Metalwork:1,
    xpAward         = Woodwork:60;Metalwork:20,
    Tags            = InHandCraft,
    needToBeLearn   = false,

    inputs
    {
        item 4 [Base.Plank],
        item 8 [Base.Nails],
        item 1 tags[base:hammer] mode:keep,
        item 1 tags[base:saw] mode:keep,
    }

    outputs
    {
        item 1 MyMod.MyItem,
    }
}
```

### Parameters

| Parameter | Format | Notes |
|---|---|---|
| `timedAction` | `= Making` | Animation to play during craft. Common values: `Making`, `SawLog`, `Carpentry`. |
| `Time` | `= 300` | Duration in **tenths of a second**. 300 = 30 seconds. |
| `category` | `= Carpentry` | Groups the recipe in the crafting UI. |
| `SkillRequired` | `= Woodwork:3` | Skill gate. Semicolon-separated for multiple: `Woodwork:3;Metalwork:1`. Player needs ALL listed skills. |
| `xpAward` | `= Woodwork:60` | XP granted on completion. Semicolon-separated for multiple skills. |
| `Tags` | `= InHandCraft` | Flags. `InHandCraft` means recipe appears in the standard crafting menu. |
| `needToBeLearn` | `= false` | `true` = recipe requires finding a recipe book first. `false` = available by default. |
| `OnCreate` | `= Recipe.OnCreate.MyFunc` | Lua function called after craft completes. |
| `OnTest` | `= Recipe.OnTest.MyFunc` | Lua function called to test if recipe is available (return bool). |

### inputs Block

```
inputs
{
    // Consumed (destroyed) — default behavior
    item 4 [Base.Plank],

    // Tool — not consumed
    item 1 tags[base:hammer] mode:keep,

    // Specific item, not consumed
    item 1 [Base.Nails] mode:keep,

    // Any item matching a tag, not consumed, with flags
    item 1 tags[base:saw] mode:keep flags[MayDegradeLight],
}
```

**Critical rule:** Items are **consumed (destroyed) by default**. You must add `mode:keep` for tools and anything that shouldn't be used up.

**Tag matching** (`tags[base:tagname]`) accepts any item in the game that has that tag. This is how recipes accept "any hammer" rather than a specific hammer item ID. Use tags for tools wherever possible — it's more compatible with other mods that add new tool types.

### outputs Block

```
outputs
{
    item 1 MyMod.MyItem,        // one item
    item 3 Base.Plank,          // multiple of same item
}
```

Note: outputs use `Module.ItemID` **without brackets**, unlike inputs which use `[Module.ItemID]` with brackets.

### Upgrade Path Pattern

To create a recipe that consumes a previous tier as a base component, just list it as a normal consumed input:

```
craftRecipe UpgradeToWoodenWheelbarrow
{
    ...
    inputs
    {
        item 1 [MyMod.DragSledge],          // consumed — becomes the wheelbarrow base
        item 1 [MyMod.CarvedWoodWheel],      // consumed — the wheel
        item 2 [Base.Plank],
        item 6 [Base.Nails],
        item 1 tags[base:hammer] mode:keep,
    }

    outputs
    {
        item 1 MyMod.WoodenWheelbarrow,
    }
}
```

The player will feel like they "upgraded" their drag sledge into a wheelbarrow because the sledge is consumed in the process — their earlier work carries forward.

### Skill Names

These are the internal skill ID strings used in `SkillRequired` and `xpAward`:

| Skill | Internal ID | TODO:VERIFY |
|---|---|---|
| Carpentry | `Woodwork` | ✓ confirmed |
| Metalworking | `Metalwork` | needs verification |
| Masonry | `Masonry` | needs verification |
| Carving | `Carving` | needs verification |
| Tailoring | `Tailoring` | needs verification |

> **Note:** This section will be updated as skills are verified in-game. The internal IDs are not always the same as the display names.

---

## Container Mechanics

### How Capacity Works

`Capacity` is the maximum total encumbrance of items stored inside the container. Each item in the game has a `Weight` value — when placed in a container with `WeightReduction = 60`, that item effectively weighs 40% of its normal value toward the container's capacity.

Example: A container with `Capacity = 50` and `WeightReduction = 65`:
- Item weighing 5.0 effectively weighs 1.75 (5.0 × 0.35)
- So you can fit ~28 of that item before hitting the capacity limit

The **100 capacity hard cap** in vanilla B42 is a known limitation. If you need more, the community workaround is to use a Lua `OnContainerUpdate` hook to manipulate the container — but this is poorly documented and needs testing.

### Lua Container API

```lua
local item = player:getPrimaryHandItem()
if item then
    local container = item:getContainer()
    if container then
        local capacity  = container:getCapacity()     -- max capacity
        local weight    = container:getWeight()       -- current contents weight
        local fillRatio = weight / capacity           -- 0.0 to 1.0

        -- Iterate contents
        local items = container:getItems()            -- Java ArrayList
        for i = 0, items:size() - 1 do
            local storedItem = items:get(i)
            -- do something with storedItem
        end

        -- Add/remove items
        container:AddItem("Base.SomeItem")            -- add by string ID
        container:Remove(someInventoryItem)           -- remove by InventoryItem reference
        container:contains(someInventoryItem)         -- boolean check
    end
end
```

---

## Lua Scripting

### File Location

Client Lua: `42/media/lua/client/`
Server Lua: `42/media/lua/server/`
Shared Lua: `42/media/lua/shared/` (loaded by both)

The game loads all `.lua` files in these directories automatically — no registration needed.

### Event System

PZ uses a global `Events` object. You register a Lua function to be called when an event fires:

```lua
local function myHandler(player)
    -- your logic
end

Events.OnPlayerUpdate.Add(myHandler)

-- Remove when no longer needed
Events.OnPlayerUpdate.Remove(myHandler)
```

### Key Events for Item/Container Mods

| Event | When it fires | Parameters |
|---|---|---|
| `OnPlayerUpdate` | Every game tick per player | `(IsoPlayer player)` |
| `OnPlayerMove` | Every tick the local player moves | `(IsoPlayer player)` |
| `OnCreatePlayer` | Player spawns into world | `(int playerIndex, IsoPlayer player)` |
| `OnFillInventoryObjectContextMenu` | Player right-clicks an item | `(int playerNum, ISContextMenu menu, ArrayList items)` |
| `OnContainerUpdate` | Container contents change | varies |
| `EveryOneMinute` | Every in-game minute | none |

### OnPlayerUpdate Performance

`OnPlayerUpdate` fires **every game tick** for every player. Keep your handlers fast:

```lua
local MY_ITEM = "MyMod.MyItem"

local function onPlayerUpdate(player)
    -- Always guard against nil first
    if not player then return end

    -- Exit early if player isn't holding our item
    local primary = player:getPrimaryHandItem()
    if not primary or primary:getFullType() ~= MY_ITEM then return end

    -- Only now do more expensive operations
    local container = primary:getContainer()
    -- ...
end

Events.OnPlayerUpdate.Add(onPlayerUpdate)
```

Avoid creating tables or objects inside `OnPlayerUpdate`. Cache anything reusable at module level.

### Drop-on-Aim Pattern

For two-handed hauling items, you may want the item to drop automatically when the player tries to aim a weapon. Whether `TwoHandWeapon = TRUE` already prevents aiming in B42 is **not yet verified** — but if it doesn't, this pattern handles it:

```lua
local HAUL_ITEMS = {
    ["MyMod.DragSledge"]        = true,
    ["MyMod.WoodenWheelbarrow"] = true,
    -- add all haul items here
}

local function onPlayerUpdate(player)
    if not player then return end
    local primary = player:getPrimaryHandItem()
    if not primary or not HAUL_ITEMS[primary:getFullType()] then return end

    if player:isAiming() then
        -- TODO:VERIFY these are the correct unequip methods in B42
        player:setPrimaryHandItem(nil)
        player:setSecondaryHandItem(nil)
    end
end

Events.OnPlayerUpdate.Add(onPlayerUpdate)
```

### IsoPlayer Common Methods

```lua
player:getPrimaryHandItem()         -- InventoryItem or nil
player:getSecondaryHandItem()       -- InventoryItem or nil
player:setPrimaryHandItem(item)     -- equip item (nil to unequip)
player:setSecondaryHandItem(item)   -- equip item (nil to unequip)
player:getInventory()               -- ItemContainer (main inventory)
player:isAiming()                   -- bool
player:getVehicle()                 -- IsoVehicle or nil (nil if on foot)
player:getX(), player:getY(), player:getZ()  -- world coordinates
```

### InventoryItem Common Methods

```lua
item:getFullType()      -- "Module.ItemID" e.g. "Base.Plank"
item:getType()          -- "ItemID" without module e.g. "Plank"
item:getContainer()     -- ItemContainer if this is a container item, else nil
item:getWeight()        -- item's weight value
item:getCondition()     -- durability (0-100)
item:getDisplayName()   -- localized display name string
```

---

## Key Gotchas and Verified IDs

A running list of things that have burned time or need in-game verification. **Update this as items are confirmed on the gaming machine.**

### Confirmed Working
- `module Base { item ... }` — items join the Base namespace correctly
- `ItemType = base:container` — B42 container type
- `TwoHandWeapon = TRUE` — forces both hand slots
- `RunSpeedModifier` — stacks correctly with other equipped items
- `SkillRequired = Woodwork:2` — Carpentry skill gate confirmed working

### Needs In-Game Verification

| What | Our assumption | How to check |
|---|---|---|
| Tree branch item ID | `Base.TreeBranch` | Check inventory on a fallen tree |
| Twine item ID | `Base.Twine` | Check crafting/inventory |
| Sheet item ID | `Base.Sheet` or `Base.Sheets` | Check inventory |
| Log item ID | `Base.Log` | Check woodcutting output |
| Stone wheel item ID | `Base.StoneWheel` | Check Masonry crafting menu |
| Metal pipe item ID | `Base.MetalPipe` | Check hardware store loot |
| Vanilla wooden rod ID | `Base.WoodenRod` | Check Carving crafting output |
| Carving tool tag | `tags[base:knifesharp]` | Check if knife appears in carving recipes |
| Needle tag | `tags[base:needle]` | Check tailoring recipes |
| Metalwork skill ID | `Metalwork` | Check a vanilla metalworking recipe |
| Masonry skill ID | `Masonry` | Check a vanilla masonry recipe |
| Carving skill ID | `Carving` | Check a vanilla carving recipe |
| Does TwoHandWeapon prevent aiming? | Assumed yes | Equip item and try to right-click aim |

### Common Mistakes

**Item not appearing in game:** Check that your module declaration is correct and the file is in `42/media/scripts/`. Also check the game's console log — script parse errors are printed there.

**Recipe not appearing:** The `category` value must match a valid crafting category. Common categories: `Carpentry`, `Tailoring`, `Metalwork`, `Masonry`, `Cooking`, `Farming`. Wrong category = recipe still exists but may be hard to find.

**Items being destroyed when they should be kept:** Forgot `mode:keep` on a tool input. All inputs are consumed by default.

**Mod not loading at all:** Check `mod.info` is inside `42/` (not at the root). Check `id` field has no spaces.

**Old B41 mod not working in B42:** The three big breaks — folder structure, `Type =` vs `ItemType =`, and `recipe {}` vs `craftRecipe {}` — cover 95% of cases.

---

## Testing Workflow

### Setup

1. Clone/copy your mod into `~/Zomboid/mods/YourModID/` (the folder name should match the `id` in `mod.info`)
2. Launch PZ, go to **Mods**, enable your mod
3. Start a new save in **Sandbox** mode — use a custom preset with high XP gain and all skills maxed so you can test any recipe immediately

### Console / Debug Output

Enable the debug console: launch PZ with `-debug` flag, or press `F11` in-game to open the debug panel.

Lua errors print to:
- The in-game console (open with `` ` `` key by default)
- `~/Zomboid/Logs/` — check `*.txt` files here for script parse errors on startup

### Quick Iteration

You **do not** need to restart the game to reload Lua changes. In the debug console:

```
/reloadlua
```

However, **item script and recipe changes do require a full restart** — those are parsed at game load, not at runtime.

### Checking Item IDs In-Game

With debug mode enabled:
- Open your inventory and hover over any item
- The debug tooltip shows the full item ID (`Module.ItemID`)
- Use this to verify any `TODO:VERIFY` IDs in your scripts

---

## Resources

### Official / Semi-Official

- [PZwiki — Mod Structure](https://pzwiki.net/wiki/Mod_structure)
- [PZwiki — Item Scripts](https://pzwiki.net/wiki/Item_(scripts))
- [PZwiki — craftRecipe Scripts](https://pzwiki.net/wiki/CraftRecipe_(scripts))
- [PZwiki — inputs block](https://pzwiki.net/wiki/Inputs)
- [PZwiki — Lua Events](https://pzwiki.net/wiki/Lua_Events)
- [PZwiki — Getting Started with Modding](https://pzwiki.net/wiki/Getting_started_with_modding)
- [Official JavaDocs](https://projectzomboid.com/modding/) — Java class reference, the closest thing to an official API doc
- [Unofficial JavaDocs (B42)](https://pzwiki.net/wiki/Unofficial_JavaDocs_(Build_42)) — community-maintained, more complete

### Community Tools

- [PZ Lua Event Docs](https://demiurgequantified.github.io/ProjectZomboidLuaDocs/md_Events.html) — best reference for event signatures
- [PZ Event Stubs (GitHub)](https://github.com/demiurgeQuantified/PZEventStubs) — IDE intellisense stubs for PZ events
- [B42 Mod Template (GitHub)](https://github.com/LabX1/ProjectZomboid-Build42-ModTemplate) — working B42 starter template
- [Awesome B42 Resources (GitHub)](https://github.com/JBD-Mods/awesome-project-zomboid-build42-resources) — curated tool list

### Reference Mods (Study These)

- [Hydrocraft Wheelbarrow (Workshop)](https://steamcommunity.com/sharedfiles/filedetails/?id=2926995676) — simple B42 container item, good starting reference
- [SaucedCarts (Workshop)](https://steamcommunity.com/sharedfiles/filedetails/?id=3651954650) — advanced ground-object push system, B42-native

### Migration Guides

- [B42 Modding Migration Guide (42.15) — The Indie Stone Forums](https://theindiestone.com/forums/index.php?/topic/92433-modding-migration-guide-4215/) — covers the translation format change
- [How to Update Your Mod for Build 42 (Steam Guide)](https://steamcommunity.com/sharedfiles/filedetails/?id=3391657438)

---

*This guide is maintained alongside [The Long Haul mod](https://github.com/gotmayonase/the-long-haul). Last updated: March 2026.*
