# Pulse — a real-time rhythm co-op

> **Share the tempo, glance at the conductor.** A band of RPG characters must drum out
> a shared emotional story on a living heartbeat — staying inside the swing envelope,
> handing off the baton when someone falters, never missing a beat.

Pulse turns **TTN-RFC-0010 (Fleet Pulse)** into a tabletop game. The RFC's robots keep
a ~1 Hz heartbeat in tight phase *without messaging every beat*; Pulse asks 2–5 players
to do the same with their hands and a metronome. The "chart" they play is the **Hero's
Arc** from `feelings_ttdb.md` (`@LAT88LON0`): Serenity → Unease → Fear → Grief → Hope →
Joy. Complete the arc as a band, in time, and you win.

- **Players:** 2–5
- **Length:** 15–25 min per story (a "set" is 3 stories)
- **Feel:** party-game tension of real-time timing, with a quiet emotional payoff
- **You need:** the card deck below, the token bag below, and **a pulse source** — a
  phone metronome, a clapping app, or one player as the human click track.

---

## 1. The core idea (straight from the RFC)

In Fleet Pulse, **the beat is computed, not received** — every node derives the grid
from a shared clock and only "glances at the conductor" occasionally to trim drift.
Pulse keeps that spirit:

| RFC concept (TTN-RFC-0010) | Pulse rule |
|---|---|
| Shared pulse clock, ~1 Hz | A metronome everyone hears. The **bar** = 4 beats. |
| Beat is *computed*, wire carries the *chart* not the *click* | Players must play **on** the beat from their own internal count, not wait to be told. |
| **Conductor**: first-up starts it, keeps it; id breaks ties; `era` on handoff | One player holds the **Baton**. They set the bar's required beat and call the count-in. The Baton passes on failure, `era` ticks up. |
| **±50 ms swing budget** (drift_reserve vs. musical swing) | The timing window for a "clean" play. Hitting dead-center is fine; the band *wants* a little human swing, but too early/late = **drift**. |
| **`beat_mask`** — each part plays on specific beats of the bar | Each character has a **Part card**: which beat(s) of the 4-beat bar they're responsible for. |
| **On-join fast-lock** (extra beacon when a node arrives) | A new/returning player gets a free **count-in** to lock back in. |
| **Resync pacing** — correct only as drift demands | **Drift tokens** accumulate; you only stop to "resync" (spend a turn) when they pile up. |
| **Graceful degradation** — lose conductor, free-run on last chart | If the Baton-holder busts, the band keeps the beat for one bar while the baton hands off. No instant game-over. |

The whole game is the RFC's slogan made physical: **you cannot succeed by reacting to
each beat — you must hold the tempo internally and only look up when drift forces it.**

---

## 2. Components

### 2.1 The Story Track (the chart)
A 6-card strip laid face-up in the center — the Hero's Arc beats, in order:

1. **Serenity** `@LAT10LON-10`
2. **Unease** `@LAT-10LON-10`
3. **Fear** `@LAT-30LON20`
4. **Grief** `@LAT-30LON-30`
5. **Hope** `@LAT20LON20`
6. **Joy** `@LAT30LON30`

A shared **Story Marker** sits on the current beat. Advancing it to **Joy** wins.

### 2.2 Character cards (dispositions as classes)
Each player draws one RPG character. The card lists a **disposition** and a
**reaches / strains** pair drawn from the Feelings TTDB edges:

| Character | Disposition node | Reaches (play for −1 cost) | Strains (costs +1 Drift to play) |
|---|---|---|---|
| The Seeker | Curiosity `@LAT10LON40` | Unease, Hope | Grief |
| The Warden | Suspicion `@LAT-20LON-30` | Fear, Grief | Joy |
| The Healer | Compassion `@LAT30LON40` | Hope, Joy | Fear |
| The Hermit | Equanimity `@LAT30LON-20` | Serenity, Grief | Hope |
| The Trickster | Indifference `@LAT-10LON-40` | Fear, Unease | Joy, Hope |

> **Why this forces cooperation:** no single character can carry all six beats cheaply.
> The Warden powers through Fear and Grief but chokes on Joy; the Healer lands Hope and
> Joy but strains at Fear. The band has to route each beat to whoever *reaches* it —
> and hand off the Baton accordingly.

### 2.3 Part cards (the `beat_mask`)
Dealt one per player at the start of each story. Your Part says which beat(s) of the
4-beat bar are **yours to play**:

