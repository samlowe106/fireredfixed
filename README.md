# FireRed Fixed

This is a minimal ROM hack of Pokemon FireRed and LeafGreen that allows completing the Regional Dex and most of the National Dex without external tools or trades, plus a handful of fixes. Based on the decompilation at [pret/pokefirered](https://github.com/pret/pokefirered).

## Regional Dex Changes

- [x] All encounter tables have been merged and renormalized so version exclusive Pokemon can be found anywhere they could be found in either FireRed or LeafGreen. These version-exclusive Pokemon maintain their original encounter rates (at the cost of slightly reducing the encounter rates of Pokemon common to both games)
- [x] Mirror trades for Alakazam, Golem, Machamp, and Gengar have been added (you trade the same species back, so it evolves):
  - [x] Trade data defined: Kadabra (Timid), Machoke (Adamant), Graveler (Impish), Haunter (Timid)
  - [x] A trade-machine NPC in the Saffron City Cable Club (Pokémon Center 2F) offers all four via a menu
- [x] The Celadon Prize Corner now has Pokemon from both games, all of which are cheaper:
  - [x] Abra (Lv.5)
  - [x] Clefairy (Lv.10)
  - [x] Dratini (Lv.15)
  - [x] Pinsir (Lv.20)
  - [x] Scyther (Lv.25)
  - [x] Porygon (Lv.30)
- [x] Khangaskhan, Chansey, Tauros, Scyther, and Pinsir will now only appear in their individually assigned Areas in the Safari Zone, but are more common there

## Quality of Life Changes

- [x] All TMs are now reusable
- [x] The player can now run indoors
- [x] The Safari Zone mechanics for Rock and Bait have been rebalanced to work closer to what was probably intended:
  - [x] Rock increases the catch rate so Pokemon require fewer Safari Balls on average, but increases the risk of them fleeing
  - [x] Bait decreases the catch rate so Pokemon require more Safari Balls on average, but decreases the risk of them fleeing
- [ ] The FireRed/LeafGreen intro video will be random every time with equal probability
- [x] A spelling error has been fixed in the Teachy TV

## Post-Game Changes

- [ ] The Old Sea Map can now be obtained from Mr. Fuji after entering the Hall of Fame
- [ ] After unlocking the National Dex, Eevees who reach enough friendship will be able to evolve into Umbreon at even levels or Espeon at odd levels
- [ ] Raikou, Suicune, and Entei will all roam regardless of which starter Pokemon you chose
- [x] Fixed Raikou and Entei permanently disappearing after they used Roar while roaming:
  - [x] Spark and Roar have been swapped in Raikou's level up learnset, so it won't know it when it's encountered
  - [x] Stomp and Roar have been swapped in Entei's level up learnset, so it won't know it when it's encountered
  - [x] Suicune never learned Roar anyways, so no changes to Suicune
- [ ] An NPC has been added to the Sevii Islands who will give you an egg for the Kanto starter Pokemon that your starter is strong against
- [ ] An NPC has been added to the Sevii Islands who will give you an egg for the Kanto starter Pokemon that your starter is weak to
- [ ] Celio will give out the Aurora Ticket and Mystic Ticket after establishing the trading link with Hoenn
- [ ] Meteorites have been added to Route 4 outside the entrance to Mt. Moon that allow Deoxys to change formes

# Installation

To set up the repository, see [INSTALL.md](INSTALL.md).
