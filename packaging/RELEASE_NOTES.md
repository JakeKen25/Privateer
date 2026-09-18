# Privateer 0.932 Beta

Static-table rebuild for testing the reported Microsoft Defender detection.

- Aircraft defaults now read a stored row for the exact aircraft type and campaign year.
- All supported years (1800-2200) have precomputed values; aircraft creation no longer interpolates or calculates year-based default statistics.
- Missing intermediate years have plausible values filled in beforehand. Earlier years use minimum defaults; later years repeat the final observed averages.
- All displayed aircraft statistics remain editable.

This replaces the earlier 0.932 Beta package for testing. The distinct tag `v0.932-beta-static-table` identifies this build while preserving the original tag. The program version remains 0.932 Beta.

Validation: all 92 source tests passed. The earlier Defender detection remains unresolved; this build is not confirmed to fix it. Windows installation instructions are included as INSTALL.txt in the ZIP.
