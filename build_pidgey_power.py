#!/usr/bin/env python3
"""Build the Pidgey Power mod.

Applies to a Pokemon Blaze Black 2 Redux v1.4.1 (Complete) ROM:
  1. Pidgey-line buffs: base stats, the No Guard ability, and a front-loaded
     special-attacker movepool. Types and evolutions are left unchanged.
  2. Trainer Spencer: Youngster Masahiro at the Virbank Complex (trainer 745)
     becomes Youngster Spencer, running the three Unova starters.

Requires ndspy:  pip install ndspy

Usage:
    python build_pidgey_power.py <Blaze Black 2 Redux .nds> [output .nds]
"""
import sys
import struct
import ndspy.rom
import ndspy.narc

# ---------------- Pidgey line ----------------
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

# ---------------- Quick Search (reskinned Moody) ----------------
# Moody (ability 141) is renamed to "Quick Search" with TCG flavor text, as a
# nod to Pidgeot's Poke-Power in EX FireRed & LeafGreen. The Pidgey line gets
# it in ability slot 2; No Guard stays in slot 1. Effect is Moody's: at the
# end of each turn, one stat is sharply raised and another is lowered.
MOODY = 141
ABIL2 = 0x19                   # ability slot 2 offset inside a personal record
ABILITY_NAMES_FILE = 374       # a/0/0/2 text NARC, entry index == ability id
ABILITY_NAMES_UPPER_FILE = 487 # all-caps duplicate of the ability names
ABILITY_DESC_FILE = 375        # ability descriptions
QS_NAME = "Quick Search"
QS_DESC = "Searches up something\nbroken every turn."

# ---------------- Trainer Spencer ----------------
SPENCER_TRAINER = 745          # Youngster Masahiro, Virbank Complex
SPENCER_NAME = "Spencer"
TRAINER_NAMES_FILE = 382       # inside the a/0/0/2 text NARC

# Format-1 trainer pokemon: iv u8, pid u8, level u16, species u16, form u16,
# then four move u16s. pid 0x20 = ability slot 2, which in Redux Complete is
# the classic starter ability (Overgrow / Blaze / Torrent).
SPENCER_TEAM = [
    # (species, level, [move1, move2, move3, move4])
    (495, 15, [22, 35, 74, 536]),    # Snivy: Vine Whip, Wrap, Growth, Leaf Tornado
    (498, 15, [52, 33, 111, 488]),   # Tepig: Ember, Tackle, Defense Curl, Flame Charge
    (501, 16, [55, 534, 116, 33]),   # Oshawott: Water Gun, Razor Shell, Focus Energy, Tackle
]


def build_spencer_pokes():
    out = b""
    for species, level, moves in SPENCER_TEAM:
        out += struct.pack("<BBHHH", 0, 0x20, level, species, 0)
        out += struct.pack("<4H", *moves)
    return out


# ---------------- Gen 5 text codec ----------------
# Strings are XOR-encrypted; the per-entry key schedule rotates left 3 bits per
# character. The starting key is recovered by walking back from the 0xFFFF
# terminator, so no magic constants are needed.

def _ror16(v, n):
    return ((v >> n) | (v << (16 - n))) & 0xFFFF


def _entry_key0(chars):
    key = chars[-1] ^ 0xFFFF
    for _ in range(len(chars) - 1):
        key = _ror16(key, 3)
    return key


def _crypt(chars, key):
    out = []
    for c in chars:
        out.append(c ^ key)
        key = ((key << 3) | (key >> 13)) & 0xFFFF
    return out


def _unpack9(chars):
    """Undo the 0xF100 9-bit packing some strings use."""
    acc = nbits = 0
    out = []
    for v in chars:
        acc |= v << nbits
        nbits += 16
        while nbits >= 9:
            c = acc & 0x1FF
            acc >>= 9
            nbits -= 9
            if c == 0x1FF:
                return out
            out.append(c)
    return out