| Part | `beat_mask` | Role (RFC §7.1 voicing) |
|---|---|---|
| Hi-hat | beats 1·2·3·4 | timekeeper — plays every bar, the band's spine |
| Lead | beat 1 (downbeat) | sounds the story-beat advance |
| Backbeat | beats 2 & 4 | the groove; covers the conductor on handoff |
| Rim | beat 3 | the offbeat accent |

With 2–3 players, combine masks so every beat of the bar is covered by someone.

### 2.4 Feeling cards (your hand)
A shared draw deck of Feeling cards matching the six arc emotions (plus near-neighbors
from the field: Contentment, Melancholy, Frustration, Excitement…). You hold **3**.

### 2.5 Tokens
- **Pulse tokens** ×7 (shared) — the band's "life." Lose one on a missed/doubled beat.
- **Drift tokens** (shared pool) — accumulate from sloppy or strained plays; too many
  forces a **Resync**.
- **The Baton** ×1 — marks the conductor. Has an **`era` dial** (a d10 or a counter),
  starts at 1, ticks up on every handoff.
- **Swing tokens** ×3 (shared) — earned by clean play, spent to "swing" (see §4.4).

---

## 3. Setup

1. Lay the **Story Track** (6 beats), Story Marker on **Serenity**.
2. Each player draws a **Character** and a **Part** card, and **3 Feeling cards**.
3. Put **7 Pulse tokens** in the center, the Drift pool empty, **3 Swing tokens** aside.
4. **First-up is conductor (RFC §3.1):** whoever most recently kept a beat (drummed,
   tapped, hummed) takes the **Baton**, `era = 1`. Ties break to the youngest player
   (your "lowest-id" rule — pick any deterministic tie-break and keep it all game).
5. Start the metronome at a **gentle tempo** (≈ 60 BPM, one beat per second). You can
   speed up between stories.

---

## 4. How a bar works

A **bar** is 4 metronome beats. Everything happens in time with the click.

### 4.1 Count-in (the Baton-holder's job)
On beat **4** of the previous bar, the conductor calls the **required emotion** for the
next bar — it must be the Story Marker's **current** beat or the **next** one on the
track (you can only advance by a legal edge). This is the conductor "announcing the
chart."

### 4.2 Playing your beat
When *your* beat (per your Part's `beat_mask`) comes around, you must **lay a Feeling
card face-up onto the Story Track** in time with the click:

- **On time** (within the swing window — i.e. on the click, give or take a hair): clean.
- **A legal card** = a Feeling that matches the required emotion **or** sits on a typed
  edge toward it (`resonates_with`, `can_deepen_into`, `intensifies_into`).
- Play a card your character **Reaches**: no cost (and you may take a **Swing token** if
  the play was clean).
- Play a card your character **Strains**: add **+1 Drift** to the pool (you did it, but
  it cost the band tightness).

### 4.3 What goes wrong (lose a Pulse token)
- **Missed beat** — your beat passed and you played nothing, or played late/early enough
  to be off the click: **−1 Pulse token**, **+1 Drift**.
- **Doubled beat** — two players play on the same beat (collision): **−1 Pulse token**.
  (The RFC's `(src,seq)` dedup, dramatized: two nodes can't own the same slot.)
- **Illegal advance** — a card that doesn't reach the required emotion: doesn't count;
  the beat is treated as missed.

### 4.4 Swing (the ±50 ms is *feel*, not slop — RFC §6)
Spend a **Swing token** to deliberately **lay back or push** a play — land it a touch
late (relaxed) or early (urgent) **on purpose** and still count it clean, *and* draw an
extra Feeling card. This is the RFC's point that the tolerance is "expressive headroom,
not uncorrected error": good bands use the window, they don't just survive it.

### 4.5 Advancing the story
At the end of a bar, if the **downbeat (Lead) play** legally matched the required
emotion, move the **Story Marker** forward one beat on the arc. Reach **Joy** = the band
wins the story.

---

## 5. Conductor handoff (the heart of the game)

This is the RFC's election model (§3) turned into the cooperative engine.

- **Trigger a handoff** when the conductor's own beat **busts** (missed/illegal on the
  beat they were responsible for), **or** voluntarily when the next required emotion is
  one the conductor **Strains** but a teammate **Reaches**.
- **Graceful degradation (RFC §3.4):** the band does **not** stop. The **Backbeat**
  part holds the next bar's groove (free-run on the last chart) while the baton moves.
