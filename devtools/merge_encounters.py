#!/usr/bin/env python3
"""
Convert paired (version-exclusive) wild encounter tables for any pret Gen-3 decomp
into the per-species-weight format, merging FireRed/LeafGreen (or Ruby/Sapphire).

This repo uses a weighted encounter engine: each wild mon carries an explicit
`rate` (relative weight), and a mon's chance is its weight / the sum of the list's
weights. There are no fixed 12/5/10 slots, so a merged table can hold any number of
species and exact rates -- nothing overflows and nothing has to be dropped.

Two merge modes (choose with --math):

  preserve  Version-exclusives keep their original rate; species common to both
            versions shrink slightly to make room. Matches the README.

  average   Combine + renormalize: a species' merged weight is the sum of its two
            versions' weights (i.e. the average of the two distributions). Fully
            symmetric -- no favoritism between two version-exclusives -- but it
            halves the rate of a version-exclusive.

Every table is emitted in the weighted format. Tables that don't differ between
versions (and single-version / skipped tables like the Safari Zone) are converted
1:1, each mon keeping its original slot weight, so their behaviour is unchanged.

Fishing is emitted as three per-rod lists (old_rod / good_rod / super_rod).

Usage:
    python3 devtools/merge_encounters.py              # firered, preserve, apply
    python3 devtools/merge_encounters.py --math average
    python3 devtools/merge_encounters.py --dry-run    # report only
    python3 devtools/merge_encounters.py --profile rubysapphire

Run from the repo root (paths like src/data/wild_encounters.json are resolved against the
current working directory, not this script's location).
"""

import argparse
import copy
import json
import os

SPRITE_DIR = "graphics/pokemon"
SPRITE_OVERRIDES = {"SPECIES_UNOWN": "unown/a"}

PROFILES = {
    "firered":      {"path": "src/data/wild_encounters.json", "versions": ("FireRed", "LeafGreen"), "skip_prefixes": ("sSafariZone",)},
    "rubysapphire": {"path": "src/data/wild_encounters.json", "versions": ("Ruby", "Sapphire"),     "skip_prefixes": ("SafariZone",)},
    "emerald":      {"path": "src/data/wild_encounters.json", "versions": ("Ruby", "Sapphire"),     "skip_prefixes": ()},
}

REPORT_PATH = "merge_report.md"
FIELD_TYPES = ("land_mons", "water_mons", "rock_smash_mons", "fishing_mons")


def strip_suffix(label, suffixes):
    for s in suffixes:
        if label.endswith(s):
            return label[: -len(s)]
    return label


def label_version(label, suffixes):
    for s in suffixes:
        if label.endswith(s):
            return s
    return None


def build_field_groups(field_def):
    """Return (slot_count, [(group_name, [positions], [weights]), ...])."""
    rates = field_def["encounter_rates"]
    n = len(rates)
    if "groups" in field_def:
        return n, [(g, list(idxs), [rates[i] for i in idxs]) for g, idxs in field_def["groups"].items()]
    return n, [("all", list(range(n)), list(rates))]


def species_distribution(mons, positions, weights):
    """species -> total slot weight, and species -> list of (min, max) levels."""
    dist, levels = {}, {}
    for local_i, pos in enumerate(positions):
        m = mons[pos]
        sp = m["species"]
        dist[sp] = dist.get(sp, 0) + weights[local_i]
        levels.setdefault(sp, []).append((m["min_level"], m["max_level"]))
    return dist, levels


def level_union(species, fr_levels, lg_levels):
    entries = fr_levels.get(species, []) + lg_levels.get(species, [])
    return min(e[0] for e in entries), max(e[1] for e in entries)