def rename_text_entry(data, index, new_text, expect_old=None):
    """Replace one entry of a single-section Gen 5 text file, preserving the
    encryption key schedule and flags of the original entry. The replacement
    is written uncompressed, which the engine reads fine."""
    nsec, nent = struct.unpack_from("<HH", data, 0)
    assert nsec == 1, f"expected 1 section, got {nsec}"
    unk8 = struct.unpack_from("<I", data, 8)[0]
    so = struct.unpack_from("<I", data, 12)[0]

    entries = []
    for i in range(nent):
        off, clen, flags = struct.unpack_from("<IHH", data, so + 4 + i * 8)
        chars = list(struct.unpack_from(f"<{clen}H", data, so + off))
        entries.append([flags, chars])

    old = entries[index][1]
    key0 = _entry_key0(old)
    dec = _crypt(old, key0)
    assert dec[-1] == 0xFFFF, "terminator not found; key recovery failed"
    body = dec[:-1]
    if body and body[0] == 0xF100:
        body = _unpack9(body[1:])
    oldname = "".join("\n" if c == 0xFFFE else chr(c) for c in body)
    if expect_old is not None:
        assert oldname == expect_old, f"slot holds {oldname!r}, not {expect_old!r}"

    new_chars = [0xFFFE if c == "\n" else ord(c) for c in new_text] + [0xFFFF]
    entries[index][1] = _crypt(new_chars, key0)

    table = b""
    blob = b""
    base = 4 + nent * 8
    for flags, chars in entries:
        table += struct.pack("<IHH", base + len(blob), len(chars), flags)
        blob += struct.pack(f"<{len(chars)}H", *chars)
    section = struct.pack("<I", 4 + len(table) + len(blob)) + table + blob
    header = struct.pack("<HHII", 1, nent, len(section), unk8) + struct.pack("<I", 16)
    return header + section, oldname


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "Pidgey Power.nds"

    rom = ndspy.rom.NintendoDSRom.fromFile(src)

    # --- Pidgey line ---
    personal = ndspy.narc.NARC(rom.getFileByName("a/0/1/6"))
    learn = ndspy.narc.NARC(rom.getFileByName("a/0/1/8"))

    # Read No Guard's ability id straight off Pidgeot (Redux already gives it).
    no_guard = personal.files[PIDGEOT][ABIL1]

    for species, stats in NEW_STATS.items():
        rec = bytearray(personal.files[species])
        rec[0:6] = bytes(stats)
        rec[ABIL1] = no_guard
        rec[ABIL2] = MOODY      # Quick Search in slot 2
        personal.files[species] = bytes(rec)

    wotbl = b"".join(struct.pack("<HH", m, l) for m, l in LEARNSET) + b"\xff\xff\xff\xff"
    for species in (PIDGEY, PIDGEOTTO, PIDGEOT):
        learn.files[species] = wotbl

    rom.setFileByName("a/0/1/6", personal.save())
    rom.setFileByName("a/0/1/8", learn.save())

    # --- Spencer: team ---
    trpoke = ndspy.narc.NARC(rom.getFileByName("a/0/9/2"))
    trpoke.files[SPENCER_TRAINER] = build_spencer_pokes()
    rom.setFileByName("a/0/9/2", trpoke.save())
    # Trainer record (a/0/9/1) is untouched: format 1, Youngster, 3 pokemon.

    # --- text edits: Spencer's name + the Quick Search reskin ---
    msg = ndspy.narc.NARC(rom.getFileByName("a/0/0/2"))
    edits = [
        (TRAINER_NAMES_FILE, SPENCER_TRAINER, SPENCER_NAME, "Masahiro"),
        (ABILITY_NAMES_FILE, MOODY, QS_NAME, "Moody"),
        (ABILITY_NAMES_UPPER_FILE, MOODY, QS_NAME.upper(), "MOODY"),
        (ABILITY_DESC_FILE, MOODY, QS_DESC, "Raises one stat and\nlowers another."),
    ]
    for fileno, index, new, expect in edits:
        newfile, oldname = rename_text_entry(msg.files[fileno], index, new,
                                             expect_old=expect)
        print(f"a/0/0/2 file {fileno} entry {index}: {oldname!r} -> {new!r}")
        msg.files[fileno] = newfile
    rom.setFileByName("a/0/0/2", msg.save())

    rom.saveToFile(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
