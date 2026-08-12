# Character Lock

The production pipeline must never infer character identity from a name alone.

## LIN_FENG

- Character ID: `LIN_FENG`
- Name: หลินเฟิง
- Gender: `MALE`
- Age: 25
- Appearance: ชายจีนโบราณ ใบหน้าชายชัดเจน ผมดำยาว ดวงตาคม
- Outfit: ชุดจีนโบราณสีดำ
- Voice ID: `MALE_THAI_LIN_FENG`

## MYSTERIOUS_WOMAN

- Character ID: `MYSTERIOUS_WOMAN`
- Name: หญิงปริศนา
- Gender: `FEMALE`
- Age: 25
- Appearance: หญิงจีนโบราณ ใบหน้าหญิงชัดเจน ผมดำยาว
- Outfit: ชุดจีนโบราณสีขาว
- Voice ID: `FEMALE_THAI_MYSTERIOUS_WOMAN`

## Speaker rule

Every dialogue line must carry `speaker_id` and `voice_id`. The voice must exactly match the Character Bible. Video generation must receive explicit character identities and speaker assignments. A model must never infer the speaker from the character name alone.
