# Pulse — Print & Play Manifest

Everything needed to build a playable copy of [Pulse](Pulse.md) from a home printer,
some cardstock, and a token bag. Card faces are written out verbatim — copy each block
onto a card. Counts are exact for a **2–5 player** set.

- **Recommended card size:** 63 × 88 mm (standard poker / "bridge-ish") — 9 per A4/Letter sheet.
- **Cardstock:** 250–300 gsm, or print on paper and sleeve over scrap cards.
- **Color coding (optional but helpful):** Story = gold border, Character = deep blue,
  Part = slate gray, Feeling = tinted by valence (warm = positive, cool = negative).
- **Total card count:** **57 cards** (6 Story + 5 Character + 8 Part + 32 Feeling + 6 reference).
- **Total tokens:** **7 Pulse + 12 Drift + 3 Swing + 1 Baton + 1 Story Marker = 24 pieces.**

> Print checklist at the very bottom (§7) if you just want the cut list.

---

## 1. Story Track cards ×6 (gold border)

The 6-beat Hero's Arc chart, laid left-to-right in the center. One card per beat.

```
┌──────────────────────────┐
│ STORY ① · SERENITY        │
│ @LAT10LON-10 · valence +  │
│                           │
│ "A mild, quiet ease."     │
│                           │
│ edge out: can_deepen → ②  │
│ ▣ ordinary world          │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ STORY ② · UNEASE          │
│ @LAT-10LON-10 · valence − │
│                           │
│ "Something not quite      │
│  right."                  │
│ edge out: resonates → ③   │
│ ▣ the call                │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ STORY ③ · FEAR            │
│ @LAT-30LON20 · valence −  │
│                           │
│ "Danger crystallizes and  │
│  hijacks attention."      │
│ edge out: down → ④        │
│ ▣ the ordeal              │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ STORY ④ · GRIEF           │
│ @LAT-30LON-30 · valence − │
│                           │
│ "What was loved is        │
│  irreversibly gone."      │
│ edge out: bloom → ⑤       │
│ ▣ the dark night          │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ STORY ⑤ · HOPE            │
│ @LAT20LON20 · valence +   │
│                           │
│ "A possibility opens in   │
│  the wreckage."           │
│ edge out: bloom → ⑥       │
│ ▣ the turn                │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ STORY ⑥ · JOY  ★ WIN      │
│ @LAT30LON30 · valence +   │
│                           │
│ "The self reconstituted   │
│  and enlarged."           │
│ reach here = WIN          │
│ ▣ the return              │
└──────────────────────────┘
```

---

## 2. Character cards ×5 (deep blue)

One per player; deal one each, return the rest to the box. `Reaches` = play for free
(+ Swing token if clean). `Strains` = +1 Drift to play.

```
┌──────────────────────────┐
│ THE SEEKER                │
│ Disposition: CURIOSITY    │
│ @LAT10LON40               │
│                           │
│ Reaches: Unease, Hope     │
│ Strains: Grief            │
│ ── "A forward lean toward │
│     the unknown."         │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ THE WARDEN                │
│ Disposition: SUSPICION    │
│ @LAT-20LON-30             │
│                           │
│ Reaches: Fear, Grief      │
│ Strains: Joy              │
│ ── "Reading the world for │
│     hidden threat."       │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ THE HEALER                │
│ Disposition: COMPASSION   │
│ @LAT30LON40               │
│                           │
│ Reaches: Hope, Joy        │
│ Strains: Fear             │
│ ── "Moved to care for     │
│     another's suffering." │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ THE HERMIT                │
│ Disposition: EQUANIMITY   │
│ @LAT30LON-20              │
│                           │
│ Reaches: Serenity, Grief  │
│ Strains: Hope             │
│ ── "Holds joy and sorrow  │
│     without overturning." │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ THE TRICKSTER             │
│ Disposition: INDIFFERENCE │
│ @LAT-10LON-40             │
│                           │
│ Reaches: Fear, Unease     │
│ Strains: Joy, Hope        │
│ ── "The world does not    │
│     call to it."          │
└──────────────────────────┘
```

