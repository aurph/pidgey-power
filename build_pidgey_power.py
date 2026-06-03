#!/usr/bin/env python3
"""Build the Pidgey Power mod.

Applies the Pidgey-line buffs (base stats, the No Guard ability, and a
front-loaded special-attacker movepool) to a Pokemon Blaze Black 2 Redux
v1.4.1 (Complete) ROM. Types and evolutions are left unchanged.

Requires ndspy:  pip install ndspy

Usage:
    python build_pidgey_power.py <Blaze Black 2 Redux .nds> [output .nds]
"""
import sys
import struct
import ndspy.rom
import ndspy.narc

PIDGEY, PIDGEOTTO, PIDGEOT = 16, 17, 18
ABIL1 = 0x18  # ability slot 1 offset inside a personal record

# New base stats in ROM byte order: HP, Atk, Def, Speed, SpAtk, SpDef
NEW_STATS = {
    PIDGEY:    [60, 50, 58, 92, 88, 62],    # display 60/50/58/88/62/92  = 410
    PIDGEOTTO: [78, 62, 72, 105, 105, 78],  # display 78/62/72/105/78/105 = 500
    PIDGEOT:   [95, 75, 90, 135, 145, 95],  # display 95/75/90/145/95/135 = 635
}

# Shared front-loaded learnset, (move_id, level)
LEARNSET = [
    (33, 1), (98, 1), (16, 3), (403, 5), (355, 9), (466, 13),
    (366, 17), (542, 21), (257, 25), (304, 29), (97, 33), (143, 41),
]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "Pidgey Power.nds"

    rom = ndspy.rom.NintendoDSRom.fromFile(src)
    personal = ndspy.narc.NARC(rom.getFileByName("a/0/1/6"))
    learn = ndspy.narc.NARC(rom.getFileByName("a/0/1/8"))

    # Read No Guard's ability id straight off Pidgeot (Redux already gives it).
    no_guard = personal.files[PIDGEOT][ABIL1]

    for species, stats in NEW_STATS.items():
        rec = bytearray(personal.files[species])
        rec[0:6] = bytes(stats)
        rec[ABIL1] = no_guard
        personal.files[species] = bytes(rec)

    wotbl = b"".join(struct.pack("<HH", m, l) for m, l in LEARNSET) + b"\xff\xff\xff\xff"
    for species in (PIDGEY, PIDGEOTTO, PIDGEOT):
        learn.files[species] = wotbl

    rom.setFileByName("a/0/1/6", personal.save())
    rom.setFileByName("a/0/1/8", learn.save())
    rom.saveToFile(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
