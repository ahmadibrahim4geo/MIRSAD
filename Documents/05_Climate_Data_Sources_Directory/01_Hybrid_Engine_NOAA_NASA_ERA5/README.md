# Hybrid source stages

NOAA GSOD → Open-Meteo ERA5/Land → NASA POWER → optional monthly Gap Fill.

Finish each source across the selected network before requesting missing cells from the next source. Any-point Hybrid skips NOAA. Valid higher-priority values remain unchanged. No source or filling method guarantees complete coverage. Raw observations, quality flags, per-value provenance and separate monthly estimates remain inspectable. Never fabricate daily observations from monthly filling.

[Full source directory](../SOURCES_EN.md)
