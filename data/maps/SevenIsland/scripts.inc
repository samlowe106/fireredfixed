SevenIsland_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SevenIsland_OnTransition
	.byte 0

SevenIsland_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SEVEN_ISLAND
	end

SevenIsland_EventScript_IslandSign::
	msgbox SevenIsland_Text_IslandSign, MSGBOX_SIGN
	end

SevenIsland_EventScript_OldWoman::
	msgbox SevenIsland_Text_IslandsMadeInSevenDays, MSGBOX_NPC
	end

SevenIsland_EventScript_Scientist::
	msgbox SevenIsland_Text_IslandVirtuallyUntouched, MSGBOX_NPC
	end

@ Fossil swaps: trade either revived fossil mon for the other. Repeatable.
SevenIsland_EventScript_FossilTradeKabuto::
	lock
	faceplayer
	setvar VAR_0x8008, INGAME_TRADE_GET_KABUTO
	goto SevenIsland_EventScript_FossilTradeRun
	end

SevenIsland_EventScript_FossilTradeOmanyte::
	lock
	faceplayer
	setvar VAR_0x8008, INGAME_TRADE_GET_OMANYTE
	goto SevenIsland_EventScript_FossilTradeRun
	end

SevenIsland_EventScript_FossilTradeRun::
	call EventScript_GetInGameTradeSpeciesInfo
	msgbox Trade_Text_LookingForMonWannaTradeForMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SevenIsland_EventScript_FossilTradeDecline
	call EventScript_ChooseMonForInGameTrade
	goto_if_ge VAR_0x8004, PARTY_SIZE, SevenIsland_EventScript_FossilTradeDecline
	call EventScript_GetInGameTradeSpecies
	goto_if_ne VAR_RESULT, VAR_0x8009, SevenIsland_EventScript_FossilTradeWrongMon
	call EventScript_DoInGameTrade
	msgbox Trade_Text_HeyThanks
	release
	end

SevenIsland_EventScript_FossilTradeDecline::
	msgbox Trade_Text_AwwOhWell
	release
	end

SevenIsland_EventScript_FossilTradeWrongMon::
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox Trade_Text_WhatThatsNoMon
	release
	end
