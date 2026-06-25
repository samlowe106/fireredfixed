#!/usr/bin/env python3
"""Port a map area (layout + tilesets) from pokeemerald into pokefirered.

There is no clean 1:1 metatile "dictionary" between the two games -- their tilesets
are authored independently and even the same-named gTileset_General differs. So this
copies *all* the tiles/palettes/metatiles over verbatim (as a new self-contained FireRed
tileset pair) and only remaps the indices that the engine-format differences force:

  * Metatile-id split : Emerald secondary starts at 0x200, FireRed at 0x280  -> +0x80
  * Tile-index split  : Emerald primary 512 tiles,  FireRed 640              -> secondary tiles +128
  * Palette split     : Emerald 6 primary pals,      FireRed 7               -> secondary pals +1 slot
  * Metatile attrs    : Emerald 2 bytes/metatile (u16), FireRed 4 (u32)      -> widen + move layer-type bits

What it writes (into the FireRed repo):
  - data/tilesets/primary/<base>_primary/   (tiles.png, palettes/00-15.pal, metatiles.bin, metatile_attributes.bin)
  - data/tilesets/secondary/<base>/         (same)
  - data/layouts/<Base>/                    (map.bin, border.bin)
  - port_report.md                          (capacity checks + the layouts.json / C snippets to paste)

The externs for the new tilesets are generated automatically by `mapjson` from the
tileset names you put in layouts.json, so only the three data/tilesets/*.h definitions
(printed in the report) need pasting by hand.

Usage:
    python3 devtools/port_emerald_area.py --emerald ../pokeemerald --map FarawayIsland_Interior --name FarawayReal
    python3 devtools/port_emerald_area.py --emerald ../pokeemerald --layout LAYOUT_FARAWAY_ISLAND_INTERIOR --name FarawayReal

Run from the repo root (--firered defaults to the current working directory).

Caveats (printed in the report too):
  * Metatile *behavior* values are copied as-is. The common terrain behaviors (normal,
    tall grass, water, ledges) share numbers between the games, but warps/doors/special
    behaviors diverge -- spot-check those. Use --behavior-map to remap specific values.
  * Terrain-type / encounter-type attribute fields are left 0 (Emerald packs that into
    behavior); fine for grass/indoor areas, revisit for surf-heavy maps.
"""

import argparse
import json
import os
import re
import shutil
import struct
import sys

# ---- engine constants ------------------------------------------------------
EM = dict(TILES_PRIMARY=512, METATILES_PRIMARY=512, PALS_PRIMARY=6)
FR = dict(TILES_PRIMARY=640, METATILES_PRIMARY=640, PALS_PRIMARY=7)
MAX_TILES = 1024        # 10-bit tile index field
MAX_METATILES = 1024    # 10-bit metatile id field
MAX_PALS = 16

TILE_SHIFT = FR['TILES_PRIMARY'] - EM['TILES_PRIMARY']        # +128
METATILE_SHIFT = FR['METATILES_PRIMARY'] - EM['METATILES_PRIMARY']  # +128
PAL_SHIFT = FR['PALS_PRIMARY'] - EM['PALS_PRIMARY']          # +1

warnings = []


def warn(msg):
    warnings.append(msg)
    print("  WARNING:", msg, file=sys.stderr)


# ---- camel/snake helpers ---------------------------------------------------
def tileset_name_to_dir(name):
    # gTileset_SeviiIslands123 -> sevii_islands_123 ; gTileset_General -> general
    base = name.replace('gTileset_', '')
    s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', base)
    s = re.sub(r'(?<=[A-Za-z])(?=[0-9])', '_', s)
    return s.lower()


# ---- attribute conversion (Emerald u16 -> FireRed u32) ---------------------
def convert_attributes(raw_em, num_metatiles, behavior_map):
    """Emerald: behavior bits 0-7, layer-type bits 12-13. FireRed: behavior bits
    0-8, layer-type bits 29-30 (terrain/encounter left 0)."""
    out = bytearray()
    for i in range(num_metatiles):
        a16 = struct.unpack_from('<H', raw_em, i * 2)[0]
        behavior = a16 & 0xFF
        behavior = behavior_map.get(behavior, behavior)
        layer = (a16 >> 12) & 0x3
        a32 = (behavior & 0x1FF) | (layer << 29)
        out += struct.pack('<I', a32)
    return bytes(out)


