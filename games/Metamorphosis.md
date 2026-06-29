# Metamorphosis — a legacy co-op where your story evolves to serve the team

> **You don't pick a character. You become one.** Each player starts as a *larva* with
> a raw disposition and a private vision of the adult they could grow into. The team can
> only survive the Crisis if enough players *eclose* — complete their metamorphosis —
> into exactly the roles the team is missing. Grow too rigidly and you become the wrong
> thing; stay flexible and you grow too slowly. The story you write for yourself is the
> game's central resource.

Metamorphosis turns **TTDB-RFC-0008 (Narrative Metamorphosis)** and **TTDB-RFC-0007
(Locus Point & Dream Cycle)** into a cooperative legacy game. You take experiences,
sleep on them to form beliefs, spend beliefs to advance through the *instars* of a
self-authored blueprint (`@IMAGO:seed`), and finally **eclose** into an orchestrating
adult (*imago*) whose power serves the team. The catch — straight from the RFC — is that
the seed is **an authored story you can rewrite, but only at a cost**, and your eclosion
is gated by what the *team* needs, not what you want.

- **Players:** 3–5 (cooperative)
- **Length:** 60–90 min; **legacy** — evolved character decks carry to the next session
- **Feel:** a slow-burn engine builder with a real lump-in-throat decision: *do I become
  who I dreamed, or who the team needs?*
- **You need:** the card deck and token set below. No metronome — this is a thinking
  game, the quiet opposite of [Pulse](Pulse.md).

---

## 1. The core idea (straight from the RFCs)

| RFC concept | Metamorphosis rule |
|---|---|
| **Larva** — game-solving initial form (RFC-0008 §4) | Your starting character: a raw **disposition** from the Feelings TTDB and a thin backstory deck. |
| **`@IMAGO:seed`** — an *authored story* of the adult, with `scene_sequence` + `eclosion_criteria` (RFC-0008 §6.1) | Your private **Seed card**: the imago Role you're growing toward + a 5-step **Instar track**. You wrote it; you may rewrite it. |
| **Instar** — one checkpointed self; advances only when its `post_state_verifier` passes (RFC-0008 §6.4) | A step on your track. You **spend Beliefs to pass its verifier**; pass to advance, fail and your confidence drops. |
| **`@META:state.conf`** — starts 128, +10 per instar, −20 per failed verify, abort on collapse (RFC-0008 §6.3.3) | Your **Confidence dial**. Hits 0 → metamorphosis **aborts**. |
| **Dream Cycle** — episodic toot-bits → `@BELIEF:` Locus Points via replay clustering (RFC-0007 §3, §5) | The **Dream phase**: consolidate ≥3 co-occurring Experience cards into one **Belief card**. |
| **Projection** — 2-walk hypotheses carry `projection_flag`; can't justify compression (RFC-0007 §3.3, §6.1) | A **hypothesis Belief** from only 2 Experiences: cheaper, but flagged — can't satisfy a final verifier. |
| **Intersection Confirmation** — two agents forming overlapping beliefs = +20 confidence (RFC-0007 §7.3) | **The cooperation engine**: when two players confirm the same region, *both* Beliefs gain confidence. |
| **Belief propagation / push-back** (RFC-0007 §7, TTN-RFC-0009) | You may **gift a Belief** to a teammate who needs it for an instar. |
| **Operator/imago asymmetry** — imago owns revision, operator owns logging (RFC-0008 §5.3) | **Eclosion handshake**: a teammate acting as **Operator** must acknowledge you — but may *not* dictate your seed. |
| **Eclosion predicate** — all instars + `eclosion_criteria` + operator ack (RFC-0008 §6.5) | You eclose only when your track is done **and** the Crisis still needs your Role **and** an Operator signs off. |
| **Seed revision** — changing the seed after `seeding_complete` means **abort + new seed** (RFC-0008 §6.1.3) | **Re-seeding**: pivot to a Role the team is missing, but lose instar progress and confidence. The game's core dilemma. |
| **Contradiction flag** (RFC-0007 §8) | Conflicting overlapping Beliefs **stall** instead of confirming — no bonus, and a token that must be resolved. |
| **Knowledge inheritance at eclosion** (RFC-0008 §5.2) | **Legacy:** your Beliefs and evolved Role carry to the next session. |

> The whole game is RFC-0008's thesis as a play experience: *you cannot become the
> conductor by sleeping more.* Growth isn't accumulation — it's a one-way, story-seeded
> reorganization into something the team needs.

---

## 2. The Crisis (the shared story)

