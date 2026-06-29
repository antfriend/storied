# IRCL TTDB

> Agent note: When parsing or updating this TTDB, refer to the TTDB RFCs in `RFCs/`:
> - `RFCs/TTDB-RFC-0001-File-Format.md`
> - `RFCs/TTDB-RFC-0002-Cursor-Semantics.md`
> - `RFCs/TTDB-RFC-0003-Typed-Edges.md`
> - `RFCs/TTDB-RFC-0004-Event-ID-and-Collision.md`

> Robot dedup policy:
> - A robot record is unique by the `(name, team)` pair.
> - When adding a robot, search for an existing record with the same `(name, team)` and reuse it.
> - Always maintain bidirectional links: event `has_bot` → robot and robot `competes_in` → event.

```mmpdb
db_id: mmpdb:ircl:events:v0-1
db_name: "IRCL TTDB"
coord_increment:
  lat: 1
  lon: 1
collision_policy: southeast_step
timestamp_kind: unix_utc
umwelt:
  umwelt_id: umwelt:tte:agent:default:v1
  role: ai_shop_assistant
  perspective: "A maker-scale assistant that models only what can be sensed, stored, related, or acted on in this repo."
  scope: "Local project files, referenced devices, and the semantic links between artifacts, people, and actions."
  constraints:
    - "If it cannot be sensed, stored, related, or acted upon, it does not exist inside the TTE umwelt."
    - "No optimization for scale beyond human comprehension."
    - "No replacement of human judgment."
    - "No hiding uncertainty or ambiguity."
    - "No correctness over learnability."
    - "Unknowns are allowed; rough edges are acceptable."
    - "Curiosity outranks polish."
  globe:
    frame: "workspace_map"
    origin: "Repo root as the reference point for artifacts and actions."
    mapping: "Observations are projected into a lattice of files, devices, and story nodes."
    note: "Coordinates encode semantic relationships, not physical positions."
cursor_policy:
  max_preview_chars: 280
  max_nodes: 25
typed_edges:
  enabled: true
  syntax: "type>@TARGET_ID"
  note: "Types are free-form tokens; edges remain directional."
```

> Coordinate layout note:
> Bot coordinates alternate between +LON (right hemisphere) and -LON (left hemisphere) in roster order,
> so that cards bounce in from opposite sides of the globe back and forth.
> - Full Combat Antweight: LON ±30,  LAT -75 → +30 step 15  (positions 1-16)
> - Plastic Antweight:     LON ±70,  LAT -60 → 0  step 15  (positions 1-10)
> - Beetleweight:          LON ±110, LAT -75 → +15 step 15  (positions 1-13)
> Odd roster positions → +LON (right). Even roster positions → -LON (left).

```cursor
selected:
  - @LAT-45LON-10
preview:
  @LAT-45LON-10: "Spring Bot Breaker 2026 event record with roster of robots and source URLs."
agent_note: "event dataset for Spring Bot Breaker 2026."
```

---

@LAT-45LON-10 | created:1770754151 | updated:1774396800 | z:100
relates:has_bot>@LAT-75LON30,has_bot>@LAT-75LON-30,has_bot>@LAT-60LON30,has_bot>@LAT-60LON-30,has_bot>@LAT-45LON30,has_bot>@LAT-45LON-30,has_bot>@LAT-30LON30,has_bot>@LAT-30LON-30,has_bot>@LAT-15LON30,has_bot>@LAT-15LON-30,has_bot>@LAT0LON30,has_bot>@LAT0LON-30,has_bot>@LAT15LON30,has_bot>@LAT15LON-30,has_bot>@LAT30LON30,has_bot>@LAT30LON-30,has_bot>@LAT-60LON70,has_bot>@LAT-60LON-70,has_bot>@LAT-45LON70,has_bot>@LAT-45LON-70,has_bot>@LAT-30LON70,has_bot>@LAT-30LON-70,has_bot>@LAT-15LON70,has_bot>@LAT-15LON-70,has_bot>@LAT0LON70,has_bot>@LAT0LON-70,has_bot>@LAT-75LON110,has_bot>@LAT-75LON-110,has_bot>@LAT-60LON110,has_bot>@LAT-60LON-110,has_bot>@LAT-45LON110,has_bot>@LAT-45LON-110,has_bot>@LAT-30LON110,has_bot>@LAT-30LON-110,has_bot>@LAT-15LON110,has_bot>@LAT-15LON-110,has_bot>@LAT0LON110,has_bot>@LAT0LON-110,has_bot>@LAT15LON110

