# The Long Haul

A Project Zomboid mod (Build 42.15+) adding tiered primitive hauling tools for wilderness survival runs.

Vanilla PZ has no way to move large quantities of supplies without making many trips. This mod adds a progression of hand-crafted hauling tools — from a stick travois lashed together on day one to a reinforced wheelbarrow built from hard-won skills and materials.

All haul items occupy both hands and slow your movement. You can't fight while using them. Survival has a cost.

---

## Progression Overview

### Travois Line
Drag-based hauling. High speed penalty, available early.

| Item | Carpentry | Other Skills | Capacity | Speed | Notes |
|---|---|---|---|---|---|
| Stick Travois | 0 | — | 20 / 50% reduction | 35% | Branches + twine. Day-one craft. |
| Lashed Travois | 0 | Tailoring 1 | 35 / 60% reduction | 40% | Adds canvas platform. Upgrade from Stick Travois. |
| Drag Sledge | 3 | Metalwork 1 | 50 / 65% reduction | 45% | Plank runners with metal strips. Base component for wheelbarrows. |

### Shoulder Yoke Line
Balanced across both shoulders. Lower speed penalty than drag items. Best for water and container hauling.

| Item | Carpentry | Other Skills | Capacity | Speed | Notes |
|---|---|---|---|---|---|
| Shoulder Yoke | 0 | — | 20 / 40% reduction | 85% | Single branch, notched ends. |
| Padded Yoke | 0 | Tailoring 2 | 30 / 50% reduction | 90% | Rag padding for longer carries. Upgrade from Shoulder Yoke. |

### Stone Wheelbarrow Line
Masonry path. Branches from the Drag Sledge. Identity: highest capacity and durability, lower speed.

| Item | Carpentry | Other Skills | Capacity | Speed | Notes |
|---|---|---|---|---|---|
| Stone Wheelbarrow | 3 | Masonry 3 | 65 / 72% reduction | 50% | Stone wheel on a Drag Sledge frame. Heavy, durable. |
| Metal-Axled Stone Wheelbarrow | — | Masonry 3, Metalwork 2 | 90 / 85% reduction | 55% | Metal reinforcement. Highest capacity of any wheelbarrow. |

### Wooden Wheelbarrow Line
Carpentry/Carving path. Branches from the Drag Sledge independently of the stone line. Identity: best speed, good capacity.

| Item | Carpentry | Other Skills | Capacity | Speed | Notes |
|---|---|---|---|---|---|
| Wooden Wheelbarrow | 4 | — | 70 / 75% reduction | 65% | Built directly from Drag Sledge + wooden wheel (two recipe paths). |
| Reinforced Wheelbarrow | 4 | Metalwork 2 | 80 / 80% reduction | 70% | Metal-reinforced axle and frame. Best speed. |

### Wheel Components
Sub-components for the wooden wheelbarrow line.

| Item | Skills Required | Notes |
|---|---|---|
| Wooden Rod | Carving 1 (vanilla) | Already in the game — crafted via the Carving skill. Used as spokes. |
| Carved Wooden Wheel | Carving 4 | Solid disc carved from a log. Heavy. Standalone wheel or hub for assembled. |
| Assembled Wooden Wheel | Carpentry 4 | Spoked wheel: carved hub + vanilla wooden rods. Lighter and faster. |

---

## Full Upgrade Paths

```
Stick Travois ──(+canvas)──► Lashed Travois
                                             \
Branches + Nails + Metal ──────────────────► Drag Sledge ──┬──(+StoneWheel, Masonry 3)──────────────► Stone Wheelbarrow ──(+Metal, Metalwork 2)──► Metal-Axled Stone Wheelbarrow
                                                            │                                                                                       (highest capacity, very durable)
                                                            │
                                                            ├──(+CarvedWoodWheel, Carp 4)────────────┐
                                                            │                                        ├──► Wooden Wheelbarrow ──(+Metal, Metalwork 2)──► Reinforced Wheelbarrow
                                                            └──(+AssembledWoodWheel, Carp 4)─────────┘                                               (best speed)

Branch + Twine ──► Shoulder Yoke ──(+Rags)──► Padded Yoke
```

---

## Balance Notes

- **Both hands required** — you cannot attack while holding any haul item
- **Speed penalty** — the more primitive the item, the slower you move; a full Stone Wheelbarrow moves at 50% speed
- **Upgrade path** — each wheelbarrow tier consumes the previous as a component, so earlier work carries forward
- **Two independent wheelbarrow lines** — Stone (Masonry path, tank stats) and Wooden (Carpentry/Carving path, speed stats) both branch from the Drag Sledge; neither is a prerequisite for the other
- **Two wheel paths into Wooden** — via Carving 4 (Carved Wheel, simpler) or Carpentry 4 + Carving (Assembled Wheel, lighter/faster result)

---

## Known Limitations / TODO

- **No custom icons** — all items currently display a placeholder vanilla icon
- **No custom models** — items have no 3D model when held or dropped on the ground
- **Vanilla item IDs need in-game verification** — several item references (stone wheel, branches, twine, metal pipe) are best guesses and need confirming against actual game files before publishing
- **Skill name verification needed** — `Masonry`, `Carving`, `Metalwork` skill IDs need confirming against the game API
- **No translation file** — item and recipe names use inline `DisplayName` values only; proper 42.15+ JSON translation files not yet added
- **Drop-on-aim** — the Lua speed manager includes drop-on-aim logic, but it needs in-game testing to confirm whether `TwoHandWeapon = TRUE` already handles this natively in B42

---

## Building / Testing

Clone directly into your Zomboid mods folder:

```bash
# Windows
git clone https://github.com/gotmayonase/the-long-haul "%USERPROFILE%\Zomboid\mods\TheLongHaul"

# Linux / macOS
git clone https://github.com/gotmayonase/the-long-haul ~/Zomboid/mods/TheLongHaul
```

Enable **The Long Haul** in the mod list, start a new save, and check the Carpentry crafting menu.

---

## Requirements

- Project Zomboid Build **42.15+** (unstable branch)

---

## Modding Guide

Building this mod came with a lot of hard-won knowledge about B42 modding that's poorly documented elsewhere. That's captured in [`docs/modding-guide.md`](docs/modding-guide.md) — a practical guide covering mod structure, item scripting, the new `craftRecipe` system, Lua hooks, container mechanics, and common gotchas. Updated as development continues.