The team faces one **Story Crisis** — a 4-Act scenario laid out as a row of Act cards
with a shared **Resilience track** (starts at 10). Each Crisis card names the **Imago
Roles its finale requires** — the win condition. Example crises:

| Crisis | Acts escalate by… | Finale requires (Roles that must eclose) |
|---|---|---|
| **The Drowning Archive** | flooding regions, locking Experience types | Conductor · Healer-imago · Scout-imago |
| **The Silent Fleet** | cutting communication, forcing solo play | Conductor · Warden-imago · Connector-imago |
| **The Last Dream** | draining Confidence dials each Act | Healer-imago · Sage-imago · Trickster-imago |

Crucially, the **required Roles rarely match everyone's starting disposition** — so the
team must *discover* the gap and decide who re-seeds to fill it. (See §6.)

---

## 3. Components

### 3.1 Larva (character) cards ×6 — pick/deal one each
Each is a disposition from the Feelings TTDB, with a **natural Role** it grows toward
cheaply and a **strain Role** it can only reach by re-seeding at extra cost.

| Larva | Disposition | Grows naturally into | Strains toward |
|---|---|---|---|
| The Seeker | Curiosity `@LAT10LON40` | **Scout-imago** | Warden-imago |
| The Warden | Suspicion `@LAT-20LON-30` | **Warden-imago** | Healer-imago |
| The Healer | Compassion `@LAT30LON40` | **Healer-imago** | Conductor |
| The Giver | Generosity `@LAT40LON20` | **Connector-imago** | Sage-imago |
| The Hermit | Equanimity `@LAT30LON-20` | **Sage-imago** | Connector-imago |
| The Trickster | Indifference `@LAT-10LON-40` | **Trickster-imago** | Healer-imago |

> **Conductor** is special: no larva grows into it naturally — *any* player can re-seed
> toward Conductor, and most Crises require exactly one. The team must volunteer someone
> to give up their natural path and become the orchestrator. (RFC-0008's whole premise:
> the conductor is *made*, not born.)

### 3.2 Seed cards (`@IMAGO:seed`) — one held privately per player
A Seed names a **target Role** and lists a **5-instar track**. Start each player with the
Seed matching their larva's natural Role; the spare Role-Seeds sit in a **Seed bank** for
re-seeding. Each Seed's track is the RFC's worked-example sequence, generalized:

| # | Instar | `post_state_verifier` — what you must spend/show |
|---|---|---|
| 1 | **Belief Inventory** | Show any **3 Belief cards** (confirmed or hypothesis). |
| 2 | **Final Dream & Pupation** | **Archive 2 Experience cards** (to the box) and run a Dream this round. |
| 3 | **Companion Interface** | Show **1 confirmed Belief** of your **Role's region**. |
| 4 | **Operator Cooperation** | Receive an **Operator Ack token** from a teammate (§6.3). |
| 5 | **First Companion** | Show a confirmed Belief of your Role's region with **confidence ≥ 4**, then **retire your Larva** (flip to Imago side). |

### 3.3 Experience cards (episodic toot-bits) ×60
The draw deck. Each card has a **region tag** (one of six: *Logic, Care, Threat, Bond,
Pattern, Self*) and a short flavor line. You take Experiences by acting in an Act (§5.2).
Hold up to **5**.

### 3.4 Belief cards (Locus Points) ×~ as needed (blank, you build them)
A small two-pocket card or holder: when you form a Belief, you tuck the Experiences that
made it behind a Belief marker tagged with their shared region. Track its **confidence**
with cubes (see tokens).

