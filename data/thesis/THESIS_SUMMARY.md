# NFRI thesis research — 2026-06-27

# T1 — Measurement lift (disclosed GWP → book_concentration)

**Question:** How much does MoS move when we replace assessed book with disclosed energy/power GWP?

**Method:** Fixed median cut-lines (exp≥56.2, prep≥61.2). Per L1 carrier with `evidence_tier=disclosed` on book_concentration, rescore with book reverted to latent-only anchor.

## Headline
- Carriers with disclosed book: **22**
- Mean ΔMoS (disclosed − assessed-book): **8.52**
- Median ΔMoS: **7.5**
- Quadrant flips: **5**

## Interpretation
Negative ΔMoS means disclosed GWP **lowers** exposure vs research anchor (carrier looks less concentrated). Positive ΔMoS means disclosed share **raises** exposure vs latent guess.

## Top movers
- **Brit Insurance** (0.8% share): assessed=3 disclosed=0 ΔMoS +22.5, ΔExp -22.5
- **AXIS Capital / Lloyd's Syndicate 1686 (and Energy Transition Syndicate 2050)** (0.7% share): assessed=3 disclosed=0 ΔMoS +22.5, ΔExp -22.5 — quad whitespace→earning_it
- **Liberty Specialty Markets** (0.3% share): assessed=2 disclosed=0 ΔMoS +15.0, ΔExp -15.0
- **Aspen Insurance** (4.8% share): assessed=3 disclosed=1 ΔMoS +15.0, ΔExp -15.0
- **Markel International** (4.9% share): assessed=3 disclosed=1 ΔMoS +15.0, ΔExp -15.0
- **AEGIS London / Lloyd's Syndicate 1225** (2.4% share): assessed=3 disclosed=1 ΔMoS +15.0, ΔExp -15.0 — quad whitespace→earning_it
- **Chaucer / Lloyd's Syndicate 1084** (0.9% share): assessed=2 disclosed=0 ΔMoS +15.0, ΔExp -15.0
- **Allied World / Lloyd's Syndicate 2232** (0.9% share): assessed=2 disclosed=0 ΔMoS +15.0, ΔExp -15.0 — quad sidelined→exposed
- **Beazley** (1.7% share): assessed=1 disclosed=0 ΔMoS +7.6, ΔExp -7.6
- **Hiscox London Market** (17.5% share): assessed=2 disclosed=3 ΔMoS -7.5, ΔExp +7.5 — quad exposed→sidelined
- **AXA XL** (2.0% share): assessed=2 disclosed=1 ΔMoS +7.5, ΔExp -7.5
- **Chubb** (0.1% share): assessed=1 disclosed=0 ΔMoS +7.5, ΔExp -7.5

---

# T2 — Trigger gap (parametric vs indemnity)

**Question:** Which L1 carriers close the non-damage basis-risk gap?

**Rule:** `trigger_gap` ≤2 = partial/full match; ≥3 = legacy physical-damage reliance. `n_nondamage_products` from `trigger_inputs.json` where disclosed.

## Headline
- L1 carriers: **39**
- Close gap (trigger≤2): **9** — Beazley, AXA, Munich, Allianz, Liberty, Chaucer, SCOR, Sompo…
- Wide gap (trigger≥3): **30**

## Closers (parametric/availability evidenced)
- Beazley: trigger_gap=2, product_fit=3, n_products=2
- AXA XL: trigger_gap=2, product_fit=3, n_products=2
- Munich Re: trigger_gap=0, product_fit=4, n_products=4
- Allianz Commercial (AGCS): trigger_gap=2, product_fit=3, n_products=2
- Liberty Specialty Markets: trigger_gap=2, product_fit=1, n_products=2
- Chaucer / Lloyd's Syndicate 1084: trigger_gap=1, product_fit=3, n_products=None
- SCOR Syndicate 2015 (formerly The Channel Syndicate): trigger_gap=1, product_fit=3, n_products=None
- Sompo International (London Market Energy): trigger_gap=2, product_fit=2, n_products=None
- AXIS Capital / Lloyd's Syndicate 1686 (and Energy Transition Syndicate 2050): trigger_gap=1, product_fit=3, n_products=None

## Wide gap (damage-led)
- Hiscox London Market: trigger_gap=4, n_products=0
- Chubb: trigger_gap=4, n_products=0
- Zurich Insurance: trigger_gap=3, n_products=1
- Aviva: trigger_gap=4, n_products=0
- RSA (Intact): trigger_gap=4, n_products=0
- QBE Europe: trigger_gap=3, n_products=1
- Convex: trigger_gap=4, n_products=0
- Tokio Marine Kiln: trigger_gap=4, n_products=0
- MS Amlin: trigger_gap=4, n_products=0
- Aspen Insurance: trigger_gap=4, n_products=0
- Markel International: trigger_gap=4, n_products=0
- Canopius: trigger_gap=3, n_products=1
- Brit Insurance: trigger_gap=4, n_products=0
- Fidelis (MGU): trigger_gap=4, n_products=0
- Lancashire Insurance / Lloyd's Syndicate 3010: trigger_gap=4, n_products=0

---

# T3 — Grid constraint × non-firm exposure

**Question:** Do assets in SSEN/NGED constraint hotspots score higher on non-firm compute exposure?

**Tags:** `contract/asset_geo_tags.json` (DNO + constraint_zone per L3 asset).

