# Toot Toot Games — Idea Catalog

Multiplayer card games and card-plus-token games built on the mechanics already
specified in this repo: the **Feelings TTDB** (an affective coordinate field with
typed edges and epistemic-weight tokens) and the **TTN / TTDB / A32 RFCs** (mesh
networking, reliable delivery, time-sync, fleet pulse, trust, dream-cycle,
narrative metamorphosis).

Players take **RPG-style characters** whose personalities are **dispositions drawn
from the Feelings TTDB** (Suspicion, Curiosity, Compassion, Hostility, Equanimity,
…). The characters must **cooperate to complete a shared story**, and in several
designs they must **evolve their own personal story** to supply the role the team
is currently missing.

## Why the repo is already a rulebook

| Repo artifact | Game mechanic it hands you |
|---|---|
| Feelings TTDB coordinate map (`feelings_ttdb.md`) | The **board**: lat = valence (N+/S−), lon = object (E other / W self), distance = intensity. |
| Typed edges (`resonates_with`, `can_deepen_into`, `intensifies_into`, `enables`, `can_become`) | The **combo / verb system** — what cards may legally chain to what. |
| `[ew]` epistemic-weight block (`conf`, `rev`, `sal`, `touched`) | **Four token tracks / dials** per belief card. |
| The Hero's Arc `ttdb-scene` (`@LAT88LON0`) | A ready-made **story track**: Serenity → Unease → Fear → Grief → Hope → Joy. |
| TTN-RFC-0007 Reliable Delivery (want_ack / ACK / backoff / dedup) | **Comms-puzzle** turn structure and token economy. |
| TTN-RFC-0010 Fleet Pulse (heartbeat, conductor election, swing) | **Real-time rhythm** loop and role rotation. |
| TTN-RFC-0005 Trust & Reputation | **Social deduction** scoring. |
| TTDB-RFC-0007 Dream Cycle (episodic→semantic, belief propagation) | **Deck-evolution** between rounds. |
| TTDB-RFC-0008 Narrative Metamorphosis (larva→imago, eclosion predicate) | **Legacy / character-growth** win condition. |

---

## The catalog (interesting → super fun)

### 🙂 1. Resonance — tableau-builder on the affective field
*Draws from: Feelings TTDB coordinate map + typed edges.*

The play mat **is** the affective globe. Each player is an RPG character holding a
hand of feeling-cards and plays them onto coordinates; a card only "lands" if it can
follow a real typed edge from a card already on the board
(`Serenity --can_deepen_into--> Joy`). Shared goal: draw an unbroken edge-path from an
opening node to the **Story node** in the corner. Teaches the graph by playing it.
Tokens are simple edge-markers. *Gentle, almost meditative.*

### 🙂 2. Reliable Delivery — cooperative comms-puzzle (cards + tokens)
*Draws from: TTN-RFC-0007 (want_ack / ACK / timeout+backoff / dedup), RFC-0006 LoRa framing.*

Players sit in a ring and may only pass face-down "packet" cards to neighbors — never
speak. Each packet carries a fragment of a story that must be reassembled **in order**
at the far end. Spend **ACK tokens** to confirm receipt; a missed ACK forces a
retransmit at a backoff cost. The tension is bandwidth: the story is bigger than the
channel, so the team must compress and sequence. *Quiet, clever, engineer's co-op.*

### 😮 3. Epistemic Weight — the dial-tracking co-op
*Draws from: TTDB-RFC-0005 (`[ew]`: conf / rev / sal / touched).*

Every character-belief card has four dials (or four token tracks): **confidence,
revision, salience, recency**. Story events let you *revise* a belief — but `rev`
ticks up and `touched` resets, while old untouched beliefs lose `sal` and fade off the
active board. Win by carrying a coherent shared belief-set to the climax with enough
total confidence. Makes "changing your mind costs something, and so does refusing to"
the core loop. *Genuinely novel — epistemic state as the resource.*

### 😮 4. Trust Mesh — semi-cooperative social deduction
*Draws from: TTN-RFC-0005 (trust/reputation) + RFC-0004 (semantic compression dictionary).*