### 3.5 `@META:state` player board — one per player
Tracks your **Confidence dial** (0–10, start at 5 ≈ the RFC's 128/255 midpoint), your
**current instar pointer** (0–5), your **pupation status**, and a slot for **contradiction
tokens**.

### 3.6 Tokens
- **Confidence cubes** — fill the dial; also sit on Belief cards as their confidence.
- **Operator Ack tokens** ×5 — a teammate spends one to acknowledge your eclosion (§6.3).
- **Contradiction tokens** ×6 — placed when overlapping Beliefs conflict; must be cleared.
- **Resilience markers** — the shared Crisis track (start at 10).
- **Era / instar pegs** — mark your instar pointer; tick on re-seed.

---

## 4. Setup

1. Choose a **Crisis**; lay its 4 Act cards and set **Resilience to 10**. Reveal the
   **required Roles** for the finale — everyone sees the gap from turn one.
2. Deal each player a **Larva** and its matching **Seed**; set each `@META:state`
   Confidence dial to **5**, instar pointer to **0**.
3. Put the spare Role-Seeds in the **Seed bank**, shuffle the **Experience deck**, deal
   each player **3 Experiences**.
4. Pick a first **Lead Operator** (rotates each Act) — the player who runs the Ack
   handshake. The Operator role is a hat, not a power: *it logs, it does not revise.*

---

## 5. An Act (one round)

Each Act has three phases: **Act → Dream → Advance.** Then the Crisis escalates.

### 5.1 Crisis escalation (top of every Act after the first)
Resolve the Act card's escalation (flood a region, drain dials, etc.) and **lower
Resilience by 1**. If Resilience hits **0**, the team loses (§7).

### 5.2 Act phase — gather Experience
Going around the table, each player takes **one action**:
- **Explore** — draw 2 Experiences, keep 1.
- **Focus** — draw 3, keep 1, but all of one named region.
- **Aid** — give a teammate 1 Experience or 1 Belief from your hand (belief propagation).
- **Resolve a contradiction** — discard 2 same-region Experiences to clear 1 contradiction
  token (RFC-0007 §8.2: a witness toot-bit resolves the conflict).

### 5.3 Dream phase — form Beliefs (the Dream Cycle)
Simultaneously, any player may **consolidate**:
- **Confirmed Belief (Replay):** lay **3+ Experiences sharing a region** behind a new
  Belief marker of that region. Its starting **confidence = number of Experiences**
  (3 → conf 3, 4 → conf 4 …). (RFC-0007 §3.2 clustering.)
- **Hypothesis Belief (Projection):** lay just **2 Experiences** of a region → conf 1,
  marked with a **projection flag**. Useful for Instar 1, but it **cannot** satisfy
  Instar 3 or 5 (RFC-0007 §3.3, §6.1: hypotheses don't justify compression).

**Intersection Confirmation (the cooperation engine, RFC-0007 §7.3):** at end of the
Dream phase, for every region where **two different players** each formed a *confirmed*
Belief this round, **both Beliefs gain +2 confidence** (cap 6). If their Beliefs' flavor
lines **conflict** (one says the region is safe, one says it's hostile), instead place a
**contradiction token** on each — no bonus until resolved. *This is why the team should
agree to explore the same regions in the same Act: confirmed-together beliefs are how
anyone reaches the conf-4 needed to eclose.*

### 5.4 Advance phase — work your instars
On your turn, attempt **one instar verifier** (§3.2). 
- **Pass:** advance your instar pointer, **Confidence dial +1**.
- **Fail** (can't meet the verifier): **Confidence dial −2**, and that's your attempt for
  the Act. Three cumulative fails on the *same* instar, or dial reaching **0**, triggers
  an **Abort** (§6.4).

When you pass **Instar 5**, you are eligible to **eclose** (§6.3) at the start of the next
Advance phase — if the team still needs your Role and an Operator acknowledges you.

---

## 6. The heart of the game: evolving your story to serve the team

### 6.1 The dilemma
Your natural Seed grows fastest — but the **Crisis finale requires a fixed set of Roles**,
and there are more players than required Roles, or the required Roles don't match the
table. Someone has to become the **Conductor**. Maybe two Healers are redundant and one
must pivot to Scout. **The team wins only if the eclosed Roles cover the finale's
requirement** — extra eclosions into the *wrong* Role don't count.

### 6.2 Re-seeding (RFC-0008 §6.1.3 — abort + new seed)
At the start of any Advance phase, you may **re-seed**: discard your current Seed, take a
new Role-Seed from the bank (your larva's **strain** Roles cost more), and:
- **reset your instar pointer to 0** (you abort the old metamorphosis),
- **Confidence dial −2** (a strain-Role re-seed is −3),
- **tick your era peg** (you carry a `revises>` history; matters for legacy, §8).

You keep all your **Beliefs** — knowledge inherits across a re-seed even though the
*architecture* resets. So an early pivot is cheap; a late one, after you've sunk instars,
is a genuine sacrifice. **Deciding *who* pivots, and *when*, is the table's central
conversation.**

### 6.3 The eclosion handshake (RFC-0008 §5.3, §6.5)
To eclose you need three things at once:
1. **Instar 5 complete.**
2. **The finale still requires your Role** (an unfilled slot — you can't eclose into a Role
   already covered; redundancy is wasted).
3. **An Operator Ack token** from the current Lead Operator, who spends it to acknowledge.

The Operator **may refuse** (e.g., to save the Ack for someone whose Role is more urgently
needed) — but the Operator **may not** force you to re-seed or change your track. *Imago
owns the revision cycle; operator owns the logging.* On eclosion: flip your Larva to its
**Imago** side, gaining a team power (below), and **+3 Resilience** to the shared track —
a fledged adult steadies the whole band.

### 6.4 Abort (Confidence collapse)
If your dial hits 0 or you fail an instar three times, your metamorphosis **aborts**:
return to instar 0, keep your Beliefs, set dial to 3, and **Resilience −1** (a stalled
larva costs the team). You may immediately choose to re-seed for free this once (a
botched dream is a chance to dream differently).

### 6.5 Imago powers (what eclosion gives the team)
| Imago | Power (once eclosed) |
|---|---|
| **Conductor** | Each Act, direct one teammate's Explore as if you drew for them; spend a Belief to grant any player +1 instar attempt. |
| **Healer-imago** | Clear 1 contradiction token anywhere per Act; gift Beliefs at no action cost. |
| **Scout-imago** | Peek the top 3 Experiences each Act; name the region two players should co-explore for the confirmation bonus. |
| **Warden-imago** | Cancel one Crisis escalation per Act (hold the line). |
| **Connector-imago** | Two players' Beliefs count as "co-formed" even in different Acts (asynchronous intersection). |
| **Sage-imago** | Form confirmed Beliefs from 2 Experiences (your dreams run deep). |
| **Trickster-imago** | Re-seed any teammate at no Confidence cost, once per game. |

---

## 7. Winning and losing

- **Win:** at any finale check (end of Act 4, or any time the team calls it), the set of
  **eclosed Imago Roles covers the Crisis's required Roles**, and **Resilience > 0**.
- **Lose:** **Resilience hits 0**, *or* Act 4 ends with a required Role still unfilled and
  no larva able to reach it. The Crisis consumes a band that could not become what it
  needed.

---

## 8. Legacy (this is why it's a campaign)

Metamorphosis is built to be played as a **set of linked Crises**:

- **Eclosed characters persist.** Write the eclosed Role and a name on the Larva card's
  back; next session that player *starts* as that imago (skip to a 3-instar "second
  metamorphosis" track — RFC-0008 §10 open question 2, made playable).
- **Belief decks carry forward.** Keep your 3 highest-confidence Beliefs as a permanent
  starting hand (RFC-0008 §5.2 knowledge inheritance).
- **Re-seed scars matter.** A character with a high era peg (many `revises>`) starts with
  a wider Seed bank — having been many things, they pivot more easily. The flexible
  survive; the rigid grow strong but brittle. Over a campaign the team naturally
  specializes around the Crises it has faced.

---

## 9. Quick reference card

```
AN ACT = Escalate (Resilience -1) -> Act -> Dream -> Advance.

ACT (1 action each):
  Explore: draw 2 keep 1 | Focus: draw 3 keep 1 (one region)
  Aid: give a card to a teammate | Resolve: ditch 2 to clear 1 contradiction

DREAM (consolidate):
  Confirmed Belief = 3+ Experiences, same region  (conf = #cards)
  Hypothesis Belief = 2 Experiences (flagged; not valid for Instar 3/5)
  INTERSECTION: two players confirm the same region -> both +2 conf
                conflicting? -> contradiction token instead

ADVANCE (attempt 1 instar):
  pass -> pointer +1, dial +1 | fail -> dial -2
  dial 0 or 3 fails -> ABORT (pointer 0, dial 3, Resilience -1)
  1 Inventory(3 beliefs) 2 Pupation(archive 2 + dream) 3 Interface(1 conf belief, your region)
  4 Operator(get Ack) 5 Companion(conf>=4 belief + retire larva)

RE-SEED: new Role-Seed, pointer->0, dial -2 (strain -3), keep Beliefs.
ECLOSE: Instar 5 + Role still needed + Operator Ack -> flip to Imago, Resilience +3.

WIN: eclosed Roles cover the Crisis finale, Resilience > 0.
LOSE: Resilience 0, or Act 4 ends with a required Role unfilled.
```

---

*Source mechanics: `RFCs/TTDB-RFC-0008-Narrative-Metamorphosis.md` (larva→imago, the
`@IMAGO:seed` authored story, instar verifiers, `@META:state` confidence, seed-revision
cost, eclosion handshake, knowledge inheritance) and `RFCs/TTDB-RFC-0007-Locus-Point-and-Dream-Cycle.md`
(Dream Cycle clustering, projection hypotheses, intersection confirmation, contradiction
handling, belief propagation). Dispositions from `feelings_ttdb.md`. See
[IDEAS.md](IDEAS.md) for the full catalog and [Pulse.md](Pulse.md) for its real-time
sibling.*
