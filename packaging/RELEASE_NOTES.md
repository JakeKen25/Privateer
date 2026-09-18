# Privateer 0.932 Beta

Updated build with the equivalent-year aircraft slider.

- Choose an equivalent year to load that year's stored aircraft statistics while keeping the design and base model dates at the current campaign year.
- Each aircraft type's slider and table span its first through last recorded Game 6 years. Intermediate years retain precomputed values; no runtime interpolation is performed.
- Changing aircraft type resets the slider to the campaign year or nearest available endpoint. Moving the slider replaces the editable statistics.

Replaces the previous ZIP on this release. Aircraft implementation: https://github.com/JakeKen25/Privateer/commit/72306b258b41768f672380e1662430b3b5230767 . The existing release tag is preserved; GitHub's automatic source archives describe the original tagged build. Use the attached Windows ZIP for this updated application.

Validation: all 93 source tests passed, including slider and saved design-date checks. The local app opened successfully. The preceding static-table build passed the user's Defender test; this rebuilt package needs its own check. INSTALL.txt is included in the Windows ZIP.