## Headline
- L3 assets tagged: **24** / 24
- Mean non-firm eff (hotspot): **2.67**
- Mean non-firm eff (other tagged): **1.4**
- Mean non-firm eff (unclassified): **None**

## Hotspot assets
- **Virtus Data Centres — Stockley Park & Hayes, West London** [ssen/ssen_west_london]: nf=2, MoS=-15.0
- **Equinix London — LD-series IBX (Slough & Docklands)** [ssen/ssen_west_london]: nf=2, MoS=-7.5
- **Yondr Group — Slough West London Hyperscale Campus** [ssen/ssen_west_london]: nf=2, MoS=-21.3
- **CyrusOne LON6 — Iver Heath, Buckinghamshire** [ssen/ssen_west_london]: nf=2, MoS=-13.8
- **Whitelee Wind Farm — Eaglesham Moor, Scotland** [spen/scotland_wind]: nf=4, MoS=-55.0
- **Seagreen Offshore Wind Farm — Firth of Forth, off Angus, Scotland** [ssen/scotland_wind]: nf=4, MoS=-57.4
- **Gate Burton Energy Park — West Lindsey, Lincolnshire, England** [nged/nged_midlands]: nf=3, MoS=-62.6
- **Harmony Energy Pillswood BESS — Cottingham near Hull** [nged/nged_midlands]: nf=2, MoS=-52.5
- **Coalburn 1 BESS — South Lanarkshire, Scotland** [spen/scotland_wind]: nf=3, MoS=-56.2

---

# T4 — Portfolio divergence (carrier vs linked L3 slice)

**Question:** When headline carrier MoS diverges from linked-asset mean, is it book shape vs prototype slice?

## Headline
- L1 with portfolio: **39**
- Mean |carrier − portfolio avg|: **25.8** pts
- Large divergence (≥10 pts): **28**

## Largest gaps
- **Beazley**: carrier MoS +48.8 vs portfolio avg -34.0 (Δ+82.8) — carrier_safer_than_linked_assets, named links=2
- **Chaucer / Lloyd's Syndicate 1084**: carrier MoS +53.8 vs portfolio avg -6.9 (Δ+60.7) — carrier_safer_than_linked_assets, named links=0
- **AXA XL**: carrier MoS +27.5 vs portfolio avg -28.1 (Δ+55.6) — carrier_safer_than_linked_assets, named links=3
- **SCOR Syndicate 2015 (formerly The Channel Syndicate)**: carrier MoS +45.0 vs portfolio avg -6.9 (Δ+51.9) — carrier_safer_than_linked_assets, named links=0
- **Apollo Syndicate Management / Lloyd's Syndicate 1969**: carrier MoS +42.4 vs portfolio avg -6.9 (Δ+49.3) — carrier_safer_than_linked_assets, named links=0
- **Chubb**: carrier MoS +17.5 vs portfolio avg -28.1 (Δ+45.6) — carrier_safer_than_linked_assets, named links=2
- **Atrium Underwriters / Lloyd's Syndicate 609**: carrier MoS +38.7 vs portfolio avg -6.9 (Δ+45.6) — carrier_safer_than_linked_assets, named links=0
- **AXIS Capital / Lloyd's Syndicate 1686 (and Energy Transition Syndicate 2050)**: carrier MoS +38.7 vs portfolio avg -6.9 (Δ+45.6) — carrier_safer_than_linked_assets, named links=0
- **Brit Insurance**: carrier MoS +37.5 vs portfolio avg -6.9 (Δ+44.4) — carrier_safer_than_linked_assets, named links=5
- **Zurich Insurance**: carrier MoS +10.0 vs portfolio avg -34.0 (Δ+44.0) — carrier_safer_than_linked_assets, named links=3
- **Munich Re**: carrier MoS +33.8 vs portfolio avg -6.9 (Δ+40.7) — carrier_safer_than_linked_assets, named links=2
- **Aspen Insurance**: carrier MoS +30.0 vs portfolio avg -6.9 (Δ+36.9) — carrier_safer_than_linked_assets, named links=0
- **Allianz Commercial (AGCS)**: carrier MoS +28.8 vs portfolio avg -6.9 (Δ+35.7) — carrier_safer_than_linked_assets, named links=3
- **Liberty Specialty Markets**: carrier MoS +27.5 vs portfolio avg -6.9 (Δ+34.4) — carrier_safer_than_linked_assets, named links=8
- **MS Amlin**: carrier MoS +23.8 vs portfolio avg -6.9 (Δ+30.7) — carrier_safer_than_linked_assets, named links=4

---

# T5 — Whitespace: optionality vs thin evidence

**Question:** Whitespace quadrant — genuine prep>exp optionality or assessed-heavy noise?

## Headline
- Whitespace entities: **32**
- Mean measured share in whitespace: **12.2%**
- Mean prep / exp in whitespace: **75.1** / **41.1**
- Whitespace with <20% measured: **20** (62%)

## Measured share by quadrant
- whitespace: 12.2% measured (n=32)
- exposed: 3.9% measured (n=31)
- sidelined: 10% measured (n=25)
- earning_it: 6.7% measured (n=27)

## Verdict (provisional)
Whitespace skews **assessed-heavy** — reads as underwriting *hypothesis* until registers/disclosures lift measured share. Prep scores are directionally useful but magnitudes are provisional.
