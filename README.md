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

### Wheelbarrow Line
Each tier is crafted by upgrading the previous. The Drag Sledge is the required starting point.

| Item | Carpentry | Other Skills | Capacity | Speed | Notes |
|---|---|---|---|---|---|
| Stone Wheelbarrow | 3 | Masonry 3 | 60 / 70% reduction | 50% | Stone wheel mounted on a Drag Sledge frame. Heavy but durable. |
| Wooden Wheelbarrow | 4 | — | 70 / 75% reduction | 65% | Stone wheel swapped for a carved or assembled wooden wheel. |
| Reinforced Wheelbarrow | 4 | Metalwork 2 | 80 / 80% reduction | 70% | Metal-reinforced axle and frame. Best all-around. |

### Wheel Components
Sub-components required for the wheelbarrow upgrade path.

| Item | Skills Required | Notes |
|---|---|---|
| Wooden Rod | Carving 1 | Carved from a branch. Yields 2 per branch. Used as spokes. |
| Carved Wooden Wheel | Carving 4 | Solid disc carved from a log. Heavy. Can be used standalone or as hub. |
| Assembled Wooden Wheel | Carpentry 4 | Spoked wheel built around a carved hub + wooden rods. Lighter and faster. |

---

## Full Upgrade Paths

```
Stick Travois ──(+canvas)──► Lashed Travois
                                             \
Branches + Nails + Metal ──────────────────► Drag Sledge ──(+StoneWheel)──► Stone Wheelbarrow
                                                                                               |
                                                                             (+CarvedWoodWheel)├──► Wooden Wheelbarrow ──(+Metal)──► Reinforced Wheelbarrow
                                                                           (+AssembledWoodWheel)┘

Branch + Twine ──────────────────────────────────────────────────────────► Shoulder Yoke ──(+Rags)──► Padded Yoke
```

---

## Balance Notes

- **Both hands required** — you cannot attack while holding any haul item
- **Speed penalty** — the more primitive the item, the slower you move; a full Stone Wheelbarrow moves at 50% speed
- **Upgrade path** — each wheelbarrow tier consumes the previous as a component, so earlier work carries forward
- **Two wheel paths** — the Wooden Wheelbarrow can be built via Carving 4 (Carved Wheel) or Carpentry 4 + Carving (Assembled Wheel); the assembled path is slightly faster to craft once components are made

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