- **Who takes it:** the new conductor must be someone who **Reaches** the upcoming
  emotion. Among eligible players, lowest-id (your fixed tie-break) takes the baton.
- **`era` ticks up.** Increment the Baton's era dial. A higher era "wins" — so a player
  who busted out can't immediately grab the baton back (no flapping, RFC §3.4).
- **On-join fast-lock (RFC §4.2):** the new conductor gets a **free count-in bar** to
  settle before play resumes — the band glances at the new timekeeper.

> The story literally cannot finish unless the baton travels to the right character for
> each emotional beat. The Warden carries you through **Fear** and **Grief**; you *must*
> hand off to the Healer or Seeker to land **Hope**, and to the Healer for **Joy**. The
> band's job is to route the conductor role around the arc.

---

## 6. Resync (paced by drift, not by tempo — RFC §5)

You don't stop every bar to tidy up — only when drift threatens the swing budget.

- When the **Drift pool reaches 3**, the band must **Resync** at the top of the next
  bar: skip one bar of story advancement, discard all Drift tokens, and the conductor
  re-calls the count. The metronome keeps running — you just spend a bar re-tightening.
- A Resync **costs no Pulse token** (it's maintenance, not failure) but it costs
  *tempo*: you lose ground on a timed set (see §8).
- This mirrors the RFC's "correct only as often as drift demands": the band that plays
  cleanly (mostly **Reaches** plays, good handoffs) almost never resyncs; a band
  forcing **Strains** plays resyncs constantly and runs out the clock.

---

## 7. Winning and losing

- **Win the story:** advance the Story Marker to **Joy** with at least one Pulse token
  left.
- **Lose the story:** Pulse tokens hit **0** — the band fell apart; the heartbeat
  stopped.
- **Win the set:** complete **3 stories**, raising the tempo each time (60 → 80 → 100
  BPM). The band that holds the groove as it gets faster has truly locked in.

---

## 8. Variants & scaling

- **Solo / 2-player:** one player covers two Parts (combine `beat_mask`s); the Baton
  still passes between *characters* you hold.
- **Timed set (advanced):** put a 3-minute timer on each story. Every Resync burns
  table time — now the RFC's "tight band, idle wire" becomes "tight band, time to
  spare." A sloppy band beats the clock with no margin.
- **Conductor-loss drill (RFC §10 test 5):** once per set the active player may "power
  off" — sit out a bar without warning. The band must hand the baton off mid-bar and
  keep the beat. Survive it for a bonus Swing token.
- **Adaptive tempo:** if the band clears two bars with zero Drift, the conductor *may*
  nudge the metronome up a notch — the RFC's optional adaptive pacing (§5).
- **Full Metamorphosis crossover:** carry your Character's evolved hand into a game of
  [Metamorphosis](IDEAS.md#-7-metamorphosis--legacy-co-op-where-your-story-evolves-to-serve-the-team)
  — the emotions you learned to *Reach* in Pulse become beliefs you can consolidate.

---

## 9. Quick reference card

```
A BAR = 4 metronome beats.   YOUR BEAT = your Part's beat_mask.

ON YOUR BEAT, in time with the click:
  play a Feeling card that REACHES/EDGES the required emotion.
    Reaches  -> clean, take a Swing token
    Strains  -> +1 Drift
  miss / late / illegal -> -1 Pulse, +1 Drift
  two players same beat -> -1 Pulse (collision)

CONDUCTOR (Baton): calls next emotion on beat 4; must Reach it.
  busts or strains -> hand baton to someone who Reaches it; era +1;
                      Backbeat holds the groove; new conductor gets a free count-in.

DRIFT hits 3 -> Resync: skip a bar, clear Drift, re-count.

SWING token: spend to push/lay-back a play on purpose -> still clean + draw a card.

WIN story: reach JOY with >=1 Pulse left.   LOSE: Pulse hits 0.
WIN set: 3 stories, tempo 60 -> 80 -> 100 BPM.
```

---

*Source mechanics: `RFCs/TTN-RFC-0010-Fleet-Pulse.md` (heartbeat, conductor election,
swing budget, beat_mask parts, resync pacing) and `feelings_ttdb.md` (the Hero's Arc
chart `@LAT88LON0`, dispositions, typed edges). See [IDEAS.md](IDEAS.md) for the full
game catalog.*
