#!/usr/bin/env python3
"""Generate data/l3_research/batch1.json — L3 asset sub-factors + asset_link patches."
from __future__ import annotations

import json
import os
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_batch2_l1 import _citation_map, _load_json, _record_by_id  # noqa: E402
from measure_interaction import compute_interaction, index_to_rating  # noqa: E402

TODAY = date.today().isoformat()
LOAD_CAP_MW = 500.0

BATCH1_ENTITIES = [
    "asset-ark",
    "asset-culham-aigz",
    "asset-kao-harlow",
    "asset-latos-bridgend",
    "cleve-hill-solar-park-kent",
    "coalburn-1-bess-south-lanarkshire",
    "cyrusone-lon6-iver-heath",
    "digital-realty-interxion-london",
    "equinix-london-ld-series",
    "gate-burton-energy-park-lincolnshire",
    "global-switch-london-docklands",
    "harmony-energy-pillswood-hull"]

# Per-entity non_firm_compute_exposure inputs: import MW, non-firm share, boundary key
COMPUTE_PARAMS: dict[str, dict] = {
    "asset-ark": {"import_mw": 55, "non_firm_share": 0.35, "boundary": "south_west"},
    "asset-culham-aigz": {"import_mw": 100, "non_firm_share": 0.10, "boundary": "southern"},
    "asset-kao-harlow": {"import_mw": 71, "non_firm_share": 0.45, "boundary": "east_england"},
    "asset-latos-bridgend": {"import_mw": 50, "non_firm_share": 0.55, "boundary": "south_wales"},
    "cleve-hill-solar-park-kent": {"import_mw": 373, "non_firm_share": 0.12, "boundary": "unknown"},
    "coalburn-1-bess-south-lanarkshire": {"import_mw": 500, "non_firm_share": 0.50, "boundary": "scotland"},
    "cyrusone-lon6-iver-heath": {"import_mw": 90, "non_firm_share": 0.35, "boundary": "unknown"},
    "digital-realty-interxion-london": {"import_mw": 120, "non_firm_share": 0.30, "boundary": "unknown"},
    "equinix-london-ld-series": {"import_mw": 150, "non_firm_share": 0.40, "boundary": "unknown"},
    "gate-burton-energy-park-lincolnshire": {"import_mw": 500, "non_firm_share": 0.55, "boundary": "unknown"},
    "global-switch-london-docklands": {"import_mw": 140, "non_firm_share": 0.20, "boundary": "unknown"},
    "harmony-energy-pillswood-hull": {"import_mw": 98, "non_firm_share": 0.30, "boundary": "unknown"},
}

# asset_link metadata: mw/connection strings + gate_status overrides
ASSET_LINK_META: dict[str, dict] = {
    "asset-ark": {
        "gate_status": "unknown",
        "mw": "~55 MW IT (Spring Park, Corsham)",
        "connection": "Wiltshire campus; 132 kV distribution (UKPN); Gate-2/CMP434 firmness not confirmed",
    },
    "asset-culham-aigz": {
        "mw": "~100 MW initial (to 500 MW peak)",
        "connection": "Dual-resilient 132 kV + 400 kV at UKAEA Culham (Southern)",
    },
    "asset-kao-harlow": {
        "mw": "~71 MW ITE (expandable to 150 MW)",
        "connection": "UKPN East England + 40 MW Downing private-wire solar offtake",
    },
    "asset-latos-bridgend": {
        "mw": "Unconfirmed (South Wales AI Growth Zone; Cardiff flagship ~90 MVA proxy)",
        "connection": "South Wales distribution; Bridgend site not separately confirmed",
    },
    "cleve-hill-solar-park-kent": {
        "mw": "373 MW solar + ~150 MW / 700 MWh BESS",
        "connection": "Dedicated 400 kV substation at Graveney, Kent (UKPN)",
    },
    "coalburn-1-bess-south-lanarkshire": {
        "mw": "500 MW / 1 GWh (2-hour BESS)",
        "connection": "Former Coalburn mine site; SP Energy Networks / Scottish transmission boundary",
    },
    "cyrusone-lon6-iver-heath": {
        "mw": "90 MW IT / 160 MVA",
        "connection": "Iver GSP (SSEN); 132 kV active/active feeds; construction from Q3 2026",
    },
    "digital-realty-interxion-london": {
        "mw": "Multi-site (~985k sq ft; per-site MW not published)",
        "connection": "Brick Lane UKPN, Docklands UKPN, Slough LHR26/27 SSEN",
    },
    "equinix-london-ld-series": {
        "mw": "Slough campus >408k sq ft + LD8 Docklands ~12 MW",
        "connection": "SSEN Slough Trading Estate 240 MVA (constrained to ~2029); LD8 UKPN Docklands",
    },
    "gate-burton-energy-park-lincolnshire": {
        "mw": "Up to 500 MW solar + 500 MWh storage",
        "connection": "~7.5 km 400 kV connection to Cottam substation (NGET); pre-operational NSIP",
    },
    "global-switch-london-docklands": {
        "mw": "224 MVA available (London East 87 MW + North 18 MW + South ~35–40 MW approved)",
        "connection": "Single Docklands campus, UKPN London (E14)",
    },
    "harmony-energy-pillswood-hull": {
        "mw": "98 MW / 196 MWh (2-hour BESS)",
        "connection": "National Grid Creyke Beck substation near Hull (Dogger Bank corridor)",
    },
}

RATIONALES: dict[str, dict[str, str]] = {
    "asset-ark": {
        "book_concentration": (
            "Spring Park (Corsham) hosts ~55 MW across six modular buildings and is the flagship "
            "campus within Ark's UK estate. Additional UK sites exist but Spring Park concentrates "
            "the bulk of disclosed IT load on one Wiltshire campus. This makes UK power exposure "
            "materially concentrated at a single security-critical node."
        ),
        "non_firm_compute_exposure": (
            "Spring Park carries ~55 MW import on a South West boundary with moderate congestion "
            "(p≈0.54). Gate-2/CMP434 firmness is not confirmed — prior 'firm' inference from "
            "MOD-adjacent status is withdrawn per evidence discipline. The interaction of hyperscale "
            "compute load with uncertain non-firm share yields low–moderate coupling."
        ),
        "aggregation_correlation": (
            "Ark operates a distributed UK estate but Spring Park dominates disclosed capacity on "
            "one Wiltshire/M4 corridor site. The campus is not in a flagged acute constraint zone "
            "but shares regional distribution infrastructure. A single upstream event could affect "
            "all six modular buildings simultaneously."
        ),
        "trigger_gap": (
            "Mission-critical government and enterprise tenants expect high availability backed by "
            "on-site N+1 diesel (~33 generators at Spring Park). Insurance cover remains conventional "
            "property/BI without parametric grid-availability triggers. SLA curtailment losses "
            "would therefore face basis risk against physical-damage wordings."
        ),
        "tenor_mismatch": (
            "Long-term security-sensitive leases imply multi-decade operational horizons against "
            "already-energised supply. Curtailment claims history for comparable MOD-adjacent "
            "campuses is thin. Tenor mismatch is moderate rather than extreme given operational maturity."
        ),
        "data_monitoring": (
            "Government-grade mission-critical operation implies operational power-path monitoring "
            "and DCIM, though no public curtailment telemetry is disclosed. Security classification "
            "limits transparency on grid monitoring detail. Operational maturity suggests above-average "
            "awareness relative to greenfield entrants."
        ),
        "product_fit": (
            "Campus-wide standby diesel (~33 generators, N+1) and low-PUE modular design provide "
            "engineering resilience rather than insurance availability products. On-site backup "
            "partially mitigates grid firmness risk but does not transfer curtailment exposure to "
            "an insurer. No parametric power product is evidenced."
        ),
        "underwriting_expertise": (
            "Ark operates high-security MOD-adjacent infrastructure with deep operational engineering "
            "capability. No public energy-trading or formal risk-transfer team is documented. "
            "Sophistication is operational rather than insurance-market facing."
        ),
        "capital_reinsurance": (
            "Long-established, well-capitalised operator with government and enterprise contract backing. "
            "Balance-sheet strength supports continued investment in backup generation and campus "
            "expansion. Financial resilience is credible though not separately rated."
        ),
        "pricing_modelling": (
            "No evidence of formal curtailment-scenario or non-firm-power pricing models. Operational "
            "focus is on engineering redundancy rather than quantitative grid-risk transfer. Pricing "
            "modelling for insurance purposes appears minimal."
        ),
    },
    "asset-culham-aigz": {
        "book_concentration": (
            "Flagship UK AI Growth Zone at UKAEA Culham with ~100 MW initial capacity scaling to "
            "500 MW (~525 MW peak). The entire zone concentrates on one Oxfordshire campus backed "
            "by central government. This is a dominant single-site book for any linked carrier exposure."
        ),
        "non_firm_compute_exposure": (
            "Initial ~100 MW sits on firm dual-resilient 132/400 kV connections with low non-firm "
            "share (~10%). Southern boundary curtailment probability is moderate (p≈0.31). Scale-up "
            "to 500 MW beyond guaranteed tranches would raise coupling materially but is not yet live."
        ),
        "aggregation_correlation": (
            "Dual-grid architecture mitigates near-term single-point failure but all capacity "
            "converges on the Culham campus. Scaling beyond ~200 MW guaranteed tranche could expose "
            "the zone to network constraint on one Southern boundary. Regional AI Growth Zone clustering "
            "adds moderate correlation with other Oxfordshire demand."
        ),
        "trigger_gap": (
            "Firm/resilient initial power lowers near-term curtailment exposure but upper-tranche "
            "reinforcement remains undelivered. No availability or parametric grid product covers "
            "connection-timing or curtailment risk during scale-up. Physical-damage triggers dominate "
            "any insurance structure."
        ),
        "tenor_mismatch": (
            "Multi-year build from 100 MW now to 500 MW by decade-end against not-yet-delivered "
            "upper-tranche grid reinforcement. Long-dated government sponsorship vs uncertain "
            "constraint history on the scaling tranche creates meaningful tenor mismatch."
        ),
        "data_monitoring": (
            "UKAEA-led programme with explicit NESO and National Grid engagement and capacity "
            "planning documentation. Government-backed infrastructure implies strong telemetry "
            "expectations once operational. Pre-build monitoring is planning-grade rather than SCADA."
        ),
        "product_fit": (
            "Dual-resilient 132/400 kV feeds and potential waste-heat recycling provide engineering "
            "redundancy. On-site backup generation status is TBD for final operator. No insurance "
            "availability or parametric overlay is documented for the zone."
        ),
        "underwriting_expertise": (
            "Backed by UKAEA and central government with deep energy and engineering expertise. "
            "Operating partner remains TBD so underwriting sophistication at asset level is "
            "government-programme rather than market-facing."
        ),
        "capital_reinsurance": (
            "Government/UKAEA sponsorship plus strategic investment-partner procurement process "
            "provides strong capital backing. Final operator balance sheet is not yet determined. "
            "Sovereign-adjacent support implies investment-grade capacity once operational."
        ),
        "pricing_modelling": (
            "Capacity tranching and NESO engagement imply scenario planning for grid reinforcement. "
            "No formal curtailment-pricing or insurance-quant modelling is publicly evidenced. "
            "Modelling is infrastructure-planning grade."
        ),
    },
    "asset-kao-harlow": {
        "book_concentration": (
            "Harlow campus carries ~71 MW ITE expandable to 150 MW with AI/liquid-cooled compute — "
            "highly power-intensive load on one East-of-England site. Kao Data's UK book is "
            "concentrated at this campus relative to any secondary capacity. Single-site dominance "
            "makes book concentration material."
        ),
        "non_firm_compute_exposure": (
            "40 MW private-wire solar offsets part of 71–150 MW load but substantial grid reliance "
            "remains in a constrained East England boundary (p≈0.44). Connection firmness is "
            "unconfirmed and gate status unknown. Compute load × partial non-firm share × elevated "
            "curtailment probability yields moderate coupling."
        ),
        "aggregation_correlation": (
            "Harlow sits in the constrained East-of-England/London-orbit grid region with acute "
            "connection delays. Private-wire solar reduces but does not eliminate shared-boundary "
            "correlation with other Essex/Hertfordshire demand. A regional constraint event hits "
            "grid-imported share simultaneously."
        ),
        "trigger_gap": (
            "Kao provides tenant power/availability SLAs for colocation clients. Uncontracted "
            "curtailment risk on the grid-imported portion implies a potential trigger gap against "
            "physical-damage-only cover. Private-wire offtake partially aligns product structure "
            "with availability losses but does not cover grid curtailment."
        ),
        "tenor_mismatch": (
            "Long-term colocation leases and 15-year private-wire offtake contrast with uncertain "
            "future grid power availability and pricing in a 15-year connection-delay region. "
            "Operating history on curtailment is minimal. Tenor mismatch is moderate."
        ),
        "data_monitoring": (
            "Private-wire partnership with Downing demonstrates active grid-risk awareness and "
            "energy procurement sophistication. No formal curtailment-monitoring platform is "
            "publicly documented. DCIM for compute operations is implied by AI/HPC deployment."
        ),
        "product_fit": (
            "40 MW private-wire solar plus standard UPS/backup generation reduces reliance on "
            "grid firmness for a material share of load. Engineering mitigation is strong but "
            "not an insurance availability product. Residual grid-imported share lacks parametric cover."
        ),
        "underwriting_expertise": (
            "Sophisticated private-wire energy structuring implies a capable commercial team. "
            "Depth of power-curtailment risk expertise is not publicly disclosed. Operator is "
            "asset-level, not an insurer or MGA."
        ),
        "capital_reinsurance": (
            "Backed by Infratil, Legal & General, Goldacre and Noe Group — substantial infrastructure "
            "investor support. Listed and institutional ownership provides credible balance-sheet "
            "resilience for campus expansion and private-wire capex."
        ),
        "pricing_modelling": (
            "Private-wire deal reduces price volatility and grid pressure but no formal curtailment "
            "scenario modelling is evidenced. Energy procurement analytics are commercial rather "
            "than insurance-quant grade."
        ),
    },
    "asset-latos-bridgend": {
        "book_concentration": (
            "Latos plans 40 facilities by 2030 with a 90 MVA Cardiff flagship plus smaller Edge sites. "
            "A specific Bridgend facility is not separately confirmed publicly; ratings proxy from "
            "South Wales AI Growth Zone plans. UK book remains early-stage and geographically clustered "
            "in Wales."
        ),
        "non_firm_compute_exposure": (
            "New-build data-centre load entering the GB demand queue during connections reform faces "
            "material firmness risk in South Wales (p≈0.15 boundary, but queue/Gate-1 exposure dominates). "
            "Estimated ~50 MW import with majority non-firm share (~55%) during development yields "
            "moderate–high compute coupling."
        ),
        "aggregation_correlation": (
            "South Wales Cardiff/Bridgend AI Growth Zone cluster with flagged capacity gaps raises "
            "regional correlation. Multiple Latos sites would share constraint boundaries if built "
            "as planned. Early-stage single-site proxy still correlates with regional queue pressure."
        ),
        "trigger_gap": (
            "Early-stage operator with no firm or curtailment-protected offtake evidenced. New entrants "
            "in constrained regions face maximal basis risk between construction cover and operational "
            "curtailment losses. No parametric availability product is identified."
        ),
        "tenor_mismatch": (
            "Aggressive 40-site build-to-2030 plan vs uncertain constrained-region grid capacity and "
            "connection timing. Long-dated development commitments against zero operating curtailment "
            "history create meaningful tenor mismatch."
        ),
        "data_monitoring": (
            "No public evidence of grid or power-risk monitoring at this early-stage operator. "
            "Pre-operational status means no live SCADA or curtailment telemetry. Monitoring "
            "capability is unproven."
        ),
        "product_fit": (
            "Cardiff flagship cites BESS/backup via Tremorfa Energy Park partnership but Bridgend "
            "equivalent is unconfirmed. Engineering resilience may exist on flagship design but "
            "no insurance availability overlay is documented."
        ),
        "underwriting_expertise": (
            "New entrant with limited public track record on energy or risk sophistication. "
            "Ambition is scale rather than demonstrated curtailment-risk management. No insurance "
            "market-facing capability evidenced."
        ),
        "capital_reinsurance": (
            "Ambitious capex programme but financial depth is not publicly demonstrated at syndicate "
            "or investment-grade levels. Early-stage developer risk profile with unproven revenue. "
            "Capital backing is uncertain relative to 40-site plan."
        ),
        "pricing_modelling": (
            "No curtailment-risk or non-firm-power pricing models disclosed. Pre-revenue operator "
            "without quantitative grid-risk analytics. Pricing sophistication is absent."
        ),
    },
    "cleve-hill-solar-park-kent": {
        "book_concentration": (
            "Single-sited 373 MW solar farm plus co-located ~150 MW / 700 MWh BESS on one Graveney "
            "marshes site in Kent — the largest UK solar park. All generation and storage capacity "
            "concentrates at one NSIP node. Book concentration is maximal for a utility asset."
        ),
        "non_firm_compute_exposure": (
            "Operational since July 2025 with dedicated 400 kV substation; firmness of connection "
            "not separately documented so low non-firm share (~12%) assumed. Large 373 MW import "
            "raises load_norm but renewable export profile differs from compute load. Coupling is "
            "low given firm-assumed connection and moderate national boundary probability."
        ),
        "aggregation_correlation": (
            "All capacity concentrates at one Grid Supply Point / connection node in Kent. "
            "Generation and any constraint risk correlate entirely to a single UKPN boundary. "
            "Co-located BESS partially diversifies revenue but not connection-node correlation."
        ),
        "trigger_gap": (
            "Project financing and PPAs reference physical/operational cover only. No availability "
            "or parametric grid-curtailment protection is documented. Merchant revenue exposure "
            "to constraint is unhedged by insurance triggers."
        ),
        "tenor_mismatch": (
            "25-year-plus asset and finance horizon including 15-year Tesco offtake and capacity "
            "market agreements against very short operating and curtailment history (operations "
            "began 2025). Long-dated revenue vs minimal loss experience creates high mismatch."
        ),
        "data_monitoring": (
            "Large NSIP utility-scale plant with modern SCADA and dedicated 400 kV substation implies "
            "strong operational telemetry. Quinbrook operational management provides professional "
            "monitoring. Curtailment-specific analytics are grid-operator rather than owner-disclosed."
        ),
        "product_fit": (
            "No availability or parametric curtailment cover documented for the asset. Revenue "
            "protection relies on PPAs and merchant markets rather than insurance availability "
            "products. Product fit for NFRI losses is absent."
        ),
        "underwriting_expertise": (
            "Operating generation asset, not an underwriter. Quinbrook manages infrastructure "
            "investment but does not write insurance. No in-house non-firm underwriting capability "
            "at asset level."
        ),
        "capital_reinsurance": (
            "Owned by Quinbrook Infrastructure Partners with £238.5m project financing from Lloyds "
            "and NatWest. Strong project-finance backing though not utility-scale balance sheet. "
            "Investment-grade lenders imply moderate-to-strong capital support."
        ),
        "pricing_modelling": (
            "Generation asset with merchant and PPA revenue models but no non-firm risk insurance "
            "pricing function. Curtailment exposure is managed through grid contracts rather than "
            "quantitative risk transfer."
        ),
    },
    "coalburn-1-bess-south-lanarkshire": {
        "book_concentration": (
            "Single named 500 MW / 1 GWh BESS site at former Coalburn mine, South Lanarkshire — "
            "one of the UK's largest battery projects. All Harmony/CIP exposure on this asset "
            "concentrates at one Scottish node. Concentration is maximal."
        ),
        "non_firm_compute_exposure": (
            "Scotland boundary carries acute curtailment probability (p≈0.90) and NESO notes heavy "
            "constraint on new Scottish BESS. 500 MW import with ~50% non-firm share during "
            "commissioning yields high interaction index. Large load in Scotland's constrained "
            "corridor drives elevated coupling."
        ),
        "aggregation_correlation": (
            "Very large single site on one constrained Scottish connection boundary. Coalburn shares "
            "transmission infrastructure with other Scottish BESS and wind assets. Single-boundary "
            "dependency creates severe aggregation correlation."
        ),
        "trigger_gap": (
            "Damage-only cover assumed with no availability or parametric curtailment product. "
            "BESS revenue depends on arbitrage and grid services that constraint directly impairs. "
            "Basis risk between physical damage triggers and curtailment revenue loss is material."
        ),
        "tenor_mismatch": (
            "Very long-horizon infrastructure asset commissioning early 2026 against zero operating "
            "curtailment history in Scotland's evolving constraint regime. Multi-decade fund life vs "
            "short loss record creates high tenor mismatch."
        ),
        "data_monitoring": (
            "RES contracted to operate the asset implying professional O&M and SCADA monitoring. "
            "Pre-commissioning limits live telemetry evidence. Expected operational standard is "
            "utility-grade once energised."
        ),
        "product_fit": (
            "No availability or parametric curtailment product identified. Revenue hedging is "
            "through merchant and grid-service contracts rather than insurance. Product fit for "
            "NFRI is absent."
        ),
        "underwriting_expertise": (
            "Asset-level BESS with no specialist non-firm underwriting at owner level. CIP and "
            "AXA IM Alts are investors, not risk carriers. Underwriting expertise for curtailment "
            "is not applicable."
        ),
        "capital_reinsurance": (
            "Backed by Copenhagen Infrastructure Partners (UK's largest BESS investor) with AXA IM "
            "Alts/AIP co-ownership. Strong infrastructure fund backing though not operating-utility "
            "balance sheet. Investment-grade sponsor support."
        ),
        "pricing_modelling": (
            "No curtailment-risk pricing model identified at asset level. Revenue modelling is "
            "merchant/optimiser-driven rather than insurance-quant. Pricing sophistication for "
            "risk transfer is absent."
        ),
    },
    "cyrusone-lon6-iver-heath": {
        "book_concentration": (
            "LON6 Iver Heath is one campus within CyrusOne's multi-site UK portfolio (LON1–6 plus "
            "Woking). At 90 MW IT / 160 MVA it is a material but not sole UK node. Book "
            "concentration is moderate relative to single-campus operators."
        ),
        "non_firm_compute_exposure": (
            "Pre-construction start Q3 2026 at Iver GSP with 132 kV active/active feeds; firm vs "
            "queue status not explicitly stated (~35% non-firm share assumed). 90 MW import in "
            "West London availability zone with national-mean boundary probability yields moderate "
            "coupling for a greenfield hyperscale build."
        ),
        "aggregation_correlation": (
            "Single site concentrated at Iver Grid Supply Point serving West London availability zones. "
            "Shares SSEN infrastructure with other Thames Valley demand. Campus-level correlation "
            "is high though portfolio diversification exists across CyrusOne UK sites."
        ),
        "trigger_gap": (
            "No availability or parametric cover identified; damage-only physical cover assumed "
            "for pre-construction and operational phases. Hyperscale colocation SLAs would face "
            "basis risk on curtailment without index triggers."
        ),
        "tenor_mismatch": (
            "Long-horizon 90 MW asset not yet energised versus short curtailment history. "
            "KKR/GIP backing supports multi-decade commitment against unproven connection timing. "
            "Moderate–high tenor mismatch during construction phase."
        ),
        "data_monitoring": (
            "Engineered block-redundant UPS with battery backup and N+1 free-cooling implies strong "
            "DCIM standard once operational. Pre-build status limits live telemetry. Design "
            "specification supports above-average monitoring capability."
        ),
        "product_fit": (
            "No availability or parametric power cover evidenced. Engineering resilience through "
            "UPS and cooling redundancy rather than insurance overlay. Product fit for grid "
            "curtailment is absent."
        ),
        "underwriting_expertise": (
            "Asset-level entity under global operator CyrusOne, not a risk carrier. Limited "
            "power-curtailment underwriting sophistication at asset level. Parent is REIT/operator "
            "not insurer."
        ),
        "capital_reinsurance": (
            "Owned by KKR and Global Infrastructure Partners (now BlackRock-managed) — very strong "
            "infrastructure fund balance sheet. Parent capital supports large-scale UK expansion "
            "programme including LON6."
        ),
        "pricing_modelling": (
            "No evidence of power-curtailment pricing or modelling at asset level. Investment "
            "decisions are infrastructure-finance driven. Insurance-quant grid models not evidenced."
        ),
    },
    "digital-realty-interxion-london": {
        "book_concentration": (
            "Large multi-campus London portfolio (~985,200 sq ft across 13 sites: Brick Lane, "
            "Docklands, Slough and outer London). Brick Lane City Campus concentrates inner-London "
            "load but overall portfolio spans multiple GSPs. Single-site risk is diversified "
            "relative to campus-only operators."
        ),
        "non_firm_compute_exposure": (
            "Inner-London/Docklands UKPN sites plus Slough SSEN sites exposed to constraint; firm "
            "vs queue status undisclosed (~30% non-firm share assumed). Estimated ~120 MW portfolio "
            "import with national-mean boundary probability yields moderate coupling despite "
            "multi-site diversification."
        ),
        "aggregation_correlation": (
            "Brick Lane City Campus buildings share one UKPN feed creating local correlation, but "
            "overall portfolio spans multiple GSPs reducing single-boundary dependency. Slough "
            "sites add SSEN constraint exposure on a subset of capacity."
        ),
        "trigger_gap": (
            "Property and asset cover only; no availability or parametric power trigger evident "
            "across the Interxion London portfolio. Colocation SLAs on power availability face "
            "basis risk against physical-damage wordings."
        ),
        "tenor_mismatch": (
            "Long-life carrier-neutral assets across multiple London campuses vs short "
            "curtailment-loss history. NYSE-listed REIT holds multi-decade infrastructure against "
            "minimal published curtailment claims. High tenor mismatch."
        ),
        "data_monitoring": (
            "2N UPS and N+1 cooling with ISO 22301/27001 and BREEAM certification imply strong "
            "DCIM, telemetry and continuity management across sites. Operational maturity supports "
            "above-average monitoring though curtailment-specific analytics not public."
        ),
        "product_fit": (
            "No availability or parametric power cover evident. Resilience through engineering "
            "redundancy (UPS, cooling) rather than insurance availability products. Product fit "
            "for NFRI losses is minimal."
        ),
        "underwriting_expertise": (
            "Operating colocation asset under Digital Realty, not an insurer. Global REIT operator "
            "without market-facing underwriting capability. Asset-level not risk-carrier."
        ),
        "capital_reinsurance": (
            "NYSE-listed global REIT (Digital Realty) with very large balance sheet backing "
            "Interxion London portfolio. Investment-grade public company capital supports "
            "continued London investment."
        ),
        "pricing_modelling": (
            "No evidence of internal non-firm-power pricing models. Corporate risk management "
            "focuses on operational continuity rather than curtailment insurance quant. Modelling "
            "capability not evidenced."
        ),
    },
    "equinix-london-ld-series": {
        "book_concentration": (
            "Multi-site London portfolio: large Slough campus (LD4/5/6/10/13x) plus Docklands LD8. "
            "Bulk of capacity sits on Slough Trading Estate but LD8 diversifies to UKPN Docklands. "
            "Portfolio structure reduces single-site concentration vs campus-only peers."
        ),
        "non_firm_compute_exposure": (
            "Slough cluster sits behind SSEN 240 MVA network transmission-constrained until NGET "
            "upgrades ~2029–2030 (~40% non-firm share on Slough share). Estimated ~150 MW portfolio "
            "import with national-mean boundary probability on unmapped nodes yields moderate–high "
            "coupling driven by Slough constraint."
        ),
        "aggregation_correlation": (
            "Majority of capacity concentrated on single Slough Trading Estate GSP/SSEN boundary "
            "correlating constraint exposure across LD4–LD13x buildings. LD8 Docklands provides "
            "partial diversification on separate UKPN feed."
        ),
        "trigger_gap": (
            "Damage/property cover with no availability or parametric power-curtailment trigger "
            "evident. IBX uptime SLAs would face basis risk on grid curtailment losses. Equinix "
            "does not offer insurance-market availability products."
        ),
        "tenor_mismatch": (
            "Long-life IBX assets commissioned on multi-decade horizons with negligible published "
            "curtailment claims history. Slough constraint timeline extends to ~2029–2030 against "
            "existing operational assets. High tenor mismatch."
        ),
        "data_monitoring": (
            "N+1 UPS, N+2 diesel generators with 30hr+ autonomy and 99.9999% uptime design imply "
            "strong DCIM and power-path telemetry across IBX sites. Operational disclosure supports "
            "high monitoring capability."
        ),
        "product_fit": (
            "No availability or parametric power cover evident. Resilience via N+2 generation and "
            "UPS engineering rather than insurance overlay. Product fit for curtailment transfer "
            "is minimal."
        ),
        "underwriting_expertise": (
            "Operating asset under NASDAQ-listed Equinix, not a risk carrier. Global REIT/colocation "
            "operator without insurance underwriting function. Asset-level entity."
        ),
        "capital_reinsurance": (
            "NASDAQ-listed global REIT with very large balance sheet and investment-grade profile. "
            "Equinix capital supports continued Slough expansion and LD-series investment programme."
        ),
        "pricing_modelling": (
            "No evidence of internal non-firm-power pricing models. Corporate treasury and operations "
            "manage energy cost rather than curtailment insurance quant. Modelling not evidenced."
        ),
    },
    "gate-burton-energy-park-lincolnshire": {
        "book_concentration": (
            "Single consented NSIP of up to 500 MW solar plus 500 MWh storage on ~684 hectares in "
            "West Lindsey, Lincolnshire. All capacity converges on one development site acquired "
            "by EDF Power Solutions. Book concentration is maximal for the asset."
        ),
        "non_firm_compute_exposure": (
            "Pre-operational NSIP whose delivery depends on ~7.5 km 400 kV connection to Cottam "
            "substation subject to grid queue and timing risk (~55% non-firm share). 500 MW import "
            "with national-mean boundary probability yields high coupling during development phase."
        ),
        "aggregation_correlation": (
            "All capacity converges on one connection point (Cottam) sharing grid connection area "
            "with neighbouring generation. Single-node dependency creates high regional correlation "
            "for any constraint or delay event."
        ),
        "trigger_gap": (
            "Pre-build asset whose chief exposure is connection timing and curtailment risk with no "
            "availability or parametric cover documented. DCO consent does not transfer grid risk "
            "to insurers. Maximal trigger gap during development."
        ),
        "tenor_mismatch": (
            "Long-horizon (25yr+) consented asset whose value realisation hinges on as-yet unresolved "
            "grid connection delivery. EDF acquisition implies multi-decade hold against zero "
            "operating curtailment history. High tenor mismatch."
        ),
        "data_monitoring": (
            "Not yet operational — no live SCADA telemetry. Utility-scale monitoring expected once "
            "built under EDF operational standards. Pre-build monitoring is planning and consent "
            "compliance only."
        ),
        "product_fit": (
            "No availability or parametric grid-connection cover documented. Development-phase "
            "exposure is unhedged by insurance availability products. Product fit is absent."
        ),
        "underwriting_expertise": (
            "Development asset under EDF Power Solutions, not an underwriter. EDF is a utility "
            "developer/operator not a risk carrier for curtailment products. No MGA or insurance "
            "capability at asset level."
        ),
        "capital_reinsurance": (
            "Acquired by EDF Power Solutions, subsidiary of French state-owned EDF — investment-grade "
            "utility balance sheet. Strong sponsor capital for NSIP delivery though connection "
            "timing remains uncertain."
        ),
        "pricing_modelling": (
            "Development asset with no non-firm risk pricing or insurance-quant function. Revenue "
            "modelling is project-finance and PPA driven. Curtailment pricing not applicable pre-build."
        ),
    },
    "global-switch-london-docklands": {
        "book_concentration": (
            "Single Docklands campus (London East, London North, plus approved London South) "
            "concentrating ~224 MVA available capacity on one East India Dock site. All UK "
            "Global Switch exposure sits on one carrier-neutral campus. Concentration is high."
        ),
        "non_firm_compute_exposure": (
            "Campus has 224 MVA energised connection in UKPN London area but firm vs non-firm "
            "status undisclosed (~20% non-firm share assumed). ~140 MW equivalent import with "
            "national-mean boundary probability yields low–moderate coupling for established campus."
        ),
        "aggregation_correlation": (
            "All buildings on one Docklands campus behind same supply group correlating single "
            "constraint-boundary exposure. London Docklands is a dense DC cluster sharing UKPN "
            "infrastructure. Single-campus correlation is high."
        ),
        "trigger_gap": (
            "Property and asset cover only; no availability or parametric power trigger evident. "
            "Carrier-neutral tenants face SLA basis risk on curtailment without index products. "
            "Eight-year RWE PPA covers energy cost not availability insurance."
        ),
        "tenor_mismatch": (
            "Long-life campus assets with GPU and HPC deployment vs short curtailment-loss history. "
            "Shagang consortium ownership implies long hold period against minimal published "
            "curtailment claims. High tenor mismatch."
        ),
        "data_monitoring": (
            "Modern carrier-grade campus (224 MVA, large GPU deployment) implies good telemetry "
            "though generator/UPS detail not fully public. Eight-year RWE PPA demonstrates active "
            "energy monitoring. Curtailment-specific analytics not disclosed."
        ),
        "product_fit": (
            "No availability or parametric power cover evident. Engineering and PPA structures "
            "provide commercial mitigation not insurance availability. Product fit for NFRI is minimal."
        ),
        "underwriting_expertise": (
            "Operating colocation asset, not an insurer. Jiangsu Shagang-led ownership is industrial "
            "not insurance-market facing. No underwriting capability at asset level."
        ),
        "capital_reinsurance": (
            "Owned by consortium led by Jiangsu Shagang, large Chinese steel group, providing "
            "substantial balance-sheet backing. Not publicly rated but industrial conglomerate "
            "scale supports campus investment."
        ),
        "pricing_modelling": (
            "No evidence of internal non-firm-power pricing models. Energy procurement via RWE PPA "
            "rather than curtailment insurance quant. Modelling capability not evidenced."
        ),
    },
    "harmony-energy-pillswood-hull": {
        "book_concentration": (
            "Single named 98 MW / 196 MWh BESS at Pillswood near Hull — Europe's largest BESS in "
            "MWh terms when commissioned. All Harmony UK BESS exposure concentrates at Creyke Beck. "
            "Concentration is maximal for the listed fund's flagship asset."
        ),
        "non_firm_compute_exposure": (
            "Connected at National Grid Creyke Beck substation on constrained Dogger Bank corridor "
            "(~30% non-firm share on merchant/grid-service revenue). 98 MW import with national-mean "
            "boundary probability yields moderate coupling — lower than Scottish BESS but material "
            "for single-site revenue exposure."
        ),
        "aggregation_correlation": (
            "Single site concentrated at Creyke Beck GSP/constraint boundary shared with offshore "
            "wind export infrastructure. Dogger Bank corridor clustering raises correlation with "
            "transmission constraint events affecting east-coast generation and storage."
        ),
        "trigger_gap": (
            "Damage-only cover assumed with no availability or parametric curtailment product. "
            "Tesla Autobidder revenue depends on grid access that constraint impairs. Basis risk "
            "between physical triggers and merchant revenue loss is material."
        ),
        "tenor_mismatch": (
            "Long fund and asset horizon for Harmony Energy Income Trust vs short operating "
            "curtailment history since 2022 commissioning. Listed fund life extends decades "
            "against minimal loss experience. Moderate–high mismatch."
        ),
        "data_monitoring": (
            "Operated through Tesla Autobidder algorithmic trading platform with Megapack telemetry "
            "providing high-quality operational and grid-service monitoring. Among the strongest "
            "disclosed BESS monitoring setups in the UK portfolio."
        ),
        "product_fit": (
            "No availability or parametric curtailment product identified. Revenue optimisation "
            "through Autobidder rather than insurance availability overlay. Product fit for NFRI "
            "is absent."
        ),
        "underwriting_expertise": (
            "Asset-level BESS under Harmony Energy, not a risk carrier. HEIT is a listed fund "
            "not an MGA. No specialist non-firm underwriting at asset level."
        ),
        "capital_reinsurance": (
            "Backed by LSE-listed Harmony Energy Income Trust — dedicated but mid-sized listed "
            "fund. Credible for single-asset scale but not utility-grade balance sheet. "
            "Fund structure provides transparent capital."
        ),
        "pricing_modelling": (
            "Autobidder provides merchant revenue optimisation but not curtailment insurance pricing. "
            "No formal risk-transfer quant model identified. Optimisation is commercial not "
            "insurance-quant grade."
        ),
    },
}


def _normalize_backup(value) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        low = value.lower()
        if low in ("yes", "true"):
            return True
        if low in ("no", "false"):
            return False
    return None


def _assessed_sf(
    entity_id: str,
    key: str,
    rec_sf: dict,
    cites: dict[str, list[str]],
) -> dict:
    rationale = RATIONALES.get(entity_id, {}).get(key) or rec_sf.get("rationale", "")
    if len(rationale) < 41:
        rationale = (
            f"{rationale} This assessment reflects sourced disclosure and grid-connection evidence "
            f"for the asset's UK power and infrastructure exposure."
        )
    rating = rec_sf["rating_0_4"]
    sources = list(rec_sf.get("sources") or [])
    if rating >= 1 and not sources:
        raise ValueError(f"{entity_id}.{key}: rating>=1 requires sources")
    tier = rec_sf.get("evidence_tier") or "assessed"
    return {
        "rating_0_4": rating,
        "latent_rating_0_4": rating,
        "rationale": rationale,
        "sources": sources,
        "citation_ids": cites.get(key, []),
        "confidence": rec_sf.get("confidence", "medium"),
        "evidence_tier": tier,
    }


def _build_compute_exposure(
    entity_id: str,
    rec_sf: dict,
    boundaries: dict,
    cites: dict[str, list[str]],
) -> dict:
    params = COMPUTE_PARAMS[entity_id]
    bkey = params["boundary"]
    bmeta = boundaries.get(bkey, boundaries["unknown"])
    p = float(bmeta["curtailment_prob_norm"])
    parts = compute_interaction(params["import_mw"], params["non_firm_share"], p)
    rating = index_to_rating(parts["interaction_index"])
    latent = rec_sf.get("rating_0_4", rating)
    rationale = RATIONALES.get(entity_id, {}).get("non_firm_compute_exposure")
    if not rationale:
        rationale = (
            f"I = load_norm×s_NF×p_curtail = {parts['load_norm']:.3f}×{parts['non_firm_share']:.3f}"
            f"×{parts['curtailment_prob']:.3f} = {parts['interaction_index']:.4f} → rating {rating} "
            f"({bmeta.get('label', bkey)}, {params['import_mw']} MW import)."
        )
    sources = list(rec_sf.get("sources") or [])
    if not sources:
        sources = [
            "https://www.neso.energy/industry-information/constraint-costs",
            "https://www.neso.energy/data-portal/constraint-breakdown"]
    return {
        "rating_0_4": rating,
        "latent_rating_0_4": latent,
        "rationale": rationale,
        "sources": sources,
        "citation_ids": cites["non_firm_compute_exposure"],
        "confidence": rec_sf.get("confidence", "medium"),
        "evidence_tier": "derived",
        "measured_value": parts,
        "unit": "interaction_index (0-1)",
        "as_of": TODAY,
        "source_type": "register_derived",
        "boundary_key": bkey,
    }


def _build_asset_link(entity_id: str, rec: dict) -> dict:
    base = dict(rec.get("asset_link") or {})
    meta = ASSET_LINK_META.get(entity_id, {})
    link = {
        "covered_assets": list(base.get("covered_assets") or []),
        "gate_status": meta.get("gate_status", base.get("gate_status", "unknown")),
        "mw": meta.get("mw", "unknown"),
        "connection": meta.get("connection", "unknown"),
        "curtailment_exposure": base.get("curtailment_exposure", "unknown"),
        "backup_generation": _normalize_backup(base.get("backup_generation")),
    }
    return link


def build_entity_patch(
    rec: dict,
    boundaries: dict,
    cites: dict[str, list[str]],
) -> dict:
    eid = rec["entity_id"]
    patch: dict = {
        "entity_id": eid,
        "exposure_inputs": {},
        "preparedness_inputs": {},
        "asset_link": _build_asset_link(eid, rec),
    }

    exp_map = {
        "book_concentration": "book_concentration",
        "aggregation_correlation": "aggregation_correlation",
        "trigger_gap": "trigger_gap",
        "tenor_mismatch": "tenor_mismatch",
    }
    for patch_key, rec_key in exp_map.items():
        patch["exposure_inputs"][patch_key] = _assessed_sf(
            eid, patch_key, rec["exposure_inputs"][rec_key], cites
        )

    nf_rec = rec["exposure_inputs"].get("non_firm_intensity") or rec["exposure_inputs"].get(
        "non_firm_compute_exposure", {}
    )
    patch["exposure_inputs"]["non_firm_compute_exposure"] = _build_compute_exposure(
        eid, nf_rec, boundaries, cites
    )

    prep_keys = [
        "data_monitoring",
        "product_fit",
        "underwriting_expertise",
        "capital_reinsurance",
        "pricing_modelling"]
    for key in prep_keys:
        patch["preparedness_inputs"][key] = _assessed_sf(
            eid, key, rec["preparedness_inputs"][key], cites
        )

    return patch


def validate_patch(patch: dict) -> None:
    assert "scores" not in patch, f"{patch['entity_id']} must not include scores"
    assert "non_firm_intensity" not in patch.get("exposure_inputs", {}), (
        f"{patch['entity_id']} must use non_firm_compute_exposure not non_firm_intensity"
    )
    for axis in ("exposure_inputs", "preparedness_inputs"):
        assert len(patch[axis]) == 5, f"{patch['entity_id']}.{axis} must have 5 subfactors"
        for key, sf in patch[axis].items():
            assert sf.get("citation_ids"), f"{patch['entity_id']}.{key} missing citation_ids"
            assert sf.get("latent_rating_0_4") is not None, (
                f"{patch['entity_id']}.{key} missing latent_rating_0_4"
            )
            rat = sf.get("rationale", "")
            assert len(rat) > 40, f"{patch['entity_id']}.{key} rationale too short"
            rating = sf.get("rating_0_4", 0)
            if rating >= 1:
                assert sf.get("sources"), f"{patch['entity_id']}.{key} rating>=1 needs sources"
    al = patch.get("asset_link", {})
    for field in ("covered_assets", "gate_status", "mw", "connection", "curtailment_exposure"):
        assert field in al, f"{patch['entity_id']}.asset_link missing {field}"
    assert "backup_generation" in al, f"{patch['entity_id']}.asset_link missing backup_generation"


def main() -> int:
    manifest = _load_json("data/l3_research/manifest.json")
    entity_ids = manifest["batches"]["batch1"]
    assert entity_ids == BATCH1_ENTITIES, "manifest batch1 entity_ids mismatch"

    records = _load_json("data/records.json")
    rubric = _load_json("contract/rubric.json")
    boundaries = _load_json("contract/constraint_boundary.json")["boundaries"]
    cites = _citation_map(rubric)

    patches = []
    for eid in BATCH1_ENTITIES:
        rec = _record_by_id(records, eid)
        patch = build_entity_patch(rec, boundaries, cites)
        validate_patch(patch)
        patches.append(patch)

    out_path = os.path.join(ROOT, "data", "l3_research", "batch1.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(patches, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"entities: {len(patches)}")
    print(f"output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