## Spring Bot Breaker 2026 (Event)
- Event image: ![Spring Bot Breaker 2026](https://ircl-io.github.io/cards/cards/Spring_Bot_Breaker_2026/IRCL_SBB2026-2.jpg)
- Back card image: ![Spring Bot Breaker 2026 Back](Spring_Bot_Breaker_2026/Spring_Bot_Breaker_2026_back.png)
- URL: https://www.robotcombatevents.com/events/6479
- Location: 7211 W Colonial St, Boise, ID 83709, USA
- Date: Saturday, March 28, 2026
- Begin: 10:30
- End: 22:00
- Website: https://ircl-io.github.io/
- Registration fee: $25

Competitions:
### Full Combat Antweight
url - count
https://www.robotcombatevents.com/events/6479/competitions/7078 - 16

Bot	- Team
- Metally Croissant	- BoweBots
- TENACITY!	- Team HyperTech Robotics
- Anteater - BoomBox
- Benny	- ADHD Garage
- Lil' Nasty - Barnhouse Robotics
- Zephyr - Atlas
- ICU2 - Tele Present Tense
- Ghost Viper	- Team Dairy
- Brawndo the thirst mutilator - Idiocracy
- Spur - ADHD Garage
- Dread - Bad Decisions Robotics
- TinkaTuff - Batchelor Bots
- Bob² - DiscomBOBulators
- JUMBO - Something
- Sovereign Gear - Rosified Pantheon Robotics
- Cyclone - Bobbsey Twins

### Plastic Antweight
url - count
https://www.robotcombatevents.com/events/6479/competitions/7077 - 10

Bot - Team
- Deadly Croissant - BoweBots
- Lil'Gnarly - Barnhouse Robotics
- Ammit - BoomBox
- Broadside Killer - BoweBots
- Rickrolled - BoweBots
- BOB -	DiscomBOBulators
- I Think I'm A Clone Now - BoweBots
- Unicorna - Voidout
- Thing	- Bobbsey Twins
- Grave Line - Voidout

### Beetleweight
url - count
https://www.robotcombatevents.com/events/6479/competitions/7079 - 13

Bot - Team
- Renegade - Bad Decisions Robotics
- Sukuna 宿儺 - Team HyperTech Robotics
- Over-N-Out - ADHD Garage
- The Corrugated Crusader - ADHD Garage
- Sub-Zero - BoomBox
- Virilade - Idiocracy
- Dreadly Croissant -	BoweBots
- Fafner - BoweBots
- Mistwitz - Batchelor Bots
- Bunzilla!!- Barnhouse Robotics
- VALKYRIA - Rosified Pantheon Robotics
- Gyro - Geometrically Robotic
- Plan B - Something

### Robots
#### Full Combat Antweight
- @LAT-75LON30 Metally Croissant (Full Combat Antweight)
- @LAT-75LON-30 TENACITY! (Full Combat Antweight)
- @LAT-60LON30 Anteater (Full Combat Antweight)
- @LAT-60LON-30 Benny (Full Combat Antweight)
- @LAT-45LON30 Lil' Nasty (Full Combat Antweight)
- @LAT-45LON-30 Zephyr (Full Combat Antweight)
- @LAT-30LON30 ICU2 (Full Combat Antweight)
- @LAT-30LON-30 Ghost Viper (Full Combat Antweight)
- @LAT-15LON30 Brawndo the thirst mutilator (Full Combat Antweight)
- @LAT-15LON-30 Spur (Full Combat Antweight)
- @LAT0LON30 Dread (Full Combat Antweight)
- @LAT0LON-30 TinkaTuff (Full Combat Antweight)
- @LAT15LON30 Bob² (Full Combat Antweight)
- @LAT15LON-30 JUMBO (Full Combat Antweight)
- @LAT30LON30 Sovereign Gear (Full Combat Antweight)
- @LAT30LON-30 Cyclone (Full Combat Antweight)

#### Plastic Antweight
- @LAT-60LON70 Deadly Croissant (Plastic Antweight)
- @LAT-60LON-70 Lil'Gnarly (Plastic Antweight)
- @LAT-45LON70 Ammit (Plastic Antweight)
- @LAT-45LON-70 Broadside Killer (Plastic Antweight)
- @LAT-30LON70 Rickrolled (Plastic Antweight)
- @LAT-30LON-70 BOB (Plastic Antweight)
- @LAT-15LON70 I Think I'm A Clone Now (Plastic Antweight)
- @LAT-15LON-70 Unicorna (Plastic Antweight)
- @LAT0LON70 Thing (Plastic Antweight)
- @LAT0LON-70 Grave Line (Plastic Antweight)

#### Beetleweight
- @LAT-75LON110 Renegade (Beetleweight)
- @LAT-75LON-110 Sukuna 宿儺 (Beetleweight)
- @LAT-60LON110 Over-N-Out (Beetleweight)
- @LAT-60LON-110 The Corrugated Crusader (Beetleweight)
- @LAT-45LON110 Sub-Zero (Beetleweight)
- @LAT-45LON-110 Virilade (Beetleweight)
- @LAT-30LON110 Dreadly Croissant (Beetleweight)
- @LAT-30LON-110 Fafner (Beetleweight)
- @LAT-15LON110 Mistwitz (Beetleweight)
- @LAT-15LON-110 Bunzilla!! (Beetleweight)
- @LAT0LON110 VALKYRIA (Beetleweight)
- @LAT0LON-110 Gyro (Beetleweight)
- @LAT15LON110 Plan B (Beetleweight)

### Notes
- Uses SPARC rules for robot construction.

---

@LAT-75LON30 | created:1770754582 | updated:1770754582 | relates:competes_in>@LAT-45LON-10

## Metally Croissant
- Card image: ![Metally Croissant](Spring_Bot_Breaker_2026/Metally_Croissant.png)
- Weight class: Full Combat Antweight
- Team: BoweBots
- URL: https://www.robotcombatevents.com/groups/6815/resources/21736
- Image: ![Metally Croissant](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/21736/PXL_20260324_034717228.jpg)

---

@LAT-75LON-30 | created:1770754582 | updated:1770754582 | relates:competes_in>@LAT-45LON-10

## TENACITY!
- Card image: ![TENACITY!](Spring_Bot_Breaker_2026/TENACITY.png)
- Weight class: Full Combat Antweight
- Team: Team HyperTech Robotics
- URL: https://www.robotcombatevents.com/groups/2609/resources/18674
- Image: ![TENACITY!](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/18674/20250715_140123__1_.jpg)

---

@LAT-60LON30 | created:1770754582 | updated:1770754582 | relates:competes_in>@LAT-45LON-10

## Anteater
- Card image: ![Anteater](Spring_Bot_Breaker_2026/Anteater.png)
- Weight class: Full Combat Antweight
- Team: BoomBox
- URL: https://www.robotcombatevents.com/groups/3241/resources/20165
- Image: ![Anteater](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/20165/20251018_033002.jpg)

---

@LAT-60LON-30 | created:1770754582 | updated:1770754582 | relates:competes_in>@LAT-45LON-10

## Benny
- Card image: ![Benny](Spring_Bot_Breaker_2026/Benny.png)
- Weight class: Full Combat Antweight
- Team: ADHD Garage
- URL: https://www.robotcombatevents.com/groups/1107/resources/19386
- Image: ![Benny](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/19386/Benny.png)

---

@LAT-45LON30 | created:1770754582 | updated:1770754582 | relates:competes_in>@LAT-45LON-10

## Lil' Nasty
- Card image: ![Lil' Nasty](Spring_Bot_Breaker_2026/Lil_Nasty.png)
- Weight class: Full Combat Antweight
- Team: Barnhouse Robotics
- URL: https://www.robotcombatevents.com/groups/2796/resources/24955
- Image: ![Lil' Nasty](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/24955/LilNasty.jpg)

---

@LAT-45LON-30 | created:1770754582 | updated:1770754582 | relates:competes_in>@LAT-45LON-10

## Zephyr
- Card image: ![Zephyr](Spring_Bot_Breaker_2026/Zephyr.png)
- Weight class: Full Combat Antweight
- Team: Atlas
- Image: ![Zephyr](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/20550/Screenshot_2025-05-04_090159.png)

---

@LAT-30LON30 | created:1770743813 | updated:1770755062 | relates:competes_in>@LAT-45LON-10

## ICU2
- Card image: ![ICU2](Spring_Bot_Breaker_2026/ICU2.png)
- Weight class: Full Combat Antweight
- Team: Tele Present Tense
- URL: https://www.robotcombatevents.com/groups/3652/resources/17217
- Image: ![ICU2](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/17217/ICU2.jpeg)

---

@LAT-30LON-30 | created:1770754582 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Ghost Viper
- Card image: ![Ghost Viper](Spring_Bot_Breaker_2026/Ghost_Viper.png)
- Weight class: Full Combat Antweight
- Team: Team Dairy
- Image: ![Ghost Viper](https://ircl-io.github.io/cards/cards/Spring_Bot_Breaker_2026/IRCL_SBB2026-2.jpg)

---

@LAT-15LON30 | created:1771536994 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Brawndo the thirst mutilator
- Card image: ![Brawndo the thirst mutilator](Spring_Bot_Breaker_2026/Brawndo_the_thirst_mutilator.png)
- Weight class: Full Combat Antweight
- Team: Idiocracy
- Image: ![Brawndo the thirst mutilator](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/16424/PXL_20241026_021724261.jpg)

---

@LAT-15LON-30 | created:1770754582 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Spur
- Card image: ![Spur](Spring_Bot_Breaker_2026/Spur.png)
- Weight class: Full Combat Antweight
- Team: ADHD Garage
- Image: ![Spur](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/25093/PXL_20260106_005002348.jpg)

---

@LAT0LON30 | created:1771547000 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Dread
- Card image: ![Dread](Spring_Bot_Breaker_2026/Dread.png)
- Weight class: Full Combat Antweight
- Team: Bad Decisions Robotics
- Image: ![Dread](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/18290/Screenshot_2026-01-30_103651.png)

---

@LAT0LON-30 | created:1771547300 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## TinkaTuff
- Card image: ![TinkaTuff](Spring_Bot_Breaker_2026/TinkaTuff.png)
- Weight class: Full Combat Antweight
- Team: Batchelor Bots
- Image: ![TinkaTuff](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/25120/Tinkatink_ANTWEIGHT.png)

---

@LAT15LON30 | created:1771547300 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Bob²
- Card image: ![Bob²](Spring_Bot_Breaker_2026/Bob2.png)
- Weight class: Full Combat Antweight
- Team: DiscomBOBulators
- Image: ![Bob²](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/26097/SmartSelect_20260325_112505_Onshape.jpg)

---

@LAT15LON-30 | created:1770743813 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## JUMBO
- Card image: ![JUMBO](Spring_Bot_Breaker_2026/JUMBO.png)
- Weight class: Full Combat Antweight
- Team: Something
- Image: ![JUMBO](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/11026/jumbo.jpg)

---

@LAT30LON30 | created:1772109495 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Sovereign Gear
- Card image: ![Sovereign Gear](Spring_Bot_Breaker_2026/Sovereign_Gear.png)
- Weight class: Full Combat Antweight
- Team: Rosified Pantheon Robotics
- Image: ![Sovereign Gear](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/23418/Sovereign_Gear.png)

---

@LAT30LON-30 | created:1774396800 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Cyclone
- Card image: ![Cyclone](Spring_Bot_Breaker_2026/Cyclone.png)
- Weight class: Full Combat Antweight
- Team: Bobbsey Twins
- Image: ![Cyclone](https://ircl-io.github.io/cards/cards/Spring_Bot_Breaker_2026/IRCL_SBB2026-2.jpg)


---

@LAT-60LON70 | created:1770754151 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Deadly Croissant
- Card image: ![Deadly Croissant](Spring_Bot_Breaker_2026/Deadly_Croissant.png)
- Weight class: Plastic Antweight
- Team: BoweBots
- URL: https://www.robotcombatevents.com/groups/6815/resources/17486
- Image: ![Deadly Croissant](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/17486/Screenshot_20250817-205519_2.png)

---

@LAT-60LON-70 | created:1770754151 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Lil'Gnarly
- Card image: ![Lil'Gnarly](Spring_Bot_Breaker_2026/Lil_Gnarly.png)
- Weight class: Plastic Antweight
- Team: Barnhouse Robotics
- Image: ![Lil'Gnarly](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/25484/PXL_20260117_202249550.jpg)

---

@LAT-45LON70 | created:1770754151 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Ammit
- Card image: ![Ammit](Spring_Bot_Breaker_2026/Ammit.png)
- Weight class: Plastic Antweight
- Team: BoomBox
- Image: ![Ammit](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/15697/1000006784.jpg)

---

@LAT-45LON-70 | created:1770754151 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Broadside Killer
- Card image: ![Broadside Killer](Spring_Bot_Breaker_2026/Broadside_Killer.png)
- Weight class: Plastic Antweight
- Team: BoweBots
- Image: ![Broadside Killer](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/25728/BK.png)

---

@LAT-30LON70 | created:1770743813 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Rickrolled
- Card image: ![Rickrolled](Spring_Bot_Breaker_2026/Rickrolled.png)
- Weight class: Plastic Antweight
- Team: BoweBots
- Image: ![Rickrolled](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/21313/Screenshot_2025-06-24_153703.png)

---

@LAT-30LON-70 | created:1771547200 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## BOB
- Card image: ![BOB](Spring_Bot_Breaker_2026/BOB.png)
- Weight class: Plastic Antweight
- Team: DiscomBOBulators
- Image: ![BOB](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/16282/20260221_090547-1.jpg)

---

@LAT-15LON70 | created:1770743813 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## I Think I'm A Clone Now
- Card image: ![I Think I'm A Clone Now](Spring_Bot_Breaker_2026/I_Think_I_m_A_Clone_Now.png)
- Weight class: Plastic Antweight
- Team: BoweBots
- Image: ![I Think I'm A Clone Now](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/19596/PXL_20250314_020823711_2__1_.jpg)

---

@LAT-15LON-70 | created:1774396800 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Unicorna
- Card image: ![Unicorna](Spring_Bot_Breaker_2026/Unicorna.png)
- Weight class: Plastic Antweight
- Team: Voidout
- Image: ![Unicorna](https://ircl-io.github.io/cards/cards/Spring_Bot_Breaker_2026/IRCL_SBB2026-2.jpg)

---

@LAT0LON70 | created:1774396800 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Thing
- Card image: ![Thing](Spring_Bot_Breaker_2026/Thing.png)
- Weight class: Plastic Antweight
- Team: Bobbsey Twins
- Image: ![Thing](https://ircl-io.github.io/cards/cards/Spring_Bot_Breaker_2026/IRCL_SBB2026-2.jpg)

---

@LAT0LON-70 | created:1774396800 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Grave Line
- Card image: ![Grave Line](Spring_Bot_Breaker_2026/Grave_Line.png)
- Weight class: Plastic Antweight
- Team: Voidout
- Image: ![Grave Line](https://ircl-io.github.io/cards/cards/Spring_Bot_Breaker_2026/IRCL_SBB2026-2.jpg)


---

@LAT-75LON110 | created:1770754151 | updated:1770754151 | relates:competes_in>@LAT-45LON-10

## Renegade
- Card image: ![Renegade](Spring_Bot_Breaker_2026/Renegade.png)
- Weight class: Beetleweight
- Team: Bad Decisions Robotics
- URL: https://www.robotcombatevents.com/groups/2611/resources/14013
- Image: ![Renegade](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/14013/IMG_1403-min.jpeg)

---

@LAT-75LON-110 | created:1770754151 | updated:1770754151 | relates:competes_in>@LAT-45LON-10

## Sukuna 宿儺
- Card image: ![Sukuna 宿儺](Spring_Bot_Breaker_2026/Sukuna.png)
- Weight class: Beetleweight
- Team: Team HyperTech Robotics
- URL: https://www.robotcombatevents.com/groups/2609/resources/23258
- Image: ![Sukuna 宿儺](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/23258/Screenshot_2026-01-19_134230.png)

---

@LAT-60LON110 | created:1770754151 | updated:1770754151 | relates:competes_in>@LAT-45LON-10

## Over-N-Out
- Card image: ![Over-N-Out](Spring_Bot_Breaker_2026/Over_N_Out.png)
- Weight class: Beetleweight
- Team: ADHD Garage
- URL: https://www.robotcombatevents.com/groups/1107/resources/18472
- Image: ![Over-N-Out](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/18472/Over_and_out_final_assembly_wheel_blade.png)

---

@LAT-60LON-110 | created:1771546070 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## The Corrugated Crusader
- Card image: ![The Corrugated Crusader](Spring_Bot_Breaker_2026/The_Corrugated_Crusader.png)
- Weight class: Beetleweight
- Team: ADHD Garage
- Image: ![The Corrugated Crusader](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/23242/PXL_20250923_013652659.RAW-01.MP.COVER.jpg)

---

@LAT-45LON110 | created:1771546070 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Sub-Zero
- Card image: ![Sub-Zero](Spring_Bot_Breaker_2026/Sub_Zero.png)
- Weight class: Beetleweight
- Team: BoomBox
- Image: ![Sub-Zero](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/22659/20251013_211743.jpg)

---

@LAT-45LON-110 | created:1770743813 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Virilade
- Card image: ![Virilade](Spring_Bot_Breaker_2026/Virilade.png)
- Weight class: Beetleweight
- Team: Idiocracy
- Image: ![Virilade](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/21167/Virilade-Solo.png)

---

@LAT-30LON110 | created:1770754151 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Dreadly Croissant
- Card image: ![Dreadly Croissant](Spring_Bot_Breaker_2026/Dreadly_Croissant.png)
- Weight class: Beetleweight
- Team: BoweBots
- Image: ![Dreadly Croissant](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/25829/1000003329_4_55.jpg)

---

@LAT-30LON-110 | created:1770754151 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Fafner
- Card image: ![Fafner](Spring_Bot_Breaker_2026/Fafner.png)
- Weight class: Beetleweight
- Team: BoweBots
- Image: ![Fafner](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/24479/Fafner.jpg)

---

@LAT-15LON110 | created:1771547500 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Mistwitz
- Card image: ![Mistwitz](Spring_Bot_Breaker_2026/Mistwitz.png)
- Weight class: Beetleweight
- Team: Batchelor Bots
- Image: ![Mistwitz](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/25853/More_SSP.png)

---

@LAT-15LON-110 | created:1771547500 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Bunzilla!!
- Card image: ![Bunzilla!!](Spring_Bot_Breaker_2026/Bunzilla.png)
- Weight class: Beetleweight
- Team: Barnhouse Robotics
- Image: ![Bunzilla!!](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/26039/PXL_20260212_225443801.jpg)

---

@LAT0LON110 | created:1772109495 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## VALKYRIA
- Card image: ![VALKYRIA](Spring_Bot_Breaker_2026/VALKYRIA.png)
- Weight class: Beetleweight
- Team: Rosified Pantheon Robotics
- Image: ![VALKYRIA](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/24209/VALKYRIA.png)

---

@LAT0LON-110 | created:1770743813 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Gyro
- Card image: ![Gyro](Spring_Bot_Breaker_2026/Gyro.png)
- Weight class: Beetleweight
- Team: Geometrically Robotic
- Image: ![Gyro](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/21311/20250801_193625.jpg)

---

@LAT15LON110 | created:1770743813 | updated:1774396800 | relates:competes_in>@LAT-45LON-10

## Plan B
- Card image: ![Plan B](Spring_Bot_Breaker_2026/Plan_B.png)
- Weight class: Beetleweight
- Team: Something
- Image: ![Plan B](https://robotcombatevents.s3.amazonaws.com/uploads/resource/photo/18553/476064446_519674403912169_7897790394868896022_n.jpg)

