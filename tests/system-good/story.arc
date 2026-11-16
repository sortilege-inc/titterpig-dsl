ARC "SysGood_Arc" {
    NAME "DECISION-62 fixture — an arc whose scene holds the system's own check"
    SPEC_VERSION "0.6"
    EDITION "sysgood"
    VERSION "0.6.1"
    DEPENDS_ON "SysGood_Core"

    SCENE ^"The Gate" #SygGateT8u9V1w2X3y4Z5a6 {
        DESCRIPTION "A guard bars the way."
        CHECKS {
            CHECK ^"Talk past the guard" {
                SKILL "Courtesy"
                TN 2
            }
        }
    }
}