# ---- metatile conversion (per 8x u16 tile entries) -------------------------
def convert_metatiles(raw, is_secondary):
    max_tile = 0
    max_pal = 0
    out = bytearray()
    n = len(raw) // 2
    for i in range(n):
        v = struct.unpack_from('<H', raw, i * 2)[0]
        tile = v & 0x03FF
        flip = v & 0x0C00
        pal = (v >> 12) & 0x0F
        if is_secondary:
            if tile >= EM['TILES_PRIMARY']:
                tile += TILE_SHIFT
            if pal >= EM['PALS_PRIMARY']:
                pal += PAL_SHIFT
        max_tile = max(max_tile, tile)
        max_pal = max(max_pal, pal)
        out += struct.pack('<H', (pal << 12) | flip | (tile & 0x3FF))
    return bytes(out), max_tile, max_pal


# ---- blockdata conversion (map.bin / border.bin) ---------------------------
def convert_blockdata(raw):
    out = bytearray()
    n = len(raw) // 2
    max_meta = 0
    for i in range(n):
        v = struct.unpack_from('<H', raw, i * 2)[0]
        meta = v & 0x03FF
        rest = v & 0xFC00  # collision + elevation
        if meta >= EM['METATILES_PRIMARY']:
            meta += METATILE_SHIFT
        max_meta = max(max_meta, meta)
        out += struct.pack('<H', rest | (meta & 0x3FF))
    return bytes(out), max_meta


# ---- palettes --------------------------------------------------------------
BLACK_PAL = "JASC-PAL\n0100\n16\n" + "\n".join(["0 0 0"] * 16) + "\n"


def write_palettes(src_dir, dst_dir, is_secondary):
    """Copy the 16 JASC .pal files, applying the secondary +1 slot shift."""
    os.makedirs(dst_dir, exist_ok=True)

    def src_pal(slot):
        p = os.path.join(src_dir, f"{slot:02d}.pal")
        return p if os.path.exists(p) else None

    for fr_slot in range(16):
        dst = os.path.join(dst_dir, f"{fr_slot:02d}.pal")
        if not is_secondary:
            src = src_pal(fr_slot)               # primary: 1:1
        else:
            # FireRed secondary owns slots 7-15 (primary provides 0-6).
            em_slot = fr_slot - PAL_SHIFT        # FR 7 <- EM 6, ... FR 15 <- EM 14
            src = src_pal(em_slot) if fr_slot >= FR['PALS_PRIMARY'] else None
        if src:
            shutil.copyfile(src, dst)
        else:
            with open(dst, 'w') as f:
                f.write(BLACK_PAL)
    if is_secondary and src_pal(15):
        warn("Emerald secondary palette slot 15 is in use; FireRed has no room for it "
             "(secondary pals only reach slot 15 after the +1 shift). Re-pack palettes.")


