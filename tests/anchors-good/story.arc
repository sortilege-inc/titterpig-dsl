ARC "Demo_Anchors_Arc" {
    NAME "DECISION-24 fixture — named blocks: anchors by hash, labels by name"
    SPEC_VERSION "0.6"
    VERSION "1.0"
    DEPENDS_ON "Demo_Anchors_Base"

    CAST {
        #AncDemoMonkFFFFFFFFFFFFFF ^"The Abbot" DEF { EXTENDS #AncDemoNpcTypeAAAAAAAAAAA ^"NPC" }
        # a quote inside a name is written \" (DECISION-25)
        #AncDemoPoetHHHHHHHHHHHHHH ^"Mrinmoy \"Vidyapati\" Mishra" DEF { EXTENDS #AncDemoNpcTypeAAAAAAAAAAA ^"NPC" }
    }

    LOCATION ^"Mountain Song Temple" #AncDemoTempleCCCCCCCCCCC {
        DESCRIPTION "A temple in the high passes."
    }
    # a block with no hash is a label: it can be named only inside this file
    LOCATION ^"The Lower Road" {
        DESCRIPTION "The path up from the valley."
    }

    FLOW {
        PHASE ^"Arrival" {
            SCENE_REF #AncDemoRoadGGGGGGGGGGGGG ^"On the Road"
            SCENE_REF #AncDemoCeremonyDDDDDDDDD
        }
    }

    SCENE ^"On the Road" #AncDemoRoadGGGGGGGGGGGGG {
        LOCATION ^"The Lower Road"
        RESOLUTIONS {
            RESOLUTION ^"Onward" {
                LEADS_TO [ #AncDemoCeremonyDDDDDDDDD ^"Tea Ceremony" ]
            }
        }
    }
    SCENE ^"Tea Ceremony" #AncDemoCeremonyDDDDDDDDD {
        LOCATION #AncDemoTempleCCCCCCCCCCC ^"Mountain Song Temple"
        PREREQUISITES { COMPLETED_SCENES [ #AncDemoRoadGGGGGGGGGGGGG ^"On the Road" ] }
        CONFLICT { OPPONENTS [ #AncDemoMonkFFFFFFFFFFFFFF ^"The Abbot", #AncDemoPoetHHHHHHHHHHHHHH ^"Mrinmoy \"Vidyapati\" Mishra", #AncDemoPoetHHHHHHHHHHHHHH ] }
    }
}
