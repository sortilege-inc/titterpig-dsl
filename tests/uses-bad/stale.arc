ARC "UsesBad_Stale_Arc" {
    NAME "DECISION-55 fixture — a DEPENDS_ON that names no file: an error, as for any file"
    SPEC_VERSION "0.6"
    EDITION "demo"
    VERSION "1.0"
    DEPENDS_ON "UsesBad_Base"
    DEPENDS_ON "UsesBad_No_Such_File"
}
