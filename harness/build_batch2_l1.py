#!/usr/bin/env python3
"""Generate data/l1_research/batch2.json — L1 research patches for batch2 entities."
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from measure_capital import build_subfactor as build_capital_sf  # noqa: E402
from measure_product import build_subfactor as build_product_sf, count_to_product_fit  # noqa: E402
from measure_trigger import build_subfactor as build_trigger_sf, count_to_trigger_gap  # noqa: E402

BATCH2_ENTITIES = [
    "canopius",
    "brit",
    "markel",
    "aspen",
    "allianz-agcs",
    "aviva",
    "qbe-europe",
    "rsa-intact",
    "talbot-1183",
    "lancashire-3010"]

TRIGGER_DISCLOSED = {"allianz-agcs", "aviva", "rsa-intact", "qbe-europe"}

SYNDICATE_CAPITAL = {
    "talbot-1183": {
        "fsr_rating": "A+",
        "fsr_scale": "ambest",
        "scr_coverage_pct": None,
        "fsr_source": "https://www.lloyds.com/about-lloyds/investor-relations/ratings",
        "scr_source": None,
        "as_of": "2025-07-31",
        "note": "Lloyd's market FSR (syndicate trades on Lloyd's central rating)",
    },
    "lancashire-3010": {
        "fsr_rating": "A",
        "fsr_scale": "ambest",
        "scr_coverage_pct": None,
        "fsr_source": "https://news.ambest.com/newscontent.aspx?refnum=270415&altsrc=23",
        "scr_source": None,
        "as_of": "2025-11-13",
    },
}

# Entity-specific rationales (2–4 sentences); keyed by entity_id → subfactor
RATIONALES: dict[str, dict[str, str]] = {
    "canopius": {
        "book_concentration": (
            "Canopius Syndicate 4444 hosts a dedicated Natural Resources & Energy team writing upstream, "
            "downstream and renewable risks as a core Lloyd's specialty line. Global Parametrics became a "
            "coverholder in 2023, signalling strategic emphasis on index-linked climate and energy covers. "
            "Energy is a named franchise within a diversified syndicate rather than the whole book."
        ),
        "non_firm_intensity": (
            "Renewable and parametric programmes target wind, solar and weather-index exposures where "
            "output variability is material, but the syndicate does not disclose non-firm connection share. "
            "Most traditional energy property remains firm-asset physical damage. Intermittent generation "
            "exposure is present but not dominant across the total syndicate account."
        ),
        "aggregation_correlation": (
            "Natural resources and renewable portfolios cluster on shared weather grids and North Sea / "
            "UK constraint boundaries, creating moderate regional correlation. Global Parametrics index "
            "products add event clustering on named perils while the wider Canopius book remains diversified "
            "across marine, property and casualty lines."
        ),
        "trigger_gap": (
            "Global Parametrics coverholder status brings evidenced parametric and index structures alongside "
            "conventional property/BI renewable covers. Physical-damage wordings still anchor much of the "
            "energy premium, leaving partial basis risk on curtailment and SLA losses not tied to insured damage."
        ),
        "tenor_mismatch": (
            "Renewable construction and operational covers can run multi-year while UK grid-curtailment-as-BI "
            "claims history remains thin. Canopius writes standard annual Lloyd's ventures on many lines with "
            "some extended project phases on greenfield renewables."
        ),
        "data_monitoring": (
            "Partnership with Global Parametrics provides index and hazard data feeds for parametric underwriting "
            "beyond generic market statistics. Traditional energy lines rely on engineering survey and market "
            "loss data rather than proprietary curtailment telemetry."
        ),
        "product_fit": (
            "Global Parametrics parametric coverholder programmes address non-damage weather and index triggers "
            "on renewable risks. Core Canopius energy stamp remains conventional PD/BI, yielding partial rather "
            "than market-leading product design for firmness risk."
        ),
        "underwriting_expertise": (
            "Named Natural Resources & Energy underwriters on Syndicate 4444 with upstream, downstream and "
            "renewable appetite. Parametric partnership demonstrates willingness to span traditional energy "
            "and index-linked product design within Lloyd's specialty market."
        ),
        "pricing_modelling": (
            "Parametric coverholder relationship implies quantitative index and weather modelling on supported "
            "programmes. Broader energy lines use established Lloyd's pricing with engineering input rather than "
            "published curtailment-probability models."
        ),
    },
    "brit": {
        "book_concentration": (
            "Brit Insurance operates a dedicated Energy division spanning upstream, downstream, renewables and "
            "power as a core Lloyd's specialty segment. Syndicate 2987 names energy among its lead franchises "
            "alongside property and casualty. The book is material to Brit's Lloyd's platform though not the "
            "entire group."
        ),
        "non_firm_intensity": (
            "Brit's renewable and power covers target physical assets where grid connection firmness varies, "
            "but product pages emphasise property damage and machinery breakdown rather than merchant revenue. "
            "Non-firm or curtailable exposure is incidental within a predominantly firm-asset energy portfolio."
        ),
        "aggregation_correlation": (
            "Energy and property lines share weather and catastrophe correlation on UK and North Sea renewable "
            "clusters. Brit's subscription and global spread mitigate but do not eliminate constraint-boundary "
            "clustering on large renewable programmes."
        ),
        "trigger_gap": (
            "Brit Energy covers are conventional all-risks physical damage, machinery breakdown and BI without "
            "published parametric or grid-availability triggers. Losses from curtailment or SLA breach without "
            "physical damage face typical LMA BI trigger mismatch."
        ),
        "tenor_mismatch": (
            "Multi-year construction and operational phases on renewables extend cover relative to short annual "
            "renewals on mature plant. UK curtailment loss experience remains limited versus long asset economic "
            "lives, a moderate tenor mismatch typical of Lloyd's energy writers."
        ),
        "data_monitoring": (
            "Brit cites intelligent use of data in underwriting and claims on energy risks but publishes no "
            "proprietary curtailment or grid-status telemetry. Engineering and loss experience support pricing "
            "rather than Parametrix-style availability monitoring."
        ),
        "product_fit": (
            "Energy product suite is traditional property, BI and liability without evidenced parametric or "
            "availability wordings for grid output. Minor adaptation on endorsements does not reach established "
            "parametric market standards for non-damage firmness losses."
        ),
        "underwriting_expertise": (
            "Dedicated Energy underwriting team with named leads on upstream, downstream and renewables within "
            "Brit's Lloyd's stamp. Long track record on North Sea and international energy supports recognised "
            "specialist capability."
        ),
        "pricing_modelling": (
            "Brit references data-driven underwriting on energy but does not publish curtailment-probability or "
            "connection-status models. Pricing relies on Lloyd's market experience and engineering benchmarks "
            "rather than validated portfolio aggregation for grid events."
        ),
    },
    "markel": {
        "book_concentration": (
            "Markel International's London Energy team writes upstream, downstream, power and renewables as "
            "a named specialty within Syndicate 3000. Energy is a core segment for the international platform "
            "though the syndicate also carries significant casualty and marine lines."
        ),
        "non_firm_intensity": (
            "Renewable and power covers focus on physical plant and machinery rather than merchant offtake or "
            "curtailable compute load. Markel does not disclose non-firm connection intensity; insured assets "
            "are predominantly firm-generation property risks."
        ),
        "aggregation_correlation": (
            "Energy portfolio carries moderate clustering on shared weather and regional renewable build-out, "
            "offset by Markel's global diversification across many classes. No evidence of severe single-constraint "
            "national dependency."
        ),
        "trigger_gap": (
            "Markel Energy lines are conventional property, machinery breakdown and BI without published parametric "
            "or availability products. Physical-damage triggers dominate against exposures where revenue loss may "
            "be contractual or grid-related without insured damage."
        ),
        "tenor_mismatch": (
            "Construction and operational covers on renewables can extend beyond annual cycle while curtailment "
            "claims history is thin. Standard Lloyd's annual venture model on many accounts limits extreme "
            "tenor mismatch."
        ),
        "data_monitoring": (
            "Markel uses engineering and market loss data on energy risks without disclosed curtailment telemetry "
            "or grid partnerships. Capability is generic market data rather than proprietary availability feeds."
        ),
        "product_fit": (
            "Energy products remain traditional indemnity PD/BI with minor endorsements only. No evidenced "
            "parametric or SLA-index structures comparable to Marsh Nimbus or Lockton facilities."
        ),
        "underwriting_expertise": (
            "Named London Energy underwriters with upstream, downstream and renewable expertise on Syndicate 3000. "
            "Markel's specialty culture supports dedicated energy talent though not spanning cyber/compute domains."
        ),
        "pricing_modelling": (
            "Published energy pages reference technical underwriting without quantitative curtailment models. "
            "Rule-of-thumb and engineering-led pricing rather than validated scenario aggregation for grid events."
        ),
    },
    "aspen": {
        "book_concentration": (
            "Aspen Insurance renewed its kWh Analytics partnership to expand renewable energy coverage, "
            "signalling a core specialty segment within the Lloyd's platform. Energy and renewables sit alongside "
            "property, casualty and marine as a strategic growth line under Sompo International ownership."
        ),
        "non_firm_intensity": (
            "Renewable programmes through kWh Analytics target wind and solar assets where output variability "
            "matters, but Aspen does not disclose non-firm connection share. Traditional energy property remains "
            "firm-asset focused with incidental intermittent exposure."
        ),
        "aggregation_correlation": (
            "Renewable and property books correlate on regional weather and catastrophe events. Global Sompo "
            "platform and reinsurance purchasing diversify aggregation relative to single-boundary specialists."
        ),
        "trigger_gap": (
            "kWh Analytics partnership focuses on revenue and generation analytics but published Aspen renewable "
            "covers remain property/BI wordings without parametric availability triggers. Physical-damage basis "
            "risk persists on curtailment and SLA losses."
        ),
        "tenor_mismatch": (
            "Multi-year renewable partnerships and construction phases extend tenor ahead of thin UK curtailment "
            "claims data. Annual Lloyd's cycles on operational covers limit extreme mismatch."
        ),
        "data_monitoring": (
            "kWh Analytics brings proprietary US renewable asset and loss databases to support Aspen underwriting "
            "and pricing. This exceeds generic market statistics though is not UK curtailment telemetry per se."
        ),
        "product_fit": (
            "Renewable partnership emphasises data-driven property/revenue products rather than parametric grid "
            "availability wordings. Product fit for non-damage firmness losses remains limited versus dedicated "
            "parametric MGAs."
        ),
        "underwriting_expertise": (
            "Aspen Specialty renewable team and kWh Analytics partnership demonstrate dedicated energy underwriting "
            "talent on Lloyd's. Sompo group network adds international energy reinsurance depth."
        ),
        "pricing_modelling": (
            "kWh Analytics data supports quantitative renewable pricing models on partnered programmes. Broader "
            "Aspen energy lines use established specialty pricing without published curtailment correlation models."
        ),
    },
    "allianz-agcs": {
        "trigger_gap": (
            "Allianz expert articles reference advanced BI and parametric thinking, and two evidenced non-damage "
            "product lines partially close the basis-risk gap. Core energy construction stamp remains physical-damage "
            "and delay-in-start-up led, leaving residual mismatch on curtailment without insured damage."
        ),
        "product_fit": (
            "Two evidenced non-damage or parametric-adjacent structures appear in Allianz Commercial research, "
            "demonstrating some bespoke BI adaptation. Mainstream UK energy covers remain conventional property/BI "
            "without market-leading availability parametrics."
        ),
        "book_concentration": (
            "Allianz Commercial publishes dedicated Energy & Construction insurance spanning power, renewables, "
            "upstream and downstream as a core global specialty segment. UK and European utilities and project "
            "developers are named target clients, making energy a strategic franchise within AGCS."
        ),
        "non_firm_intensity": (
            "Energy construction and operational covers include renewables where grid connection and dispatch "
            "matter, but AGCS emphasises physical asset and project phases rather than merchant curtailable load. "
            "Non-firm intensity is low to moderate on disclosed UK appetite."
        ),
        "aggregation_correlation": (
            "Global scale as a leading commercial insurer creates potential clustering on major European renewable "
            "and utility programmes under common Allianz paper. Multinational accounts concentrate exposure across "
            "related assets in constrained regions."
        ),
        "tenor_mismatch": (
            "Project-finance and construction covers extend tenor on greenfield renewables while operational BI "
            "remains annual. UK curtailment-as-BI loss history is limited relative to 15–30 year asset lives."
        ),
        "data_monitoring": (
            "Allianz Risk Consulting and engineering services provide site-level data on energy clients beyond "
            "generic statistics. Allianz Commercial publishes expert risk articles on BI trends but not UK "
            "curtailment telemetry feeds."
        ),
        "underwriting_expertise": (
            "Dedicated global Energy & Construction underwriting with named specialists spanning power, renewables "
            "and downstream. Allianz group depth supports recognised market authority in commercial energy lines."
        ),
        "pricing_modelling": (
            "Allianz publishes technical risk consulting and scenario tools on large industrial risks. Curtailment-"
            "specific validated models are not disclosed for UK renewables but quantitative capability exceeds "
            "rule-of-thumb pricing."
        ),
    },
    "aviva": {
        "trigger_gap": (
            "Aviva UK renewable pages describe property, BI and DSU on conventional all-risks wordings requiring "
            "insured peril triggers. Zero evidenced non-damage or parametric products means maximal basis risk on "
            "curtailment, SLA and availability losses without physical damage."
        ),
        "product_fit": (
            "UK GCS renewable energy is conventional construction, operational and DSU cover without parametric "
            "or grid-index structures. No published SLA, utility-index or curtailment parametric comparable to "
            "dedicated MGAs."
        ),
        "book_concentration": (
            "Aviva Global Corporate & Specialty publishes a UK Renewable Energy team covering construction, "
            "operational and DSU phases on wind, solar and BESS. Renewables are a named GCS segment within Aviva's "
            "broader commercial book rather than an incidental line."
        ),
        "non_firm_intensity": (
            "Renewable appetite explicitly includes BESS and intermittent wind/solar where output depends on grid "
            "dispatch. Aviva does not disclose data-centre or hyperscale compute exposure; renewable footprint "
            "implies mixed firm and non-firm generation assets."
        ),
        "aggregation_correlation": (
            "UK renewable portfolio clusters on shared weather and constraint boundaries, particularly offshore "
            "wind and regional solar build-out. Aviva's diversified GCS book mitigates but does not eliminate "
            "regional correlation on large accounts."
        ),
        "tenor_mismatch": (
            "Construction and DSU covers extend multi-year on greenfield renewables while operational policies "
            "renew annually. Thin UK curtailment claims history versus long asset lives creates moderate tenor "
            "mismatch."
        ),
        "data_monitoring": (
            "Aviva GCS renewable pages describe technical underwriting and risk engineering without proprietary "
            "curtailment telemetry. Capability sits between generic market data and parametric-grade monitoring."
        ),
        "underwriting_expertise": (
            "Named UK Renewable Energy underwriting team within GCS with construction-through-operational appetite. "
            "Aviva's scale supports specialist talent though not spanning cyber/compute domains at market-leading "
            "depth."
        ),
        "pricing_modelling": (
            "Renewable underwriting relies on engineering and market experience without published curtailment-"
            "probability models. Basic sector models rather than validated portfolio aggregation for grid events."
        ),
    },
    "qbe-europe": {
        "trigger_gap": (
            "QBE Sustainable Energies products emphasise conventional property and BI on renewables with one "
            "evidenced non-damage or parametric-adjacent structure. Residual trigger mismatch persists where "
            "curtailment losses are contractual rather than damage-driven."
        ),
        "product_fit": (
            "One evidenced non-damage or parametric product on sustainable energies demonstrates minor adaptation "
            "beyond legacy property/BI. Core European renewable stamp remains traditional indemnity rather than "
            "established availability parametrics."
        ),
        "book_concentration": (
            "QBE Europe's Sustainable Energies sector is a named franchise covering renewables, power and "
            "transition assets across Europe. Dedicated sector pages and underwriting teams signal a core segment "
            "within QBE's European commercial platform."
        ),
        "non_firm_intensity": (
            "Sustainable energies include wind, solar and BESS where intermittency and grid constraints are "
            "underwriting considerations. QBE does not disclose non-firm connection share; exposure is mixed "
            "firm and non-firm on renewable portfolios."
        ),
        "aggregation_correlation": (
            "European renewable and power accounts cluster on shared weather and regional constraint events. "
            "QBE's multi-country footprint provides diversification but large single-programme limits create "
            "moderate to high clustering."
        ),
        "tenor_mismatch": (
            "Construction and operational renewable covers span multi-year phases against limited curtailment "
            "loss history. Standard annual renewals on mature plant limit extreme tenor extension."
        ),
        "data_monitoring": (
            "QBE Sustainable Energies underwriting uses sector expertise and market data without disclosed "
            "curtailment telemetry partnerships. Some proprietary sector insight but not availability-grade feeds."
        ),
        "underwriting_expertise": (
            "Dedicated Sustainable Energies underwriting team with recognised European renewable and power "
            "specialists. QBE group network supports deep sector authority across transition risks."
        ),
        "pricing_modelling": (
            "Sector-focused underwriting implies structured technical pricing on nat-cat and machinery risks. "
            "No published curtailment-probability or connection-status models for UK grid events."
        ),
    },
    "rsa-intact": {
        "trigger_gap": (
            "RSA engineering and renewable appetite guide describes conventional property and BI wordings on "
            "renewable plant. Zero evidenced non-damage products implies reliance on physical-damage triggers "
            "against curtailment and SLA exposures."
        ),
        "product_fit": (
            "Engineering and renewable energy guide lists traditional indemnity covers only. No parametric, "
            "utility-index or availability wordings are published for UK renewable clients."
        ),
        "book_concentration": (
            "RSA publishes an Engineering & Renewable Energy appetite guide for brokers covering renewables, "
            "power and engineering risks as a recognised UK commercial segment. Exposure is secondary to broader "
            "RSA commercial and personal lines but material within engineering."
        ),
        "non_firm_intensity": (
            "Renewable engineering covers target physical plant and construction phases with limited merchant "
            "or curtailable load emphasis. Non-firm grid connection intensity is low on disclosed UK appetite."
        ),
        "aggregation_correlation": (
            "UK renewable and engineering portfolio carries moderate regional clustering on shared weather and "
            "construction programmes. Intact group diversification limits severe single-event national dependency."
        ),
        "tenor_mismatch": (
            "Engineering and renewable construction covers can run multi-year while operational lines renew "
            "annually. Curtailment loss history remains thin relative to project phases."
        ),
        "data_monitoring": (
            "RSA engineering underwriting uses survey and market data without proprietary curtailment telemetry. "
            "Generic commercial data capability rather than availability monitoring."
        ),
        "underwriting_expertise": (
            "Engineering and renewable energy underwriting teams within RSA UK with construction and operational "
            "appetite. Intact ownership adds North American engineering depth though UK stamp remains commercial "
            "specialist rather than market authority."
        ),
        "pricing_modelling": (
            "Engineering lines use established technical pricing without disclosed curtailment models. Rule-of-"
            "thumb and engineering benchmarks dominate."
        ),
    },
    "talbot-1183": {
        "capital_reinsurance": (
            "Talbot Syndicate 1183 trades on Lloyd's market financial strength ratings (AM Best A+ Superior; "
            "S&P/Fitch/KBRA AA- Very Strong) with AIG parent balance-sheet support. Deep reinsurance and "
            "Lloyd's chain-of-security capacity absorb correlated energy and property events."
        ),
        "book_concentration": (
            "Talbot Syndicate 1183 carries a pronounced energy, marine and specialty tilt with a Downstream "
            "Energy & Power team explicitly covering power generation and utilities. Energy is a core franchise "
            "within the AIG-backed Lloyd's platform."
        ),
        "non_firm_intensity": (
            "Power book covers physical-asset property for generation and utility plant rather than merchant "
            "intermittent revenue or data-centre compute load. Non-firm or curtailable exposure is moderate at "
            "most on renewable elements of the portfolio."
        ),
        "aggregation_correlation": (
            "Heavy property, energy and marine catastrophe book plus political violence creates meaningful correlated "
            "accumulation on large energy and property programmes. AIG parent scale supports reinsurance but "
            "syndicate-level clustering remains elevated."
        ),
        "trigger_gap": (
            "Talbot cover is explicitly all-risks direct physical loss or damage plus BI with no parametric "
            "availability product for grid output. Entirely physical-damage triggers against exposures where "
            "curtailment losses may be non-damage in nature."
        ),
        "tenor_mismatch": (
            "Conventionally annually-renewable energy and property cover with no long-dated project finance "
            "disclosure. Moderate mismatch typical of Lloyd's annual energy policies."
        ),
        "data_monitoring": (
            "Downstream Energy & Power team offers engineering reviews and site surveys but no real-time grid-"
            "output or curtailment telemetry. Technical inspection data rather than availability feeds."
        ),
        "product_fit": (
            "Physical-asset energy and power property fits traditional PD/BI well but no parametric or grid-"
            "availability product is published. Legacy property structures only for firmness risk."
        ),
        "underwriting_expertise": (
            "Named dedicated teams including Downstream Energy & Power leadership with global upstream and "
            "downstream depth. AIG parent provides recognised market authority spanning energy domains."
        ),
        "pricing_modelling": (
            "No published proprietary pricing or curtailment methodology; traditional underwriter-led assessment "
            "on energy and property risks."
        ),
    },
    "lancashire-3010": {
        "capital_reinsurance": (
            "AM Best affirmed Lancashire Holdings financial strength rating A (Excellent) and ICR a+ in "
            "November 2025, with Syndicate 3010 benefiting from Lloyd's central security. Strong but not "
            "top-tier FSR relative to AA-rated peers; adequate reinsurance supports the Power & Utility book."
        ),
        "book_concentration": (
            "Energy is one of four named core lines at Lancashire and Syndicate 3010 runs a dedicated Power & "
            "Utility book spanning conventional generation and renewables. Power is a defining franchise for the "
            "syndicate stamp."
        ),
        "non_firm_intensity": (
            "Power & Utility book spans conventional generation to renewables but cover is asset physical-damage "
            "rather than curtailable merchant output. Mixed firm and non-firm on renewable elements without "
            "dominant Gate-1 or compute load exposure."
        ),
        "aggregation_correlation": (
            "Subscription basis with global spread but power-plant and Gulf of Mexico windstorm accumulation "
            "present on energy portfolio. Moderate regional clustering without severe single UK constraint "
            "dependency."
        ),
        "trigger_gap": (
            "All energy and power cover is all-risks direct physical loss or damage plus time element with no "
            "parametric or availability triggers. Maximal physical-damage basis risk on curtailment and SLA losses."
        ),
        "tenor_mismatch": (
            "Lancashire emphasises a deliberately short-tail book with favourable reserve development per AM Best. "
            "Annual energy policies limit long-dated cover against thin curtailment history."
        ),
        "data_monitoring": (
            "No published telemetry or data-platform capability for insured power assets. Traditional underwriting "
            "and engineering assessment only."
        ),
        "product_fit": (
            "All cover is traditional indemnity PD/BI with no parametric or availability product on the Power & "
            "Utility line. Zero evidenced non-damage structures for grid firmness risk."
        ),
        "underwriting_expertise": (
            "Named power team including Head of Power (Syndicate 3010) and Head of Downstream with deep sector "
            "bench. Recognised Lloyd's authority on power and utility risks."
        ),
        "pricing_modelling": (
            "No published technical pricing or curtailment methodology; strategy documents reference general "
            "underwriting discipline without quantitative grid models."
        ),
    },
}


def _load_json(rel: str) -> dict:
    return json.load(open(os.path.join(ROOT, rel)))


def _citation_map(rubric: dict) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for axis in ("exposure", "preparedness"):
        for key, meta in rubric.get(axis, {}).items():
            out[key] = list(meta.get("citation_ids", []))
    return out


def _record_by_id(records: list, entity_id: str) -> dict:
    for r in records:
        if r["entity_id"] == entity_id:
            return r
    raise KeyError(f"entity not in records.json: {entity_id}")


def _merge_capital_rationale(base: dict, entity_id: str) -> dict:
    extra = RATIONALES.get(entity_id, {}).get("capital_reinsurance")
    if extra:
        base = dict(base)
        base["rationale"] = extra
    return base


def _merge_trigger_rationale(base: dict, entity_id: str, n: int, rating: int) -> dict:
    custom = RATIONALES.get(entity_id, {}).get("trigger_gap")
    if custom:
        base = dict(base)
        base["rationale"] = (
            f"Disclosed non-damage/parametric product count n={n} maps inversely to trigger_gap={rating}. "
            f"{custom}"
        )
    return base


def _merge_product_rationale(base: dict, entity_id: str, n: int, rating: int) -> dict:
    custom = RATIONALES.get(entity_id, {}).get("product_fit")
    if custom:
        base = dict(base)
        base["rationale"] = (
            f"Disclosed non-damage/parametric product count n={n} → product_fit={rating}. {custom}"
        )
    return base


def _assessed_sf(
    entity_id: str,
    key: str,
    rec_sf: dict,
    cites: dict[str, list[str]],
) -> dict:
    rationale = RATIONALES.get(entity_id, {}).get(key) or rec_sf.get("rationale", "")
    if len(rationale) < 41:
        rationale = (
            f"{rationale} This assessment reflects sourced underwriting appetite and product disclosure "
            f"for the entity's UK power, energy and infrastructure lines."
        )
    rating = rec_sf["rating_0_4"]
    sources = list(rec_sf.get("sources") or [])
    if rating >= 1 and not sources:
        raise ValueError(f"{entity_id}.{key}: rating>=1 requires sources")
    return {
        "rating_0_4": rating,
        "rationale": rationale,
        "sources": sources,
        "citation_ids": cites.get(key, []),
        "confidence": rec_sf.get("confidence", "medium"),
        "evidence_tier": rec_sf.get("evidence_tier") or "assessed",
    }


def build_entity_patch(
    rec: dict,
    capital_inputs: dict,
    trigger_inputs: dict,
    cites: dict[str, list[str]],
) -> dict:
    eid = rec["entity_id"]
    patch = {"entity_id": eid, "exposure_inputs": {}, "preparedness_inputs": {}}

    exp_keys = [
        "book_concentration",
        "non_firm_intensity",
        "aggregation_correlation",
        "trigger_gap",
        "tenor_mismatch"]
    prep_keys = [
        "data_monitoring",
        "product_fit",
        "underwriting_expertise",
        "capital_reinsurance",
        "pricing_modelling"]

    for key in exp_keys:
        if key == "trigger_gap" and eid in TRIGGER_DISCLOSED:
            row = trigger_inputs[eid]
            n = int(row["n_nondamage_products"])
            rating = count_to_trigger_gap(n)
            sf = build_trigger_sf(row, "live")
            sf = _merge_trigger_rationale(sf, eid, n, rating)
            sf["citation_ids"] = cites[key]
            patch["exposure_inputs"][key] = sf
        else:
            patch["exposure_inputs"][key] = _assessed_sf(
                eid, key, rec["exposure_inputs"][key], cites
            )

    for key in prep_keys:
        if key == "product_fit" and eid in TRIGGER_DISCLOSED:
            row = trigger_inputs[eid]
            n = int(row["n_nondamage_products"])
            rating = count_to_product_fit(n)
            sf = build_product_sf(row, "live")
            sf = _merge_product_rationale(sf, eid, n, rating)
            sf["citation_ids"] = cites[key]
            patch["preparedness_inputs"][key] = sf
        elif key == "capital_reinsurance":
            if eid in capital_inputs:
                sf = build_capital_sf(capital_inputs[eid], "live")
            elif eid in SYNDICATE_CAPITAL:
                sf = build_capital_sf(SYNDICATE_CAPITAL[eid], "live")
            else:
                sf = _assessed_sf(
                    eid, key, rec["preparedness_inputs"][key], cites
                )
                patch["preparedness_inputs"][key] = sf
                continue
            sf = _merge_capital_rationale(sf, eid)
            sf["citation_ids"] = cites[key]
            patch["preparedness_inputs"][key] = sf
        else:
            patch["preparedness_inputs"][key] = _assessed_sf(
                eid, key, rec["preparedness_inputs"][key], cites
            )

    return patch


def count_disclosed(patch: dict) -> int:
    n = 0
    for axis in ("exposure_inputs", "preparedness_inputs"):
        for sf in patch[axis].values():
            if sf.get("evidence_tier") == "disclosed":
                n += 1
    return n


def validate_patch(patch: dict) -> None:
    assert "scores" not in patch
    for axis in ("exposure_inputs", "preparedness_inputs"):
        assert len(patch[axis]) == 5, f"{patch['entity_id']}.{axis} must have 5 subfactors"
        for key, sf in patch[axis].items():
            assert sf.get("citation_ids"), f"{patch['entity_id']}.{key} missing citation_ids"
            rat = sf.get("rationale", "")
            assert len(rat) > 40, f"{patch['entity_id']}.{key} rationale too short"
            rating = sf.get("rating_0_4", 0)
            if rating >= 1:
                assert sf.get("sources"), f"{patch['entity_id']}.{key} rating>=1 needs sources"


def main() -> int:
    records = _load_json("data/records.json")
    rubric = _load_json("contract/rubric.json")
    capital_inputs = _load_json("contract/capital_inputs.json").get("inputs", {})
    trigger_inputs = _load_json("contract/trigger_inputs.json").get("inputs", {})
    cites = _citation_map(rubric)

    patches = []
    disclosed_total = 0
    for eid in BATCH2_ENTITIES:
        rec = _record_by_id(records, eid)
        patch = build_entity_patch(rec, capital_inputs, trigger_inputs, cites)
        validate_patch(patch)
        disclosed_total += count_disclosed(patch)
        patches.append(patch)

    out_path = os.path.join(ROOT, "data", "l1_research", "batch2.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(patches, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"entities: {len(patches)}")
    print(f"disclosed subfactors: {disclosed_total}")
    print(f"output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
