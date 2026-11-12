ARC "Demo_NarBad_Arc" {
    NAME "DECISION-22 fixture — each FROM line here holds one intentional finding"
    SPEC_VERSION "0.6"
    VERSION "1.0"
    DEPENDS_ON "Demo_NarBad_Base"

    CAST {
        FROM "Demo_NarBad_NPCs" INCLUDE [ #NarBadXGovernorBBBBBBBBBB ^"The Governor" ]
        FROM EXTENSION "Demo_NarBad_No_Such_File" INCLUDE [ #NarBadXSpiritCCCCCCCCCCCC ^"The Spirit" ]
        FROM FRAME "Demo_NarBad_NPCs" INCLUDE [ #NarBadXSpiritCCCCCCCCCCCC ^"The Spirit" ]
        FROM EXTENSION "Demo_NarBad_NPCs" INCLUDE [ #NarBadXNobodyZZZZZZZZZZZZ ^"Nobody At All" ]
        FROM EXTENSION "Demo_NarBad_NPCs" INCLUDE [ #NarBadXNoSuchHashZZZZZZZZ ^"The Governor" ]
        FROM ARC "Demo_NarBad_Base"
    }

    # each scene below holds one intentional finding in its TYPE
    SCENE ^"A string for a type" #NarBadXSceneOneTTTTTTTTT {
        TYPE "Roleplay"
    }
    SCENE ^"A type that is not defined" #NarBadXSceneTwoUUUUUUUUU {
        TYPE ^"Heist"
    }
    SCENE ^"An entity that is not a scene type" #NarBadXSceneThrVVVVVVVVV {
        TYPE #NarBadXNpcTypeAAAAAAAAAAA ^"NPC"
    }
}
