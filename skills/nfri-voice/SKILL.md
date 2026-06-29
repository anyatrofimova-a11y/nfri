---
name: nfri-voice
description: Match the NFRI whitepaper register when writing or editing any essay contract (contract/argument.json, analysis.json, findings.json, methodology.json, data.json) or any rendered prose. Use whenever drafting site copy, the thesis, or analysis. Encodes the target voice, the anti-patterns to avoid, and the conceptual frames the argument should deploy.
---

# NFRI voice & conceptual register

The full machine-readable spec is `contract/voice.json`; lint any essay against it with
`python3 harness/style_check.py` (all sections should pass). Style companions:
`contract/sequoia_thesis_style.json` (partnership-essay arc),
`contract/pirate_wires_style.json` (editorial backbone),
`contract/voice_guide.json` (working blend).

## Editorial backbone (Pirate Wires → NFRI)

Hold three domains in the same frame — **grid capacity × market structure × builder economics**
— the way a tech-politics-culture publication holds its triad. Shared thread: physical-world
builders carry bets the abstract layer cannot see; reindustrialisation runs on mispriced risk.

- **Scene before thesis** — curtailment notice, queue screen, bind moment; field-report energy
  without decorative first person.
- **Deck question** — headline argues; deck asks the hinge (`are we really pricing availability
  on this connection?`).
- **Discourse laundering** — name when damage BI stands in for availability cover.
- **Optimistic urgency** — the experiment can work if measurement precedes bind; not doom,
  not brochure.
- **Fire-take pulls** — one italic sentence between beats; load-bearing, no hedge.

## Voice — do
- Open each movement with a load-bearing claim or a concrete locus, never background.
- Organise the field with an explicit taxonomy before analysing it.
- Put a real company, number, or dated fact in the same sentence as each claim.
- State economics as a named mechanism or a back-of-envelope rule of thumb.
- Alternate short declarative thesis sentences with one longer sentence carrying the mechanism.
- Name civilizational stakes once per act — reindustrialisation requires honest cover.
- Name the strongest objection explicitly, then answer it.
- Close on a turn or reframe the reader could not have started with — who carries unrated
  availability.
- Gloss field jargon inline the first time (MGA, binder, non-firm, curtailment, expectile).

## Voice — avoid (these read as generic consulting/whitepaper filler)
Both-sides hedging; abstract nouns with no referent (synergies, value creation, holistic);
no-number paragraphs; passive throat-clearing openers ("In today's evolving landscape…");
grading adjectives doing a fact's job (robust, best-in-class, innovative); framework name-drops
with no application; naked fire takes without cite or PROVISIONAL; US-partisan or edgelord diction
on rendered site.

## Conceptual frames to deploy (anchor each to a citation in the registry)
why-now / structural tailwind · market incompleteness (the cover doesn't exist) ·
index = basis-risk-vs-timeliness tradeoff · rational demand under risk aversion ·
basis-risk-optimal (expectile) payout · the CRI / indicator construct ·
correlation substrate (what the risk correlates through) · compound loss (frequency × severity) ·
credibility-weighted fusion · the mispricing claim (observable rising cost vs flat rate) ·
discourse laundering (damage default for availability loss) · reindustrialisation stakes ·
wedge → distribution (the measurement is the moat).

## Discipline
- Content lives in `contract/*.json`; never hand-write prose into HTML.
- Every quantitative claim resolves to a `{{cite:KEY}}` (real registry entry) or a `{{fact:KEY}}`
  (live figure). No free-floating numbers.
- Do not name external authors, firms, or publications anywhere that renders to the site.
