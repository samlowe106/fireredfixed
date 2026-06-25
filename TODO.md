# TODO

Outstanding work, with links to the files involved. `README.md` holds the full feature checklist; this tracks what's left and where to do it.

## Mt. Moon meteorites → Deoxys Forme change

Scripts + text are scaffolded; sprites, collision, and the actual forme change remain.

- [x] Four meteor scripts (one per Forme) — [data/maps/Route4/scripts.inc](data/maps/Route4/scripts.inc)
- [x] Four example text strings — [data/maps/Route4/text.inc](data/maps/Route4/text.inc)
- [ ] Add four meteor sprites (`object_event`s) + collision, each pointing at a meteor script — [data/maps/Route4/map.json](data/maps/Route4/map.json)
- [ ] Implement the Forme-change action (the `@ TODO` lines in the scripts). Note: vanilla FRLG has no Deoxys Forme switch, so this needs custom support — [data/maps/Route4/scripts.inc](data/maps/Route4/scripts.inc)

## Sevii Islands starter-egg NPCs

Give an egg of the Kanto starter your starter is strong-against / weak-to. WIP scripts exist but are in XSE/HexManiac format and must be rewritten as pret scripts.

- [ ] Rewrite as pret `.inc` (use the `giveegg` macro + `VAR_STARTER_MON`); template: [data/maps/FiveIsland_WaterLabyrinth/scripts.inc](data/maps/FiveIsland_WaterLabyrinth/scripts.inc)
  - strong-against — WIP: [starter_egg_strong.inc](starter_egg_strong.inc)
  - weak-to — WIP: [starter_egg_weak.inc](starter_egg_weak.inc)
- [ ] Add the two NPCs (object_events + scripts) to a Sevii Islands map (TBD)

## Celio — Aurora Ticket & Mystic Ticket

Gated on `FLAG_SYS_CAN_LINK_WITH_RS` (the Hoenn link).

- [x] Give script written: `EventScript_CelioGiveTickets` (gives both tickets, gate + bag-full handling) — [data/maps/OneIsland_PokemonCenter_1F/scripts.inc](data/maps/OneIsland_PokemonCenter_1F/scripts.inc)
- [ ] Hook it into Celio's object script (`EventScript_Celio`)
- [ ] Delete the now-superseded WIP drafts: [aurora_ticket.inc](aurora_ticket.inc), [mystic_ticket.inc](mystic_ticket.inc)

## Eevee → Umbreon / Espeon

After the National Dex, enough friendship evolves Eevee to Umbreon at even levels / Espeon at odd levels.

- [ ] Add `EVO_FRIENDSHIP_EVEN_LEVEL` / `_ODD_LEVEL` methods — [include/constants/pokemon.h](include/constants/pokemon.h)
- [ ] Update Eevee's table — [src/data/pokemon/evolution.h](src/data/pokemon/evolution.h)
- [ ] Handle the new methods (National Dex + friendship + level parity) in `GetEvolutionTargetSpecies` — [src/pokemon.c](src/pokemon.c)

## Roaming legendaries (all three regardless of starter)

Raikou, Suicune, and Entei should all roam. Today only one roamer exists, chosen by starter.

- [ ] Expand the single `struct Roamer` into an array of three and loop it through the roamer functions — [src/roamer.c](src/roamer.c)

## Faraway Island + Mew (Old Sea Map payoff) — Phase 1 done

Phase 1 (functional, reused FRLG tilesets) is implemented and builds. See the plan in
`~/.claude/plans/okay-i-d-also-like-silly-honey.md`.

- [x] `ITEM_OLD_SEA_MAP` (constant, item data + description, Emerald icon) — [src/data/items.json](src/data/items.json)
- [x] Mr. Fuji hands over the Old Sea Map after the Hall of Fame and sets `FLAG_ENABLE_SHIP_FARAWAY_ISLAND` — [data/maps/LavenderTown_VolunteerPokemonHouse/scripts.inc](data/maps/LavenderTown_VolunteerPokemonHouse/scripts.inc)
- [x] Two new maps: `FarawayIsland_Harbor` (reuses `LAYOUT_ISLAND_HARBOR`) + `FarawayIsland_Interior` (new grass layout, generated `map.bin`) — [data/maps/FarawayIsland_Interior/](data/maps/FarawayIsland_Interior/)
- [x] Vermilion ferry offers Faraway Island when you hold the Old Sea Map; seagallop + sail-back wired — [data/maps/VermilionCity/scripts.inc](data/maps/VermilionCity/scripts.inc), [src/seagallop.c](src/seagallop.c)
- [x] Faithful Mew encounter: dodges in the grass (`MOVEMENT_TYPE_COPY_PLAYER_OPPOSITE_IN_GRASS`), corner + interact → `StartLegendaryBattle` — [data/maps/FarawayIsland_Interior/scripts.inc](data/maps/FarawayIsland_Interior/scripts.inc)
- [ ] **Playtest**: sail there, confirm Mew dodges/corners/battles/catches and re-shows after a defeat (build passing ≠ plays correctly)
- [ ] **Phase 2 (optional, faithful visuals)**: the converter exists — [devtools/port_emerald_area.py](devtools/port_emerald_area.py) ports the layout + both tilesets from a pokeemerald checkout (copies tiles verbatim; re-bases secondary IDs +0x80, secondary tiles +128, secondary pals +1 slot, metatile attrs u16→u32). To run: clone pokeemerald, `python3 devtools/port_emerald_area.py --emerald ../pokeemerald --map FarawayIsland_Interior --name FarawayReal`, paste the four snippets from `port_report.md`, point `FarawayIsland_Interior/map.json` at the new `LAYOUT_…`, drop the placeholder `data/layouts/FarawayIsland_Interior/map.bin`, rebuild. (Conversion math is unit-tested; end-to-end needs the Emerald checkout.)
- [ ] **Polish**: dedicated `MAPSEC_FARAWAY_ISLAND` (currently reuses `MAPSEC_BIRTH_ISLAND`); optional Emerald-style discovery cutscene ('!' bubble + grass-emerge); remove the now-dead `MrFujiOldSeaMapNotCleared`/`Already` sub-scripts

## Verify / cleanup

- [ ] Delete the obsolete `TradeCloneMon` WIP (mirror trades use the in-game trade system) — [fixes.c](fixes.c)
- [ ] (Optional) Replicate the trade machine NPC to more Cable Clubs, and double-check its placement (currently x=12,y=4 in Saffron) — [data/maps/SaffronCity_PokemonCenter_2F/map.json](data/maps/SaffronCity_PokemonCenter_2F/map.json)
