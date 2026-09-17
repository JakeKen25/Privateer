# Privateer 0.932 Beta

Fixes the aircraft-default table issue identified after 0.93 Beta.

- Interpolates missing years between the surrounding observed yearly averages.
- Carries the latest values forward after the final observed year.
- Uses minimum fallback values only before the first observed year for that aircraft type.

Uses the original 0.93 Beta packaging configuration. The earlier Defender detection remains unresolved; this release does not claim to resolve it.
