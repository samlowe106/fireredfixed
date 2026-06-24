Route4_MapScripts::
	.byte 0

Route4_EventScript_Unused::
	end

Route4_EventScript_Woman::
	msgbox Route4_Text_TrippedOverGeodude, MSGBOX_NPC
	end

Route4_EventScript_MtMoonSign::
	msgbox Route4_Text_MtMoonEntrance, MSGBOX_SIGN
	end

Route4_EventScript_RouteSign::
	msgbox Route4_Text_RouteSign, MSGBOX_SIGN
	end

@ ---------------------------------------------------------------------------
@ Mt. Moon meteorites, one per DEOXYS Forme. Add the meteor sprites + collision
@ in Route4/map.json later as object_events, each pointing at one of these scripts.
@ The Forme-change action is a TODO; for now each just shows its text.
@ ---------------------------------------------------------------------------
Route4_EventScript_MeteorNormal::
	lock
	@ TODO: switch the player's DEOXYS to its Normal Forme
	msgbox Route4_Text_MeteorNormal, MSGBOX_DEFAULT
	release
	end

Route4_EventScript_MeteorAttack::
	lock
	@ TODO: switch the player's DEOXYS to its Attack Forme
	msgbox Route4_Text_MeteorAttack, MSGBOX_DEFAULT
	release
	end

Route4_EventScript_MeteorDefense::
	lock
	@ TODO: switch the player's DEOXYS to its Defense Forme
	msgbox Route4_Text_MeteorDefense, MSGBOX_DEFAULT
	release
	end

Route4_EventScript_MeteorSpeed::
	lock
	@ TODO: switch the player's DEOXYS to its Speed Forme
	msgbox Route4_Text_MeteorSpeed, MSGBOX_DEFAULT
	release
	end