---

## 3. Part cards ×8 (slate gray)

Deal one per player at the start of each story. Two copies each of Hi-hat / Backbeat so
larger tables can double up; Lead and Rim are single but combinable. With 2–3 players,
combine masks so all four beats of the bar are covered.

| Qty | Part | beat_mask | Note on face |
|----|------|-----------|--------------|
| 2 | **HI-HAT** | beats ① ② ③ ④ | "Timekeeper — the band's spine. You play every beat." |
| 2 | **BACKBEAT** | beats ② ④ | "The groove. You hold the bar when the Baton hands off." |
| 2 | **LEAD** | beat ① (downbeat) | "You sound the story advance. Your clean downbeat moves the Marker." |
| 2 | **RIM** | beat ③ | "The offbeat accent. You cover the gap in the middle of the bar." |

```
┌──────────────────────────┐
│ PART · HI-HAT             │
│ beat_mask: ① ② ③ ④        │
│                           │
│ Timekeeper — every beat.  │
│ The band's spine.         │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ PART · BACKBEAT           │
│ beat_mask: ② ④            │
│                           │
│ The groove. Holds the bar │
│ during a Baton handoff.   │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ PART · LEAD               │
│ beat_mask: ① (downbeat)   │
│                           │
│ Sounds the story advance. │
│ Clean downbeat = Marker++ │
└──────────────────────────┘
```
```
┌──────────────────────────┐
│ PART · RIM                │
│ beat_mask: ③              │
│                           │
│ Offbeat accent. Covers    │
│ the middle of the bar.    │
└──────────────────────────┘
```

---

## 4. Feeling deck ×32 (valence-tinted)

Your draw deck; hold **3**. Each card names a Feeling, its node, and which Story beat(s)
it legally lands on — exact match, or a typed edge toward it (`resonates_with`,
`can_deepen_into`, `intensifies_into`). The neighbor cards are the spice: they let a
character sidestep a Strain by playing an adjacent emotion that edges into the required
beat.

**Exact-match cards (the six arc emotions) — 4 copies each = 24 cards:**

| Qty | Feeling | Node | Lands on |
|----|---------|------|----------|
| 4 | **Serenity** | `@LAT10LON-10` | Story ① (also edges → Unease) |
| 4 | **Unease** | `@LAT-10LON-10` | Story ② (also edges → Fear) |
| 4 | **Fear** | `@LAT-30LON20` | Story ③ (also edges → Grief) |
| 4 | **Grief** | `@LAT-30LON-30` | Story ④ (also edges → Hope via "bloom") |
| 4 | **Hope** | `@LAT20LON20` | Story ⑤ (also edges → Joy) |
| 4 | **Joy** | `@LAT30LON30` | Story ⑥ |

**Neighbor cards (field-adjacent, edge-only) — 8 cards:**

| Qty | Feeling | Node | Edges toward (legal on) |
|----|---------|------|--------------------------|
| 2 | **Contentment** | `@LAT20LON-10` | ① Serenity / ⑥ Joy (`can_deepen_into`) |
| 2 | **Melancholy** | `@LAT-10LON-20` | ② Unease / ④ Grief (`resonates_with`) |
| 2 | **Frustration** | `@LAT-20LON20` | ③ Fear (`can_become`) |
| 2 | **Excitement** | `@LAT30LON20` | ⑤ Hope / ⑥ Joy (`resonates_with`) |

**Card face template (Feeling):**
```
┌──────────────────────────┐
│ FEELING · FEAR            │
│ @LAT-30LON20 · −          │
│                           │
│ Lands: ③ Fear             │
│ Edge:  intensifies → ④    │
│                           │
│ "The body preparing for   │
│  threat."                 │
└──────────────────────────┘
```

> **Deck math:** 24 exact + 8 neighbor = **32 cards**. At 3-in-hand for up to 5 players
> that's 15 dealt, leaving a 17-card draw — enough for a full 3-story set without
> reshuffling most games. Reshuffle the discard if the deck runs out.

---