def png_tile_count(path):
    try:
        with open(path, 'rb') as f:
            f.read(16)  # 8-byte sig + 4 len + 4 'IHDR'
            w = int.from_bytes(f.read(4), 'big')
            h = int.from_bytes(f.read(4), 'big')
        return (w // 8) * (h // 8)
    except Exception:
        return None


# ---- per-tileset port ------------------------------------------------------
def port_tileset(em_root, fr_root, tileset_name, kind, out_dir_name, out_tileset_name, behavior_map):
    """kind = 'primary' | 'secondary'. Returns dict for the report."""
    is_secondary = kind == 'secondary'
    src = os.path.join(em_root, 'data', 'tilesets', kind, tileset_name_to_dir(tileset_name))
    if not os.path.isdir(src):
        sys.exit(f"ERROR: Emerald tileset dir not found: {src}\n"
                 f"  (derived from {tileset_name}; pass the right --emerald path)")
    dst = os.path.join(fr_root, 'data', 'tilesets', kind, out_dir_name)
    os.makedirs(dst, exist_ok=True)

    # tiles.png (verbatim copy)
    shutil.copyfile(os.path.join(src, 'tiles.png'), os.path.join(dst, 'tiles.png'))
    tcount = png_tile_count(os.path.join(src, 'tiles.png'))
    cap_tiles = (MAX_TILES - FR['TILES_PRIMARY']) if is_secondary else FR['TILES_PRIMARY']
    if tcount and tcount > cap_tiles:
        warn(f"{out_tileset_name}: tiles.png has {tcount} tiles but FireRed {kind} holds "
             f"only {cap_tiles}. The map will not fit without trimming tiles.")

    # metatiles.bin (+ capacity)
    raw_meta = open(os.path.join(src, 'metatiles.bin'), 'rb').read()
    num_metatiles = len(raw_meta) // 16
    cap_meta = (MAX_METATILES - FR['METATILES_PRIMARY']) if is_secondary else FR['METATILES_PRIMARY']
    if num_metatiles > cap_meta:
        warn(f"{out_tileset_name}: {num_metatiles} metatiles but FireRed {kind} holds "
             f"only {cap_meta}.")
    conv_meta, max_tile, max_pal = convert_metatiles(raw_meta, is_secondary)
    open(os.path.join(dst, 'metatiles.bin'), 'wb').write(conv_meta)
    if max_tile > MAX_TILES - 1:
        warn(f"{out_tileset_name}: a metatile references tile {max_tile} (>{MAX_TILES-1}) "
             f"after the +{TILE_SHIFT} shift -- overflow.")
    if max_pal > MAX_PALS - 1:
        warn(f"{out_tileset_name}: a metatile references palette slot {max_pal} (>15) "
             f"after the +{PAL_SHIFT} shift -- overflow.")

    # metatile_attributes.bin (2 -> 4 bytes)
    raw_attr = open(os.path.join(src, 'metatile_attributes.bin'), 'rb').read()
    if len(raw_attr) // 2 != num_metatiles:
        warn(f"{out_tileset_name}: attribute count ({len(raw_attr)//2}) != metatile count "
             f"({num_metatiles}); Emerald attrs assumed 2 bytes each.")
    conv_attr = convert_attributes(raw_attr, num_metatiles, behavior_map)
    open(os.path.join(dst, 'metatile_attributes.bin'), 'wb').write(conv_attr)

    # palettes
    write_palettes(os.path.join(src, 'palettes'), os.path.join(dst, 'palettes'), is_secondary)

    return dict(name=out_tileset_name, dir=f"data/tilesets/{kind}/{out_dir_name}",
                is_secondary=is_secondary, num_metatiles=num_metatiles, tiles=tcount)


# ---- report ----------------------------------------------------------------
def c_snippets(prim, sec, layout):
    def header(t):
        return (f"const struct Tileset {t['name']} =\n{{\n"
                f"    .isCompressed = TRUE,\n"
                f"    .isSecondary = {'TRUE' if t['is_secondary'] else 'FALSE'},\n"
                f"    .tiles = gTilesetTiles_{t['name'].replace('gTileset_','')},\n"
                f"    .palettes = gTilesetPalettes_{t['name'].replace('gTileset_','')},\n"
                f"    .metatiles = gMetatiles_{t['name'].replace('gTileset_','')},\n"
                f"    .metatileAttributes = gMetatileAttributes_{t['name'].replace('gTileset_','')},\n"
                f"    .callback = NULL,\n}};\n")

    def graphics(t):
        b = t['name'].replace('gTileset_', '')
        pals = "\n".join(
            f'\tINCBIN_U16("{t["dir"]}/palettes/{i:02d}.gbapal"),' for i in range(16))
        return (f'const u32 gTilesetTiles_{b}[] = INCBIN_U32("{t["dir"]}/tiles.4bpp.lz");\n\n'
                f'const u16 gTilesetPalettes_{b}[][16] =\n{{\n{pals}\n}};\n')

    def metatiles(t):
        b = t['name'].replace('gTileset_', '')
        return (f'const u16 gMetatiles_{b}[] = INCBIN_U16("{t["dir"]}/metatiles.bin");\n'
                f'const u32 gMetatileAttributes_{b}[] = INCBIN_U32("{t["dir"]}/metatile_attributes.bin");\n')

    return (
        "## 1. Append to `src/data/tilesets/metatiles.h`\n```c\n"
        + metatiles(prim) + metatiles(sec) + "```\n\n"
        "## 2. Append to `src/data/tilesets/graphics.h`\n```c\n"
        + graphics(prim) + "\n" + graphics(sec) + "```\n\n"
        "## 3. Append to `src/data/tilesets/headers.h`\n```c\n"
        + header(prim) + "\n" + header(sec) + "```\n\n"
        "## 4. Add to `data/layouts/layouts.json`\n```json\n"
        + json.dumps(layout, indent=2) + "\n```\n"
    )


def main():
    ap = argparse.ArgumentParser(description="Port an Emerald map area into FireRed.")
    ap.add_argument('--emerald', required=True, help="path to a pokeemerald checkout")
    ap.add_argument('--firered', default='.', help="path to the pokefirered repo (default: cwd)")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--map', help="Emerald map name, e.g. FarawayIsland_Interior")
    g.add_argument('--layout', help="Emerald LAYOUT_ id (if you know it directly)")
    ap.add_argument('--name', required=True, help="base name for the FireRed copies, e.g. FarawayReal")
    ap.add_argument('--behavior-map', default=None,
                    help="optional JSON dict of Emerald->FireRed metatile-behavior remaps, "
                         'e.g. \'{"101":2}\'')
    args = ap.parse_args()

    behavior_map = {}
    if args.behavior_map:
        behavior_map = {int(k): int(v) for k, v in json.loads(args.behavior_map).items()}

    layouts = json.load(open(os.path.join(args.emerald, 'data', 'layouts', 'layouts.json')))['layouts']
    layout_id = args.layout
    if args.map:
        mj = json.load(open(os.path.join(args.emerald, 'data', 'maps', args.map, 'map.json')))
        layout_id = mj['layout']
    L = next((x for x in layouts if x['id'] == layout_id), None)
    if not L:
        sys.exit(f"ERROR: layout {layout_id} not found in Emerald layouts.json")
    print(f"Porting layout {L['id']} ({L['width']}x{L['height']}) "
          f"[{L['primary_tileset']} + {L['secondary_tileset']}]")

    base = args.name
    snake = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', '_', base).lower()
    prim_name = f"gTileset_{base}Primary"
    sec_name = f"gTileset_{base}"

    prim = port_tileset(args.emerald, args.firered, L['primary_tileset'], 'primary',
                        f"{snake}_primary", prim_name, behavior_map)
    sec = port_tileset(args.emerald, args.firered, L['secondary_tileset'], 'secondary',
                       snake, sec_name, behavior_map)

    # ---- layout (blockdata) ----
    em_layout_dir = os.path.dirname(os.path.join(args.emerald, L['blockdata_filepath']))
    raw_map = open(os.path.join(args.emerald, L['blockdata_filepath']), 'rb').read()
    raw_border = open(os.path.join(args.emerald, L['border_filepath']), 'rb').read()
    conv_map, max_meta = convert_blockdata(raw_map)
    conv_border, _ = convert_blockdata(raw_border)
    if max_meta > MAX_METATILES - 1:
        warn(f"blockdata references metatile {max_meta} (>{MAX_METATILES-1}) after the "
             f"+{METATILE_SHIFT} shift -- overflow.")
    out_layout_dir = os.path.join(args.firered, 'data', 'layouts', base)
    os.makedirs(out_layout_dir, exist_ok=True)
    open(os.path.join(out_layout_dir, 'map.bin'), 'wb').write(conv_map)
    open(os.path.join(out_layout_dir, 'border.bin'), 'wb').write(conv_border)

    layout_entry = {
        "id": f"LAYOUT_{snake.upper()}",
        "name": f"{base}_Layout",
        "width": L['width'], "height": L['height'],
        "border_width": L.get('border_width', 2), "border_height": L.get('border_height', 2),
        "primary_tileset": prim_name, "secondary_tileset": sec_name,
        "border_filepath": f"data/layouts/{base}/border.bin",
        "blockdata_filepath": f"data/layouts/{base}/map.bin",
    }

    # ---- report ----
    report = [f"# Emerald -> FireRed port: {L['id']} as {base}\n",
              f"Primary  : {prim['name']}  ({prim['num_metatiles']} metatiles, {prim['tiles']} tiles)",
              f"Secondary: {sec['name']}  ({sec['num_metatiles']} metatiles, {sec['tiles']} tiles)",
              f"Layout   : LAYOUT_{snake.upper()}  ({L['width']}x{L['height']})\n"]
    if warnings:
        report.append("## ⚠ Warnings\n" + "\n".join(f"- {w}" for w in warnings) + "\n")
    else:
        report.append("No capacity/overflow warnings — the area fits FireRed's tileset budget.\n")
    report.append("## Wiring\n"
                  "1. Paste the four snippets below.\n"
                  "2. Point a map's `map.json` `\"layout\"` at the new `LAYOUT_…`.\n"
                  "3. `mapjson` auto-generates the tileset externs from the names in layouts.json.\n"
                  "4. Build; check the area renders (palettes/behaviors are the usual suspects).\n\n"
                  "Behavior values were copied as-is (common terrain matches; spot-check warps/doors — "
                  "use --behavior-map to remap). Terrain/encounter attribute fields left 0.\n")
    report.append(c_snippets(prim, sec, layout_entry))
    open(os.path.join(args.firered, 'port_report.md'), 'w').write("\n".join(report))

    print("\nWrote:")
    print(f"  {prim['dir']}/")
    print(f"  {sec['dir']}/")
    print(f"  data/layouts/{base}/")
    print(f"  port_report.md  (paste the 4 snippets, then wire a map to LAYOUT_{snake.upper()})")
    print(f"\n{len(warnings)} warning(s)." if warnings else "\nNo warnings.")


if __name__ == '__main__':
    main()
