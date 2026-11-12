ARC "Demo_AncBad_Arc" {
    NAME "DECISION-24 fixture — each reference and each repeated hash here is an intentional finding"
    SPEC_VERSION "0.6"
    VERSION "1.0"
    DEPENDS_ON "Demo_AncBad_Base"

    LOCATION ^"Mountain Song Temple" #AncBadXTempleCCCCCCCCCCC {
        DESCRIPTION "A temple in the high passes."
    }
    ENTRY ^"First Sidebar" #AncBadXSharedHHHHHHHHHHHH {
        DESCRIPTION "One entry."
    }
    ENTRY ^"Second Sidebar" #AncBadXSharedHHHHHHHHHHHH {
        DESCRIPTION "Another entry with the same hash."
    }

    FLOW {
        PHASE ^"Arrival" {
            SCENE_REF #AncBadXNoSuchSceneZZZZZZZ
            SCENE_REF #AncBadXNoSuchSceneYYYYYYY ^"A Scene That Is Not Here"
        }
    }

    SCENE ^"Tea Ceremony" #AncBadXCeremonyDDDDDDDDD {
        LOCATION ^"A Place That Is Not Here"
        CONFLICT { OPPONENTS [ #AncBadXNobodyZZZZZZZZZZZZ ] }
        RESOLUTIONS { RESOLUTION ^"Onward" { LEADS_TO [ #AncBadXNowhereZZZZZZZZZZZ ] } }
    }
}