def merge_group(fr_mons, lg_mons, positions, weights, math):
    """Merge one group (a whole land/water/rock field, or one fishing rod).
    Returns (list of weighted mon dicts, report rates {species: (fr%, lg%, merged%)})."""
    fr_d, fr_lv = species_distribution(fr_mons, positions, weights)
    lg_d, lg_lv = species_distribution(lg_mons, positions, weights)
    total = sum(weights)

    shared = set(fr_d) & set(lg_d)
    fr_only = set(fr_d) - set(lg_d)
    lg_only = set(lg_d) - set(fr_d)

    weight = {}
    if math == "average":
        # Combine + renormalize: merged weight = sum of the two versions' weights
        # (an exact integer; the group total becomes 2x, which the engine normalizes).
        for s in set(fr_d) | set(lg_d):
            weight[s] = float(fr_d.get(s, 0) + lg_d.get(s, 0))
    else:  # preserve
        for s in fr_only:
            weight[s] = float(fr_d[s])
        for s in lg_only:
            weight[s] = float(lg_d[s])
        shared_base = {s: (fr_d[s] + lg_d[s]) / 2.0 for s in shared}
        shared_total = sum(shared_base.values())
        excl_mass = sum(fr_d[s] for s in fr_only) + sum(lg_d[s] for s in lg_only)
        room = total - excl_mass
        if room > 0:
            scale = (room / shared_total) if shared_total > 0 else 0.0
            for s in shared:
                weight[s] = shared_base[s] * scale
        else:
            # Exclusives overflow: keep shared at baseline, scale exclusives to fit.
            for s in shared:
                weight[s] = shared_base[s]
            excl_room = max(0.0, total - shared_total)
            sc = (excl_room / excl_mass) if excl_mass > 0 else 0.0
            for s in (fr_only | lg_only):
                weight[s] *= sc

    # Round to integer weights (a present species never rounds away to 0).
    iweight = {}
    for s, w in weight.items():
        iw = int(round(w))
        if iw < 1 and w > 0:
            iw = 1
        if iw > 0:
            iweight[s] = iw

    mons = []
    for s in sorted(iweight, key=lambda s: (-iweight[s], s)):
        lo, hi = level_union(s, fr_lv, lg_lv)
        mons.append({"min_level": lo, "max_level": hi, "species": s, "rate": iweight[s]})

    mtot = sum(iweight.values()) or 1
    rates = {}
    for s in sorted(set(fr_d) | set(lg_d) | set(iweight)):
        rates[s] = (100.0 * fr_d.get(s, 0) / total,
                    100.0 * lg_d.get(s, 0) / total,
                    100.0 * iweight.get(s, 0) / mtot)
    return mons, rates


def convert_group(mons, positions, weights):
    """1:1 conversion of one group: each original slot becomes a weighted entry."""
    out = []
    for local_i, pos in enumerate(positions):
        m = mons[pos]
        out.append({"min_level": m["min_level"], "max_level": m["max_level"],
                    "species": m["species"], "rate": weights[local_i]})
    return out


def assemble_field(ftype, encounter_rate, by_group):
    if ftype == "fishing_mons":
        return {"encounter_rate": encounter_rate,
                "old_rod": by_group["old_rod"],
                "good_rod": by_group["good_rod"],
                "super_rod": by_group["super_rod"]}
    return {"encounter_rate": encounter_rate, "mons": by_group["all"]}


def merge_field(ftype, a_field, b_field, groups, math):
    """Merge a whole field across versions. Returns (new_field, [(group, total, rates, [])])."""
    results, report = {}, []
    for gname, positions, wts in groups:
        # In the source schema every field (including fishing) stores a flat "mons"
        # list; fishing's per-rod positions index into it via the group definition.
        mons, rates = merge_group(a_field["mons"], b_field["mons"], positions, wts, math)
        results[gname] = mons
        report.append((gname, sum(wts), rates, []))
    return assemble_field(ftype, a_field.get("encounter_rate", 0), results), report


def convert_field(ftype, field, groups):
    results = {gname: convert_group(field["mons"], positions, wts) for gname, positions, wts in groups}
    return assemble_field(ftype, field.get("encounter_rate", 0), results)


def convert_data(data, suffixes, skip_prefixes, math, apply_changes):
    report_sections = []
    for group in data.get("wild_encounter_groups", []):
        if "encounters" not in group or "fields" not in group:
            continue
        field_groups = {fd["type"]: build_field_groups(fd) for fd in group["fields"]}

        by_base = {}
        for enc in group["encounters"]:
            by_base.setdefault(strip_suffix(enc["base_label"], suffixes), {})[
                label_version(enc["base_label"], suffixes)] = enc

        for base, paired in sorted(by_base.items()):
            a = paired.get(suffixes[0])
            b = paired.get(suffixes[1])
            entries = [e for e in (a, b) if e is not None]
            is_skip = any(e["base_label"].startswith(p) for p in skip_prefixes for e in entries)

            route_report = []
            for ftype in FIELD_TYPES:
                if ftype not in field_groups:
                    continue
                _, groups = field_groups[ftype]
                a_has = a is not None and ftype in a
                b_has = b is not None and ftype in b

                mergeable = (a_has and b_has and not is_skip
                             and a[ftype]["mons"] != b[ftype]["mons"])
                if mergeable:
                    new_field, freport = merge_field(ftype, a[ftype], b[ftype], groups, math)
                    if apply_changes:
                        a[ftype] = copy.deepcopy(new_field)
                        b[ftype] = copy.deepcopy(new_field)
                    route_report.append((ftype, freport))
                else:
                    for e in entries:
                        if ftype in e and apply_changes:
                            e[ftype] = convert_field(ftype, e[ftype], groups)
            if route_report:
                report_sections.append((base, route_report))

    return len(report_sections), report_sections


