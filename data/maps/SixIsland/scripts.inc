SixIsland_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, SixIsland_OnTransition
	.byte 0

SixIsland_OnTransition::
	setworldmapflag FLAG_WORLD_MAP_SIX_ISLAND
	end

SixIsland_EventScript_Hiker::
	msgbox SixIsland_Text_ThatWayToWaterPathRuinValley, MSGBOX_NPC
	end

SixIsland_EventScript_Boy::
	msgbox SixIsland_Text_SkyAtNightIsFantastic, MSGBOX_NPC
	end

SixIsland_EventScript_IslandSign::
	msgbox SixIsland_Text_IslandSign, MSGBOX_SIGN
	end

@ Circular Kanto-starter trade: give SQUIRTLE, receive BULBASAUR. Repeatable.
SixIsland_EventScript_StarterTrade::
	lock
	faceplayer
	setvar VAR_0x8008, INGAME_TRADE_GET_BULBASAUR
	call EventScript_GetInGameTradeSpeciesInfo
	msgbox Trade_Text_LookingForMonWannaTradeForMon, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SixIsland_EventScript_StarterTradeDecline
	call EventScript_ChooseMonForInGameTrade
	goto_if_ge VAR_0x8004, PARTY_SIZE, SixIsland_EventScript_StarterTradeDecline
	call EventScript_GetInGameTradeSpecies
	goto_if_ne VAR_RESULT, VAR_0x8009, SixIsland_EventScript_StarterTradeWrongMon
	call EventScript_DoInGameTrade
	msgbox Trade_Text_HeyThanks
	release
	end

SixIsland_EventScript_StarterTradeDecline::
	msgbox Trade_Text_AwwOhWell
	release
	end

SixIsland_EventScript_StarterTradeWrongMon::
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox Trade_Text_WhatThatsNoMon
	release
	end