## 5. Reference cards ×6 (one per player + spare)

Print the [Pulse §9 quick-reference](Pulse.md#9-quick-reference-card) onto a card so each
player has the loop at the table. Verbatim face:

```
┌────────────────────────────────────────┐
│ PULSE — QUICK REFERENCE                 │
│ A BAR = 4 metronome beats.              │
│ YOUR BEAT = your Part's beat_mask.      │
│                                         │
│ ON YOUR BEAT, in time with the click:   │
│  play a Feeling that REACHES/EDGES the  │
│  required emotion.                      │
│   Reaches -> clean, take a Swing token  │
│   Strains -> +1 Drift                   │
│  miss/late/illegal -> -1 Pulse, +1 Drift│
│  two players same beat -> -1 Pulse      │
│                                         │
│ CONDUCTOR (Baton): calls next emotion   │
│  on beat 4; must Reach it. Bust/strain  │
│  -> hand baton to one who Reaches; era+1│
│  Backbeat holds; new conductor count-in.│
│                                         │
│ DRIFT hits 3 -> Resync: skip a bar,     │
│  clear Drift, re-count.                 │
│ SWING token: push/lay-back on purpose   │
│  -> still clean + draw a card.          │
│                                         │
│ WIN story: reach JOY, >=1 Pulse left.   │
│ LOSE: Pulse hits 0.                     │
│ WIN set: 3 stories, 60->80->100 BPM.    │
└────────────────────────────────────────┘
```

---

## 6. Token manifest (24 pieces)

Use coins, beads, or print-and-cut chits. Suggested shapes/colors so they don't mix up:

| Qty | Token | Suggested piece | Purpose |
|----|-------|-----------------|---------|
| **7** | **Pulse** | red hearts / red discs | The band's life. Lose one per missed/doubled beat. Hit 0 = lose. |
| **12** | **Drift** | small gray cubes | Sloppy/strained play. At 3 in the pool → forced Resync (then discard all). |
| **3** | **Swing** | gold stars | Earned on clean Reaches plays; spend to push/lay-back + draw. |
| **1** | **Baton** | a distinct stick/long token w/ a 0–9 dial | Marks the conductor; the dial tracks `era` (starts at 1, +1 each handoff). |
| **1** | **Story Marker** | a pawn / bright disc | Sits on the current Story beat; advance to Joy to win. |

**Baton `era` dial:** glue a small d10 to a clip, or print a 10-segment wheel with an
arrow. Reset to **1** at the start of each story.

**Chit-cutting sheet (if printing tokens):** one A4/Letter sheet of 20 mm squares —
7 red, 12 gray, 3 gold, plus a 25 × 60 mm Baton strip and a 25 mm Story Marker disc.

---

## 7. Cut list (TL;DR for the printer)

```
SHEET A (gold)   : 6  Story Track cards
SHEET B (blue)   : 5  Character cards
SHEET C (gray)   : 8  Part cards   (2× Hi-hat, 2× Backbeat, 2× Lead, 2× Rim)
SHEET D–E (tint) : 32 Feeling cards (24 exact @4 each, 8 neighbor @2 each)
SHEET F          : 6  Reference cards (identical)
SHEET G (chits)  : 7 Pulse, 12 Drift, 3 Swing, 1 Baton strip, 1 Story Marker
-----------------------------------------------------------------
TOTAL            : 57 cards + 24 tokens
At 9 cards/sheet : 7 card sheets + 1 token sheet = 8 pages.
```

Provide your own **metronome** (phone app at 60/80/100 BPM) — that's the pulse source,
and the one component that can't be printed.

---

*Faces and counts derive from [Pulse.md](Pulse.md), which is wired to
[`RFCs/TTN-RFC-0010-Fleet-Pulse.md`](../RFCs/TTN-RFC-0010-Fleet-Pulse.md) (heartbeat,
conductor election, swing budget, beat_mask) and [`feelings_ttdb.md`](../feelings_ttdb.md)
(the Hero's Arc chart and the disposition nodes). See [IDEAS.md](IDEAS.md) for the full
game catalog.*