# ---------------------------------------------------------------------------
# Report (collapsible, centered, party-icon thumbnails)
# ---------------------------------------------------------------------------

def short(species):
    return species.replace("SPECIES_", "").title().replace("_", "-")


def sprite_cell(species, report_dir_abs, sprite_dir):
    name = short(species)
    folder = SPRITE_OVERRIDES.get(species, species.replace("SPECIES_", "").lower())
    path = os.path.join(sprite_dir, folder, "icon.png")
    if not os.path.exists(path):
        return name
    rel = os.path.relpath(os.path.abspath(path), report_dir_abs)
    style = "object-fit:none;object-position:0 0;image-rendering:pixelated;vertical-align:middle"
    return f'<img src="{rel}" alt="" width="32" height="32" style="{style}"> {name}'


def write_report(path, report_sections, va_label, vb_label, math, sprites=True, sprite_dir=SPRITE_DIR):
    report_dir = os.path.dirname(os.path.abspath(path))

    def cell(species):
        return short(species) if not sprites else sprite_cell(species, report_dir, sprite_dir)

    def field_block(label, rows):
        out = [f'<p align="center"><b>{label}</b></p>', '<table align="center">']
        out.append(f'<tr><th align="left">Pokemon</th><th align="right">{va_label}</th>'
                   f'<th align="right">{vb_label}</th><th align="right">Merged</th></tr>')
        for c, a, b, m in rows:
            out.append(f'<tr><td align="left">{c}</td><td align="right">{a:.1f}%</td>'
                       f'<td align="right">{b:.1f}%</td><td align="right">{m:.1f}%</td></tr>')
        out.append('</table>')
        return out

    sections = []
    for base, route_report in report_sections:
        name = base[1:] if base[:1].islower() else base
        blocks = []
        for ftype, freport in route_report:
            for gname, total, rates, _dropped in freport:
                rows = []
                for s in sorted(rates, key=lambda s: -rates[s][2]):
                    a, b, m = rates[s]
                    if abs(a - m) < 0.05 and abs(b - m) < 0.05 and abs(a - b) < 0.05:
                        continue
                    rows.append((cell(s), a, b, m))
                if not rows:
                    continue
                label = ftype.replace("_mons", "") + (f" / {gname}" if gname != "all" else "")
                blocks.extend(field_block(label, rows))
        if blocks:
            sections.append((name, blocks))

    mode = "preserve exclusives" if math == "preserve" else "combine + renormalize"
    lines = [f"# Encounter merge: {va_label} / {vb_label} rate differences", ""]
    lines.append(f"_{len(sections)} areas with rate changes ({mode}). Columns are % chance within that field/rod._")
    lines.append("_Each area is collapsible — click a name to expand it._")
    lines.append("")
    for name, blocks in sections:
        lines.append("<details>")
        lines.append(f'<summary><h2 style="display:inline-block;margin:0;vertical-align:middle">{name}</h2></summary>')
        lines.append("")
        lines.extend(blocks)
        lines.append("")
        lines.append("</details>")
        lines.append("")

    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser(description="Weighted wild-encounter merge/converter for pret Gen-3 decomps.")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="firered")
    ap.add_argument("--math", choices=("preserve", "average"), default="preserve",
                    help="preserve: exclusives keep full rate; average: combine + renormalize")
    ap.add_argument("--path", help="override path to wild_encounters.json")
    ap.add_argument("--versions", nargs=2, metavar=("A", "B"))
    ap.add_argument("--skip-prefix", action="append", default=[], dest="skip_prefixes")
    ap.add_argument("--report", default=REPORT_PATH)
    ap.add_argument("--no-sprites", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="report only; do not modify JSON")
    args = ap.parse_args()

    profile = PROFILES[args.profile]
    json_path = args.path or profile["path"]
    versions = tuple(args.versions) if args.versions else profile["versions"]
    suffixes = tuple("_" + v for v in versions)
    skip_prefixes = tuple(args.skip_prefixes) or tuple(profile["skip_prefixes"])
    va_label, vb_label = versions

    with open(json_path) as f:
        data = json.load(f)

    changed, report_sections = convert_data(
        data, suffixes, skip_prefixes, args.math, apply_changes=not args.dry_run)
    write_report(args.report, report_sections, va_label, vb_label, args.math,
                 sprites=not args.no_sprites, sprite_dir=profile.get("sprite_dir", SPRITE_DIR))

    if not args.dry_run:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    print(f"Profile: {args.profile}  ({va_label} / {vb_label})  math={args.math}")
    print(f"Areas with rate changes: {changed}")
    print(f"Report written to {args.report}")
    if args.dry_run:
        print("(dry run: JSON not modified)")


if __name__ == "__main__":
    main()
