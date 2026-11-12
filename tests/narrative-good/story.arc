ARC "Demo_Narrative_Arc" {
    NAME "DECISION-22 fixture — imports by FROM, and both orders of a block's name and hash"
    SPEC_VERSION "0.6"
    VERSION "1.0"
    DEPENDS_ON "Demo_Narrative_Base"

    # a setting's location is imported the way a cast member is
    FROM SETTING "Demo_Narrative_Setting" INCLUDE [ #NarDemoRiverCityJJJJJJJJ ^"The River City" ]

    CAST {
        # the FROM line is the declaration: no USES_ line is needed for it
        FROM EXTENSION "Demo_Narrative_NPCs" INCLUDE [
            #NarDemoGovernorBBBBBBBBBB ^"The Governor",
            #NarDemoSpiritCCCCCCCCCCCC ^"The Spirit"
        ]
        FROM FRAME "Demo_Narrative_Frame" INCLUDE [ #NarDemoPublisherDDDDDDDDD ^"The Publisher" ]

        #NarDemoAuthorEEEEEEEEEEEE ^"The Author" DEF {
            EXTENDS #NarDemoNpcTypeAAAAAAAAAAA ^"NPC"
            PROPERTIES {
                ^"Role" STRING "The missing author"
                ^"Rings" DEF { ^"Air" INTEGER 3  ^"Fire" INTEGER 5 }
                ^"Skills" DEF { ^"Artisan" INTEGER 1  ^"Martial" INTEGER 2  ^"Social" INTEGER 1 }
            }
        }
    }

    # a block's name comes before its hash by convention; hash before name is also legal
    LOCATION ^"The Teahouse" #NarDemoTeahouseFFFFFFFFF {
        DESCRIPTION "An old teahouse on the river."
    }
    LOCATION #NarDemoGardensGGGGGGGGGG ^"The Gardens" {
        DESCRIPTION "The manor's interior garden."
    }

    FLOW {
        PHASE ^"Investigation" {
            SCENE_REF #NarDemoCeremonyHHHHHHHHH ^"The Tea Ceremony"
            SCENE_REF #NarDemoConfrontIIIIIIII ^"The Confrontation"
        }
    }

    SCENE ^"The Tea Ceremony" #NarDemoCeremonyHHHHHHHHH {
        TYPE #NarDemoRoleplayNNNNNNNNNN ^"Roleplay"
        LOCATION #NarDemoTeahouseFFFFFFFFF ^"The Teahouse"
        DESCRIPTION "The characters arrive at the teahouse."
    }
    SCENE #NarDemoConfrontIIIIIIII ^"The Confrontation" {
        TYPE #NarDemoCombatPPPPPPPPPPPP ^"Combat"
        LOCATION #NarDemoGardensGGGGGGGGGG ^"The Gardens"
        DESCRIPTION "The characters face the author."

        CONFLICT {
            # the source leaves it open: fought, or talked out
            TYPE CHOOSE 1 [ #NarDemoSkirmishRRRRRRRRRR ^"Skirmish", #NarDemoIntrigueSSSSSSSSSS ^"Intrigue" ]
            STAKES "The author's life"
            OPPONENTS [ #NarDemoAuthorEEEEEEEEEEEE ^"The Author" ]
        }
    }
}
