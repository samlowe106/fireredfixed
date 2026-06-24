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

## Mr. Fuji — Old Sea Map (after the Hall of Fame)

- [x] Added `ITEM_OLD_SEA_MAP` (constant, item data + description, Emerald icon) — [src/data/items.json](src/data/items.json)
- [x] Give script written: `EventScript_MrFujiOldSeaMap` (gated on `FLAG_SYS_GAME_CLEAR`) — [data/maps/LavenderTown_VolunteerPokemonHouse/scripts.inc](data/maps/LavenderTown_VolunteerPokemonHouse/scripts.inc)
- [ ] Hook it into Mr. Fuji's object script (`EventScript_MrFuji`, which currently only gives the Poké Flute)

## Verify / cleanup

- [ ] Delete the obsolete `TradeCloneMon` WIP (mirror trades use the in-game trade system) — [fixes.c](fixes.c)
- [ ] (Optional) Replicate the trade machine NPC to more Cable Clubs, and double-check its placement (currently x=12,y=4 in Saffron) — [data/maps/SaffronCity_PokemonCenter_2F/map.json](data/maps/SaffronCity_PokemonCenter_2F/map.json)
