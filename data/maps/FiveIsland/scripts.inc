FiveIsland_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FiveIsland_OnTransition
	.byte 0

FiveIsland_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_FIVE_ISLAND
	end

FiveIsland_EventScript_IslandSign::
	msgbox FiveIsland_Text_IslandSign, MSGBOX_SIGN
	end

FiveIsland_EventScript_BugCatcher::
	msgbox FiveIsland_Text_WeirdBuildingInMeadow, MSGBOX_NPC
	end

FiveIsland_EventScript_Fisher::
	msgbox FiveIsland_Text_BeenGettingBusierAroundHere, MSGBOX_NPC
	end

@ Circular Kanto-starter trade: give CHARMANDER, receive SQUIRTLE. Repeatable.
FiveIsland_EventScript_StarterTrade::
	lock
	faceplayer
	setvar VAR_0x8008, INGAME_TRADE_GET_SQUIRTLE
	call EventScript_GetInGameTradeSpeciesInfo
	msgbox Trade_Text_LookingForMonWannaTradeForMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, FiveIsland_EventScript_StarterTradeDecline
	call EventScript_ChooseMonForInGameTrade
	goto_if_ge VAR_0x8004, PARTY_SIZE, FiveIsland_EventScript_StarterTradeDecline
	call EventScript_GetInGameTradeSpecies
	goto_if_ne VAR_RESULT, VAR_0x8009, FiveIsland_EventScript_StarterTradeWrongMon
	call EventScript_DoInGameTrade
	msgbox Trade_Text_HeyThanks
	release
	end

FiveIsland_EventScript_StarterTradeDecline::
	msgbox Trade_Text_AwwOhWell
	release
	end

FiveIsland_EventScript_StarterTradeWrongMon::
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox Trade_Text_WhatThatsNoMon
	release
	end
