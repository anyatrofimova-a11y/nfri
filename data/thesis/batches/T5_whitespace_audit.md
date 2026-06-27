# T5 — Whitespace evidence audit (enrichment batch)

**As of:** 2026-06-27

**Question:** Whitespace quadrant — genuine prep>exp optionality or assessed-heavy noise?

## Headline
- Whitespace entities: **32**
- thin_assessed: **13** (41%)
- mixed: **16** (50%)
- register_backed: **3** (9%)
- Mean measured sub-factor share (whitespace): **5%**

### L1 carriers (n=12)
- **register_backed**: Beazley (beazley), Aspen Insurance (aspen), Brit Insurance (brit)
- **mixed**: AXA XL (axa-xl), Munich Re (munich-re), Allianz Commercial (AGCS) (allianz-agcs), Canopius (canopius), Apollo Syndicate Management / Lloyd's Syndicate 1969 (apollo-1969), Inigo Insurance / Lloyd's Syndicate 1301 (inigo-1301), Atrium Underwriters / Lloyd's Syndicate 609 (atrium-609), Chaucer / Lloyd's Syndicate 1084 (chaucer-1084)
- **thin_assessed**: SCOR Syndicate 2015 (formerly The Channel Syndicate) (scor-2015)

## Measured % by quadrant

| Quadrant | n | mean measured % |
|----------|---|-----------------|
| earning_it | 27 | 2.6% |
| exposed | 31 | 1.9% |
| sidelined | 25 | 5.2% |
| whitespace | 32 | 5% |

## Method

- **measured_pct**: `provenance.evidence.measured_disclosed_subfactors / total_subfactors × 100`
- **cite_density**: unique source URLs per sub-factor (across exposure + preparedness inputs)
- **thin_assessed**: 0% measured, citation density < 0.4
- **mixed**: 10% measured OR assessed-heavy with ≥4 unique sources
- **register_backed**: ≥20% measured (≥2 disclosed/measured sub-factors)

## Verdict
Whitespace skews **assessed-heavy** (41% thin_assessed; mean 5% measured sub-factor share vs 5.2% sidelined). Only 3 entities (9%) reach register_backed status. High prep scores reflect underwriting *hypothesis* until GWP/trigger registers lift measured share — Beazley, Aspen and Brit are exceptions, not the modal whitespace profile.
