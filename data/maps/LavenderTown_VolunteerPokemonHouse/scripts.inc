LavenderTown_VolunteerPokemonHouse_MapScripts::
	.byte 0

LavenderTown_VolunteerPokemonHouse_EventScript_MrFuji::
	lock
	faceplayer
	goto_if_set FLAG_GOT_POKE_FLUTE, LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiHasFlute
	msgbox LavenderTown_VolunteerPokemonHouse_Text_IdLikeYouToHaveThis
	checkitemspace ITEM_POKE_FLUTE
	goto_if_eq VAR_RESULT, FALSE, LavenderTown_VolunteerPokemonHouse_EventScript_NoRoomForPokeFlute
	setflag FLAG_GOT_POKE_FLUTE
	giveitem_msg LavenderTown_VolunteerPokemonHouse_Text_ReceivedPokeFluteFromMrFuji, ITEM_POKE_FLUTE, 1, MUS_OBTAIN_KEY_ITEM
	msgbox LavenderTown_VolunteerPokemonHouse_Text_ExplainPokeFlute
	release
	end

@ Once the player has the Poke Flute and has entered the Hall of Fame, Mr. Fuji hands
@ over the OLD SEA MAP (and enables the Faraway Island ferry). Otherwise the usual line.
LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiHasFlute::
	goto_if_unset FLAG_SYS_GAME_CLEAR, LavenderTown_VolunteerPokemonHouse_EventScript_AlreadyHavePokeFlute
	goto_if_set FLAG_RECEIVED_OLD_SEA_MAP, LavenderTown_VolunteerPokemonHouse_EventScript_AlreadyHavePokeFlute
	goto LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiGiveOldSeaMap
	end

LavenderTown_VolunteerPokemonHouse_EventScript_AlreadyHavePokeFlute::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_HasPokeFluteHelpedYou
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_NoRoomForPokeFlute::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MustMakeRoomForThis
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_LittleGirl::
	lock
	faceplayer
	famechecker FAMECHECKER_MRFUJI, 0
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MrFujiLooksAfterOrphanedMons
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_LittleBoy::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MonsNiceToHug, MSGBOX_NPC
	end

LavenderTown_VolunteerPokemonHouse_EventScript_Youngster::
	lock
	faceplayer
	goto_if_set FLAG_RESCUED_MR_FUJI, LavenderTown_VolunteerPokemonHouse_EventScript_YoungsterFujiBack
	msgbox LavenderTown_VolunteerPokemonHouse_Text_WhereDidMrFujiGo
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_YoungsterFujiBack::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MrFujiWasPrayingForCubonesMother
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_Nidorino::
	lock
	faceplayer
	waitse
	playmoncry SPECIES_NIDORINO, CRY_MODE_NORMAL
	msgbox LavenderTown_VolunteerPokemonHouse_Text_Nidorino
	waitmoncry
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_Psyduck::
	lock
	faceplayer
	waitse
	playmoncry SPECIES_PSYDUCK, CRY_MODE_NORMAL
	msgbox LavenderTown_VolunteerPokemonHouse_Text_Psyduck
	waitmoncry
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_PokemonFanMagazine::
	lockall
	famechecker FAMECHECKER_MRFUJI, 2
	msgbox LavenderTown_VolunteerPokemonHouse_Text_GrandPrizeDrawingClipped
	releaseall
	end

LavenderTown_VolunteerPokemonHouse_EventScript_Bookshelf::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_PokemonMagazinesLineShelf, MSGBOX_SIGN
	end

@ ---------------------------------------------------------------------------
@ Mr. Fuji gives the OLD SEA MAP after the Hall of Fame and enables the Faraway
@ Island ferry. Reached from EventScript_MrFujiHasFlute, which has already locked
@ the player and verified Hall of Fame cleared + map not yet received.
@ ---------------------------------------------------------------------------
LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiGiveOldSeaMap::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MrFujiOfferOldSeaMap
	checkitemspace ITEM_OLD_SEA_MAP
	goto_if_eq VAR_RESULT, FALSE, LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiOldSeaMapNoRoom
	giveitem_msg LavenderTown_VolunteerPokemonHouse_Text_MrFujiReceivedOldSeaMap, ITEM_OLD_SEA_MAP, 1, MUS_OBTAIN_KEY_ITEM
	setflag FLAG_RECEIVED_OLD_SEA_MAP
	setflag FLAG_ENABLE_SHIP_FARAWAY_ISLAND
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MrFujiOldSeaMapExplain
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiOldSeaMapNoRoom::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MrFujiOldSeaMapNoRoom
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiOldSeaMapNotCleared::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MrFujiOldSeaMapNotCleared
	release
	end

LavenderTown_VolunteerPokemonHouse_EventScript_MrFujiOldSeaMapAlready::
	msgbox LavenderTown_VolunteerPokemonHouse_Text_MrFujiOldSeaMapAlready
	release
	end