Everyone cooperates to relay a story across the mesh, BUT one player holds a
**Hostility** disposition and is secretly corrupting packets. **Trust tokens** flow to
nodes whose relayed cards later prove consistent; the saboteur tries to stay above
suspicion while degrading the signal. Messages travel in a shared **token dictionary**
(compressed codewords), so miscommunication is plausibly deniable.
*Codenames-meets-Werewolf, cover story is literal packet loss.*

### 😄 5. Pulse — real-time rhythm co-op (cards + a shared heartbeat) ★ fleshed out
*Draws from: TTN-RFC-0010 Fleet Pulse (self-syncing ~1 Hz heartbeat, conductor
election, ±50 ms swing).*

A metronome sets the band's pulse. On each beat exactly one player lays the next
story-beat card — and the **conductor** role passes by the RFC's "first-up /
lowest-id-keeps / era-handoff" election. Drop a beat or double-play and the story
desyncs (lose a pulse token). Track the **Hero's Arc** together as the chart you drum
out. **Full design: [Pulse.md](Pulse.md).**

### 😄 6. The Hero's Arc — guided emotional relay
*Draws from: the `ttdb-scene` block at `@LAT88LON0`.*

Players own different characters but share **one** emotional journey through the six
canonical beats. On your turn, move the party's feeling-token along a legal edge toward
the next required beat — but you may only play feelings *your character* would
plausibly hold (the Hermit reaches Grief easily; the Trickster struggles to hold Hope).
Cooperation = handing the narrator role to whoever can carry the current emotion.

### 🤩 7. Metamorphosis — legacy co-op where your story evolves to serve the team
*Draws from: TTDB-RFC-0008 Narrative Metamorphosis (larva→imago, instar sequencing,
eclosion predicate) + RFC-0007 Dream Cycle (episodic→semantic, belief propagation) +
RFC-0009 push-back.*

Each player starts as a **larva** character with a thin backstory deck and a raw
disposition. You play rounds solving a shared story-crisis. Between rounds comes a
**Dream Cycle**: discard episodic event-cards and *consolidate* them into permanent
**belief cards** sewn into your own deck — literally rewriting your character's story.
The cooperative engine: your personal **eclosion predicate** (larva→imago condition)
is satisfiable only by adopting beliefs the *team* needs now — a Suspicion character
keeping the group safe must eventually metamorphose into a Trust-keeper for the final
act to clear. You can refuse to grow and stay safe, but the story can't be completed
unless enough players eclose into the missing roles. Beliefs propagate between players,
so one person's growth seeds another's. The evolved deck **carries to the next
session** (legacy). *Character growth isn't flavor — it's the win condition.*

---

## Cross-cutting design notes

- **Tokens you already have for free:** `conf/rev/sal/touched` dials, ACK tokens,
  trust tokens, pulse tokens, edge-markers. The `[ew]` block is a token economy waiting
  to happen.
- **The board exists:** the lat/lon affective field is a printable hex/grid map; the
  NE–SW valence diagonal is the scoring axis.
- **Edges are the whole rules engine:** `resonates_with` (free combo),
  `can_deepen_into` / `intensifies_into` (escalate), `enables` (disposition→intent
  unlock), `can_become` (transform). Enough verbs for a full card game.

## Character roster seed (dispositions as classes)

Pull RPG archetypes straight from the Feelings TTDB disposition/intent nodes:

| Character | Disposition (node) | Reaches easily | Struggles to hold |
|---|---|---|---|
| The Seeker | Curiosity `@LAT10LON40` | Hope, To Explore | Equanimity |
| The Warden | Suspicion `@LAT-20LON-30` | Fear, To Avoid | Openness |
| The Healer | Compassion `@LAT30LON40` | Gratitude, To Nurture | Contempt |
| The Giver | Generosity `@LAT40LON20` | Joy, To Connect | Withdrawal |
| The Hermit | Equanimity `@LAT30LON-20` | Serenity, Grief (held calmly) | Excitement |
| The Trickster | Indifference `@LAT-10LON-40` | Frustration, To Withdraw | Hope, Compassion |

Each character's "reaches / struggles" list is just which edges of the affective field
they can traverse cheaply vs. at a cost — the source of forced cooperation.
