SaffronCity_PokemonCenter_2F_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, CableClub_OnFrame
	map_script MAP_SCRIPT_ON_WARP_INTO_MAP_TABLE, CableClub_OnWarp
	map_script MAP_SCRIPT_ON_LOAD, CableClub_OnLoad
	map_script MAP_SCRIPT_ON_TRANSITION, CableClub_OnTransition
	.byte 0

@ The below 3 are unused and leftover from RS
SaffronCity_PokemonCenter_2F_EventScript_Colosseum::
	call CableClub_EventScript_Colosseum
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeCenter::
	call CableClub_EventScript_TradeCenter
	end

SaffronCity_PokemonCenter_2F_EventScript_RecordCorner::
	call CableClub_EventScript_RecordCorner
	end

@ Trade machine: simulates a link trade against the predefined mirror trades, so a
@ trade-evolution Pokemon (Kadabra/Machoke/Graveler/Haunter) evolves on the spot.
SaffronCity_PokemonCenter_2F_EventScript_TradeMachine::
	lock
	faceplayer
	msgbox SaffronCity_PokemonCenter_2F_Text_TradeMachineIntro, MSGBOX_DEFAULT
SaffronCity_PokemonCenter_2F_EventScript_TradeMachineMenu::
	message SaffronCity_PokemonCenter_2F_Text_TradeMachineWhich
	waitmessage
	multichoice 16, 0, MULTICHOICE_TRADE_STATION, FALSE
	switch VAR_RESULT
	case 0, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineKadabra
	case 1, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineMachoke
	case 2, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineGraveler
	case 3, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineHaunter
	case 4, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineExit
	case 127, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineExit
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeMachineKadabra::
	setvar VAR_0x8008, INGAME_TRADE_KADABRA
	goto SaffronCity_PokemonCenter_2F_EventScript_TradeMachineRun
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeMachineMachoke::
	setvar VAR_0x8008, INGAME_TRADE_MACHOKE
	goto SaffronCity_PokemonCenter_2F_EventScript_TradeMachineRun
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeMachineGraveler::
	setvar VAR_0x8008, INGAME_TRADE_GRAVELER
	goto SaffronCity_PokemonCenter_2F_EventScript_TradeMachineRun
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeMachineHaunter::
	setvar VAR_0x8008, INGAME_TRADE_HAUNTER
	goto SaffronCity_PokemonCenter_2F_EventScript_TradeMachineRun
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeMachineRun::
	call EventScript_GetInGameTradeSpeciesInfo
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox SaffronCity_PokemonCenter_2F_Text_TradeMachineConfirm, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineMenu
	call EventScript_ChooseMonForInGameTrade
	goto_if_ge VAR_0x8004, PARTY_SIZE, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineMenu
	call EventScript_GetInGameTradeSpecies
	goto_if_ne VAR_RESULT, VAR_0x8009, SaffronCity_PokemonCenter_2F_EventScript_TradeMachineWrongMon
	call EventScript_DoInGameTrade
	goto SaffronCity_PokemonCenter_2F_EventScript_TradeMachineMenu
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeMachineWrongMon::
	bufferspeciesname STR_VAR_1, VAR_0x8009
	msgbox SaffronCity_PokemonCenter_2F_Text_TradeMachineWrongMon, MSGBOX_DEFAULT
	goto SaffronCity_PokemonCenter_2F_EventScript_TradeMachineMenu
	end

SaffronCity_PokemonCenter_2F_EventScript_TradeMachineExit::
	release
	end

SaffronCity_PokemonCenter_2F_Text_TradeMachineIntro::
	.string "Welcome to the TRADE MACHINE!\p"
	.string "I can carry out a trade for you, just\n"
	.string "as if a faraway friend were trading\l"
	.string "the same POKéMON right back to you.\p"
	.string "A trade-evolution POKéMON will evolve\n"
	.string "the instant the trade completes!$"

SaffronCity_PokemonCenter_2F_Text_TradeMachineWhich::
	.string "Which trade would you like to make?$"

SaffronCity_PokemonCenter_2F_Text_TradeMachineConfirm::
	.string "This trade needs a {STR_VAR_1}.\n"
	.string "Shall we begin?$"

SaffronCity_PokemonCenter_2F_Text_TradeMachineWrongMon::
	.string "That POKéMON isn't a {STR_VAR_1}.\p"
	.string "I can only trade a {STR_VAR_1} for\n"
	.string "another {STR_VAR_1}.$"
