# Relations: tensions, alliances and wars

Development 0.9.8.1 includes experimental relationship actions. Select an action
beside a nation in Relationship Manager. Details previews the exact field changes.
Use either a numerical tension edit or an action for a pair. Reset/Cancel discard
pending choices; Apply updates memory. Save or Save As uses existing backup and
external-file-change protection.

- **Create Alliance** sets the observed alliance value 60, preserving tension.
  Its duration and expiry have not been verified. Player treaty display is confirmed.
- **Break Treaty** sets alliance values to 0; in-game testing remains pending.
- **Reset Tension to 0** clears ordinary tension in either direction. Active-war
  or special out-of-range tension requires a separate war operation.
- **Start War** sets General/War=1 and the selected opponent's Tension=50.
  Supported only from peace for player relationships, with no existing war-associated
  opponents and no treaty with the target. Immediate war and one-turn persistence
  were observed in Game7; natural declaration financial adjustments are not reproduced.
- **Ceasefire** is experimental and awaiting user testing. It requires exactly one
  active player opponent. It sets War=-1, opponent Tension=3, player VP=0 and
  General/EnemyVP=0. No territorial concessions, reparations or financial adjustments
  are synthesized. Additional game-side war cleanup remains unverified.

Player pairs use the foreign nation's Tension/Allied fields. AI pairs use both
reciprocal AITension/AIAlliance fields. AI-only war/ceasefire and multi-opponent
settlements are not supported. Each batch is preflighted and applied atomically.

Validation: existing diplomacy tests and new action tests cover reciprocal mapping,
war/ceasefire round trips, reset, malformed fields, conflicts and failed-batch rollback.
