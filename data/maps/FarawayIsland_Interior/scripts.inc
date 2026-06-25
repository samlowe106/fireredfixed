FarawayIsland_Interior_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, FarawayIsland_Interior_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, FarawayIsland_Interior_OnResume
	.byte 0

FarawayIsland_Interior_OnTransition::
	call_if_set FLAG_CAUGHT_MEW, FarawayIsland_Interior_EventScript_HideMew
	call_if_unset FLAG_CAUGHT_MEW, FarawayIsland_Interior_EventScript_ShowMew
	end

FarawayIsland_Interior_EventScript_HideMew::
	setflag FLAG_HIDE_MEW
	return

FarawayIsland_Interior_EventScript_ShowMew::
	clearflag FLAG_HIDE_MEW
	return

@ After the special battle, remove Mew from the field only if it was caught.
FarawayIsland_Interior_OnResume::
	call_if_set FLAG_SYS_SPECIAL_WILD_BATTLE, FarawayIsland_Interior_EventScript_TryRemoveMew
	end

FarawayIsland_Interior_EventScript_TryRemoveMew::
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_ne VAR_RESULT, B_OUTCOME_CAUGHT, EventScript_Return
	removeobject LOCALID_FARAWAY_ISLAND_MEW
	return

@ Mew dodges through the grass (MOVEMENT_TYPE_COPY_PLAYER_OPPOSITE_IN_GRASS); the player
@ must corner it against a wall to interact. Interacting starts the legendary battle.
FarawayIsland_Interior_EventScript_Mew::
	lock
	faceplayer
	goto_if_questlog EventScript_ReleaseEnd
	special QuestLog_CutRecording
	waitse
	playmoncry SPECIES_MEW, CRY_MODE_ENCOUNTER
	delay 40
	waitmoncry
	setvar VAR_LAST_TALKED, LOCALID_FARAWAY_ISLAND_MEW
	seteventmon SPECIES_MEW, 30
	setflag FLAG_SYS_SPECIAL_WILD_BATTLE
	special StartLegendaryBattle
	waitstate
	clearflag FLAG_SYS_SPECIAL_WILD_BATTLE
	specialvar VAR_RESULT, GetBattleOutcome
	goto_if_eq VAR_RESULT, B_OUTCOME_CAUGHT, FarawayIsland_Interior_EventScript_CaughtMew
	goto_if_eq VAR_RESULT, B_OUTCOME_WON, FarawayIsland_Interior_EventScript_MewFled
	goto_if_eq VAR_RESULT, B_OUTCOME_RAN, FarawayIsland_Interior_EventScript_MewFled
	goto_if_eq VAR_RESULT, B_OUTCOME_PLAYER_TELEPORTED, FarawayIsland_Interior_EventScript_MewFled
	release
	end

FarawayIsland_Interior_EventScript_CaughtMew::
	setflag FLAG_CAUGHT_MEW
	release
	end

@ Won/ran: Mew flees for now but can be encountered again on a later visit
@ (only FLAG_CAUGHT_MEW hides it permanently).
FarawayIsland_Interior_EventScript_MewFled::
	setflag FLAG_DEFEATED_MEW
	setvar VAR_0x8004, SPECIES_MEW
	goto EventScript_MonFlewAway
	end
