# Pidgey Power

A small add-on patch for **Pokémon Blaze Black 2 Redux v1.4.1 (Complete)** that turns the Pidgey line into a legendary-tier special attacker.

This is an add-on, just like Redux's own Classic / EV-less patches. You apply it **on top of a Blaze Black 2 Redux ROM**, not vanilla Black 2. No ROMs are distributed here.

## What it does

| Stage | HP | Atk | Def | SpA | SpD | Spe | BST |
|-------|----|-----|-----|-----|-----|-----|-----|
| Pidgey | 60 | 50 | 58 | 88 | 62 | 92 | **410** |
| Pidgeotto | 78 | 62 | 72 | 105 | 78 | 105 | **500** |
| Pidgeot | 95 | 75 | 90 | 145 | 95 | 135 | **635** |

- **No Guard** in ability slot 1 on all three stages, so Hurricane and Sky Attack never miss.
- Typing stays Normal/Flying. Evolutions unchanged (Pidgeotto at 18, Pidgeot at 36).
- Front-loaded movepool, shared by the line: Air Slash by Lv 5, then Roost (9), Ominous Wind (13), Tailwind (17), Hurricane (21), Heat Wave (25), Hyper Voice (29), Agility (33), Sky Attack (41). A level-5 Pidgey starts with Tackle / Quick Attack / Gust / Air Slash.

Catch a Pidgey on **Route 19** (or Route 1 in the postgame) to use it.

## Quick Search

Speed Boost has been reskinned as **Quick Search**, after Pidgeot's Poke-Power in EX FireRed & LeafGreen. New name, new description ("Searches out an extra Energy every turn."), same relentless effect: +1 Speed at the end of every turn.

The Pidgey line now carries it in ability slot 2, with No Guard still in slot 1, so a wild Pidgey can roll either. Every other Speed Boost Pokémon in the game shows the new name too, since it is the same ability under the hood.

## Trainer Spencer

Youngster Masahiro at the **Virbank Complex** is now **Youngster Spencer**, running the three Unova starters:

- Snivy lv. 15 (Overgrow): Vine Whip, Wrap, Growth, Leaf Tornado
- Tepig lv. 15 (Blaze): Ember, Tackle, Defense Curl, Flame Charge
- Oshawott lv. 16 (Torrent): Water Gun, Razor Shell, Focus Energy, Tackle

Same spot as the original trainer, one level off the area curve, minus 1 on Easy and plus 1 on Challenge like the rest of the Complex.

## Requirements

A clean **Pokémon Blaze Black 2 Redux v1.4.1 (Complete)** `.nds`, which you build yourself from a clean Pokémon Black 2 (USA) ROM plus Drayano's Redux Complete patch (Drayano releases it via [@Drayano60](https://twitter.com/Drayano60)). This repo does not host any ROMs.

## How to apply

### Desktop

1. Build your Blaze Black 2 Redux v1.4.1 `.nds` (clean Black 2 USA + Redux Complete patch).
2. Apply the patch on top of it:
   - **xdelta3:** `xdelta3 -d -s "Blaze Black 2 Redux.nds" "Pidgey-Power_over_Blaze-Black-2-Redux-v1.4.1.xdelta" "Pidgey Power.nds"`
   - or the web patcher [RomPatcher.js](https://www.marcrobledo.com/RomPatcher.js/): source = your Redux `.nds`, patch = this `.xdelta`.
3. Play `Pidgey Power.nds` in any DS emulator (melonDS recommended).

### Mobile

Do the whole thing on a phone, or just copy a desktop-patched `.nds` onto your device.

- **iOS:** patch in Safari with [RomPatcher.js](https://www.marcrobledo.com/RomPatcher.js/), then import the result into [Delta](https://deltaemulator.com/).
- **Android:** patch with **Unipatcher** (supports xdelta) or RomPatcher.js in your browser, then load it in **DraStic**, **melonDS**, or RetroArch (melonDS core).

## Build it yourself

`build_pidgey_power.py` is the exact script that produces this mod. It edits the Pokémon personal data (`a/0/1/6`), level-up learnsets (`a/0/1/8`), trainer Pokémon (`a/0/9/2`), and the trainer name text (`a/0/0/2`) directly with [ndspy](https://pypi.org/project/ndspy/).

```bash
pip install ndspy
python build_pidgey_power.py "Blaze Black 2 Redux.nds" "Pidgey Power.nds"
# then regenerate the patch:
xdelta3 -e -s "Blaze Black 2 Redux.nds" "Pidgey Power.nds" out.xdelta
```

## Credit

Built on **Pokémon Blaze Black 2 Redux** by **Drayano**. This patch only changes the Pidgey line; everything else is Drayano's work. Not affiliated with or endorsed by Nintendo or Game Freak.
