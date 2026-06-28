#!/usr/bin/env python3
"""Generate data/l1_research/batch3.json — L1 research patches for batch3 Lloyd's syndicates."
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_batch2_l1 import _citation_map, _load_json, _record_by_id, validate_patch  # noqa: E402

BATCH3_ENTITIES = [
    "inigo-1301",
    "chaucer-1084",
    "travelers-5000",
    "axis-1686",
    "allied-world-2232",
    "apollo-1969",
    "ark-4020",
    "atrium-609",
    "beat-4242",
    "aegis-london-1225"]

LLOYDS_RATINGS = "https://www.lloyds.com/about-lloyds/investor-relations/ratings"

SYNDICATE_ACCOUNTS = {
    "inigo-1301": (
        "https://assets.lloyds.com/media/9520bfff-fb54-4aa5-abbe-03367ae08023/"
        "1301%20Inigo%20Syndicate%20-%201301%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
    ),
    "chaucer-1084": "https://media.chaucergroup.com/documents/Syndicate_1084-2024.pdf",
    "travelers-5000": (
        "https://www.lloyds.com/about-lloyds/investor-relations/"
        "syndicate-reports-and-accounts/2006-5000"
    ),
    "axis-1686": (
        "https://assets.lloyds.com/media/d33b75ae-31c2-4b22-b888-3b8c91ff48fe/"
        "1686%20Axis%20Syndicate%20-%201686%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1%20(1).html"
    ),
    "allied-world-2232": (
        "https://assets.lloyds.com/media/e28f76fd-0d97-404f-b670-7f9574217a32/"
        "2232%20Allied%20World%20Syndicate%20-%202232%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
    ),
    "apollo-1969": (
        "https://assets.lloyds.com/media/67b970dc-d836-4910-be89-e0a60f768be1/"
        "1969%20Apollo%20Syndicate%20-%201969%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
    ),
    "ark-4020": (
        "https://assets.lloyds.com/media/8865c6d6-d827-43f9-a62f-de5af166d90e/"
        "4020%20Ark%20Syndicate%20-%204020%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
    ),
    "atrium-609": "https://www.atrium-uw.com/wp-content/uploads/2025/10/syndicate-609-2024-accounts.pdf",
    "beat-4242": (
        "https://assets.lloyds.com/media/6e3cdb67-2bcc-412c-8941-ddc303a62362/"
        "4242%20Beat%20Syndicate%20-%204242%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
    ),
    "aegis-london-1225": (
        "https://assets.lloyds.com/media/4c27add6-228f-4022-aa0a-44d0a62d6dac/"
        "1225%20Aegis%20London%20Syndicate%20-%201225%20-%20Q4%202024%20Syndicate%20Accounts%20"
        "Submission%20(Mar%206,%202025)-ixbrl-r1.html"
    ),
}

PRODUCT_URLS = {
    "inigo-1301": "https://inigoinsurance.com/specialties/natural-resources/onshore-energy-insurance/",
    "chaucer-1084": "https://www.chaucergroup.com/classes/renewable-energy",
    "travelers-5000": "https://www.travelers.co.uk/lloyds/specialties/power",
    "axis-1686": "https://www.axiscapital.com/londonmarket/insurance/global-energy-resilience/renewable-energy",
    "allied-world-2232": "https://alliedworldinsurance.com/products/property-energy-europe-uk/",
    "apollo-1969": "https://apollounderwriting.com/marine-energy-transport/energy/",
    "ark-4020": "https://arkunderwriting.com/ark-4020/marine-energy/",
    "atrium-609": "https://www.atrium-uw.com/underwriting/energy/",
    "beat-4242": "https://horaceuw.com/what-we-offer",
    "aegis-london-1225": "https://www.aegislondon.co.uk/content/london/specialist-underwriting/utility-property.html",
}

CAPITAL_SOURCES = {
    "inigo-1301": [LLOYDS_RATINGS],
    "chaucer-1084": [LLOYDS_RATINGS],
    "travelers-5000": [LLOYDS_RATINGS, "https://www.travelers.co.uk/lloyds/specialties/power"],
    "axis-1686": [LLOYDS_RATINGS],
    "allied-world-2232": ["https://awac.com/ratings/", LLOYDS_RATINGS],
    "apollo-1969": [LLOYDS_RATINGS],
    "ark-4020": [LLOYDS_RATINGS],
    "atrium-609": [LLOYDS_RATINGS],
    "beat-4242": [LLOYDS_RATINGS],
    "aegis-london-1225": [
        "https://www.aegislondon.co.uk/content/london/about-us/rating-and-financial-information.html",
        LLOYDS_RATINGS],
}

RATIONALES: dict[str, dict[str, str]] = {
    "inigo-1301": {
        "book_concentration": (
            "Syndicate 1301 wrote USD 1.34bn gross premium in 2024 under Radian parent Inigo, with onshore "
            "energy a named specialty capped at USD 75m max line — a secondary segment within property, "
            "reinsurance and casualty. Energy is not separately disclosed in class-of-business tables but "
            "remains incidental relative to the total stamp."
        ),
        "non_firm_intensity": (
            "Onshore energy covers PD/BI for refining, petrochemical, power generation and renewables on "
            "firm physical assets rather than merchant curtailment revenue. The USD 75m energy line appetite "
            "does not target Gate-1 or flexible-connection compute load; intermittent exposure is present on "
            "renewable elements but not dominant across the USD 1.34bn syndicate account."
        ),
        "aggregation_correlation": (
            "Heavy property-catastrophe and cat-reinsurance concentration on Syndicate 1301 creates meaningful "
            "nat-cat aggregation correlation alongside energy lines. Large property limits and reinsurance "
            "purchases can cluster correlated weather events even where energy premium share is modest."
        ),
        "trigger_gap": (
            "Property reinsurance product pages list parametric structures, giving a genuine non-indemnity "
            "trigger capability at group level. Core onshore energy stamp remains conventional PD/BI without "
            "grid-availability or SLA parametric wordings for power clients."
        ),
        "tenor_mismatch": (
            "Standard annual 12-month Lloyd's underwriting on energy and property with no long-dated availability "
            "commitments disclosed. Short policy tenor against multi-decade generation assets implies minimal "
            "tenor extension beyond typical Lloyd's annual venture model."
        ),
        "data_monitoring": (
            "Inigo is explicitly data-built with Cambridge InSPIRe and Samsara IoT telemetry partnerships and "
            "dedicated data analysts supporting underwriting. Capability exceeds generic market statistics though "
            "not yet evidenced as curtailment-grade grid telemetry on the energy line."
        ),
        "product_fit": (
            "Parametric is offered within property reinsurance but no parametric or availability product targets "
            "power, grid output or data-centre firmness on the onshore energy stamp. Minor group capability does "
            "not translate to energy product design for NFRI-relevant losses."
        ),
        "underwriting_expertise": (
            "Named onshore energy team writing power and utilities including Declan Fitchew and Paul Talbot within "
            "a data-science-led syndicate platform. Specialist bench is credible on conventional generation property "
            "though not market-leading on availability-index design."
        ),
        "capital_reinsurance": (
            "Syndicate 1301 trades on Lloyd's market ratings AM Best A+ (Superior) and Fitch/S&P/Kroll AA- "
            "(Very Strong) per Lloyd's central disclosure. Radian parent backing and reinsurance purchasing support "
            "large property limits though syndicate-level SCR is not separately published."
        ),
        "pricing_modelling": (
            "Public data-science and analytics-driven underwriting philosophy is stated but no formally published "
            "curtailment-probability or connection-status methodology exists for the energy line. Pricing relies on "
            "engineering and portfolio analytics rather than validated grid models."
        ),
    },
    "chaucer-1084": {
        "book_concentration": (
            "Syndicate 1084 reported USD 2.38bn gross written premium in 2024 with Lloyd's Energy class roughly "
            "USD 22m — under 1% of the stamp despite a named renewable energy class and weather parametric franchise. "
            "Energy is one of five core classes in a top-ten Lloyd's syndicate rather than a dominant book."
        ),
        "non_firm_intensity": (
            "Renewable energy class writes wind, solar and BESS where output variability and grid constraints are "
            "material, but Chaucer does not disclose non-firm connection share. Traditional energy property remains "
            "firm-asset PD/BI; intermittent generation exposure is moderate within the total USD 2.38bn account."
        ),
        "aggregation_correlation": (
            "Global renewable and power portfolios can cluster on shared weather grids and regional constraint "
            "boundaries, creating moderate regional correlation. Chaucer's diversified five-class book and "
            "international spread mitigate but do not eliminate UK/EU renewable clustering."
        ),
        "trigger_gap": (
            "Chaucer offers parametric weather cover and a non-damage business-interruption product alongside "
            "conventional renewable PD/BI — evidenced non-damage structures that partially close the basis-risk "
            "gap. Physical-damage wordings still anchor much of the energy premium on the USD 22m Energy class."
        ),
        "tenor_mismatch": (
            "Annual Lloyd's cover is written against long-life renewable assets while UK grid-curtailment-as-BI claims "
            "history remains thin. Multi-year construction phases on greenfield renewables extend tenor somewhat "
            "without commensurate loss experience."
        ),
        "data_monitoring": (
            "Published ESG Balanced Scorecard built with Moody's (158 data points) and a data-centric weather class "
            "provide proprietary hazard and ESG feeds beyond generic market statistics. Weather parametric underwriting "
            "leverages index data though curtailment telemetry is not separately disclosed."
        ),
        "product_fit": (
            "Parametric weather BI, K2 parametric, Kita carbon cover and renewable BI products address non-damage "
            "and index-linked triggers on renewable risks. Among the strongest product-fit profiles in this batch "
            "though weather-indexed rather than pure grid-availability indexed."
        ),
        "underwriting_expertise": (
            "Named renewable energy team (Schnorr, Ray, Bishop) with dedicated leadership and market-facing "
            "innovation via Lloyd's Lab partnerships. Recognised authority on renewable property with growing "
            "parametric and weather underwriting depth."
        ),
        "capital_reinsurance": (
            "Syndicate 1084 carries Lloyd's market rating AM Best A+ / S&P AA- with China Re parent support. "
            "Top-ten stamp scale and group reinsurance provide deep capacity for correlated renewable and "
            "weather events on the USD 2.38bn platform."
        ),
        "pricing_modelling": (
            "Published ESG Balanced Scorecard methodology with Moody's integration demonstrates quantitative "
            "portfolio assessment on renewable risks. Does not yet evidence validated UK curtailment-probability "
            "models but exceeds rule-of-thumb pricing on supported programmes."
        ),
    },
    "travelers-5000": {
        "book_concentration": (
            "Travelers Syndicate 5000 runs one of the largest dedicated power and utility books in the London "
            "specialty market, backed 100% by Travelers capital via corporate members. The Global Renewable Energy "
            "Practice targets 20% CAGR growth — power, T&D, oil and gas and renewables form a core franchise "
            "rather than an incidental line."
        ),
        "non_firm_intensity": (
            "Power pages explicitly cover generation, transmission, distribution, onshore wind, solar and BESS "
            "including curtailable merchant and renewable assets. GREP growth strategy implies a majority-intermittent "
            "insured base on operational renewables relative to baseload-only plant, though connection status is "
            "not quantified."
        ),
        "aggregation_correlation": (
            "Worldwide power and utilities plus renewables across T&D networks creates shared-grid geographic "
            "aggregation on large multinational programmes. Travelers' scale as a leading London power writer means "
            "multiple insureds can correlate on regional weather and constraint events."
        ),
        "trigger_gap": (
            "Cover is all-risks direct physical loss or damage and ensuing time element with no parametric or "
            "grid-availability product on the power stamp. Entirely physical-damage triggers against exposures where "
            "curtailment and SLA losses may be non-damage in nature — maximal basis risk for NFRI."
        ),
        "tenor_mismatch": (
            "Standard annual physical-damage policies on long-lived grid and generation assets imply typical "
            "energy-property tenor mismatch. GREP construction appetite extends cover on greenfield renewables but "
            "operational BI remains short-dated against thin curtailment history."
        ),
        "data_monitoring": (
            "Dedicated in-house engineering expertise and risk-management support on power risks but no published "
            "curtailment telemetry or availability monitoring akin to Parametrix-style feeds. Engineering inspection "
            "data rather than proprietary grid-status datasets."
        ),
        "product_fit": (
            "No parametric, availability or non-damage BI product is published for power, grid output or data-centre "
            "clients on Syndicate 5000. Cover is physical damage plus ensuing time element only — zero evidenced "
            "non-damage structures for firmness risk despite large power concentration."
        ),
        "underwriting_expertise": (
            "One of the largest dedicated London power and utilities teams with named underwriters and engineers, "
            "supported by Travelers' Global Renewable Energy Practice growth mandate. Recognised market authority on "
            "conventional and renewable generation property."
        ),
        "capital_reinsurance": (
            "Syndicate 5000 trades on Lloyd's market ratings (AM Best A+, S&P AA-, Fitch AA-, KBRA AA-) with 100% "
            "Travelers group backing via corporate members. Deep parent balance-sheet and reinsurance support large "
            "power limits though syndicate SCR is not separately disclosed."
        ),
        "pricing_modelling": (
            "No published underwriting or curtailment-pricing methodology; references engineering-led risk assessment "
            "only on power and renewable accounts. Rule-of-thumb and engineering benchmarks dominate without "
            "quantitative grid models."
        ),
    },
    "axis-1686": {
        "book_concentration": (
            "Syndicate 1686 wrote USD 1.97bn gross premium in 2024 alongside purpose-built Energy Transition "
            "Syndicate 2050 with USD 43.5m stamp capacity on renewables, BESS and transition risks. Global Energy "
            "Resilience is a core named segment — not the whole book but a strategic franchise within AXIS Capital."
        ),
        "non_firm_intensity": (
            "Heavy renewables, BESS and offshore/onshore wind exposure plus the dedicated 2050 energy-transition "
            "syndicate imply a significant intermittent-generation footprint. Contingent BI and parametric weather "
            "capacity target revenue shortfall on curtailable assets though firm/non-firm split is not disclosed."
        ),
        "aggregation_correlation": (
            "Large company paper plus combined 1686/2050 capacity on renewables implies meaningful correlated grid "
            "aggregation on major renewable programmes. Multinational energy clients can share constraint boundaries "
            "under common AXIS paper."
        ),
        "trigger_gap": (
            "AXIS actively offers parametric/weather-risk capacity and contingent BI / loss-of-revenue covers — not "
            "purely damage-only on supported programmes. Physical-damage wordings remain on much conventional energy "
            "premium but evidenced non-damage structures rank among the best in this batch."
        ),
        "tenor_mismatch": (
            "Annual indemnity covers dominate though contingent BI and decommissioning liability extend tenor on "
            "transition assets. Moderate mismatch typical of Lloyd's renewable writers against thin UK curtailment "
            "claims history."
        ),
        "data_monitoring": (
            "Dedicated risk engineers and published AXIS Explores technical reports on offshore-wind downtime, "
            "solar/wind/BESS failures inform monitoring beyond generic statistics. Strong engineering analytics though "
            "not Parametrix-grade availability telemetry."
        ),
        "product_fit": (
            "Contingent BI / loss-of-revenue plus parametric/weather capacity on Global Energy Resilience and "
            "Syndicate 2050 address non-damage generation shortfall. Strongest availability-product fit in the batch "
            "though not exclusively grid-index parametric."
        ),
        "underwriting_expertise": (
            "Named energy specialists and purpose-built Syndicate 2050 led by Elliot Lyes (Active Underwriter) "
            "demonstrate dedicated transition underwriting bench. AXIS positions as a market reference on renewable "
            "and transition property with parametric capability."
        ),
        "capital_reinsurance": (
            "Syndicates 1686 and 2050 carry Lloyd's ratings S&P AA-, Fitch AA-, AM Best A with AXIS companies "
            "S&P A+ / AM Best A. Deep group capital and reinsurance support the USD 1.97bn stamp and USD 43.5m "
            "2050 transition vehicle."
        ),
        "pricing_modelling": (
            "Published AXIS Explores failure and downtime studies inform renewable pricing but no formal curtailment-"
            "probability methodology document is published. Quantitative engineering research exceeds basic models "
            "without validated portfolio grid aggregation."
        ),
    },
    "allied-world-2232": {
        "book_concentration": (
            "Syndicate 2232 wrote £472m gross premium in 2024 with Lloyd's Energy class roughly £4.4m — about 1% "
            "of the stamp. Property & Energy Europe/UK desk is a named London franchise under Fairfax parent Allied "
            "World but energy remains a secondary segment within a diversified account."
        ),
        "non_firm_intensity": (
            "Property & Energy appetite covers conventional property and energy risks on firm physical assets rather "
            "than merchant curtailment or compute load. Mixed renewable elements may carry intermittent exposure but "
            "the £4.4m Energy class is predominantly firm-generation PD/BI."
        ),
        "aggregation_correlation": (
            "Up to USD 125m capacity on property/energy programmes creates plausible regional clustering on large "
            "European accounts. Fairfax group diversification and moderate stamp size limit severe single-constraint "
            "national dependency."
        ),
        "trigger_gap": (
            "Coverage is damage/BI indemnity with no parametric or availability product on the Property & Energy "
            "Europe/UK desk. Entirely physical-damage triggers against exposures where curtailment losses may be "
            "non-damage — maximal basis risk on the £4.4m Energy class."
        ),
        "tenor_mismatch": (
            "Annual indemnity property/energy cover against long-lived assets implies standard Lloyd's tenor mismatch. "
            "No project-finance multi-decade tail cover disclosed on the £472m syndicate platform."
        ),
        "data_monitoring": (
            "No published energy-specific monitoring, curtailment telemetry or availability data capability on "
            "Syndicate 2232. Underwriting relies on submission data and engineering input rather than proprietary "
            "grid feeds."
        ),
        "product_fit": (
            "Standard property/BI indemnity with no parametric or availability product for power or grid clients. "
            "Minor endorsement flexibility does not reach established parametric market standards for firmness risk."
        ),
        "underwriting_expertise": (
            "Named London Property & Energy team led by Duncan Gorton (SVP) provides credible European energy "
            "property capability. Framed as combined Property & Energy rather than pure power desk — competent "
            "specialists but not market authority on availability products."
        ),
        "capital_reinsurance": (
            "Syndicate 2232 carries S&P A+ and Fitch AA- with group subsidiaries AM Best A+ (Superior) per AWAC "
            "ratings disclosure. Strong Fairfax-backed capacity and reinsurance support though energy line is small "
            "relative to total £472m stamp."
        ),
        "pricing_modelling": (
            "No published pricing or curtailment methodology on the Property & Energy desk. Rule-of-thumb and "
            "engineering benchmarks dominate on the £4.4m Energy class."
        ),
    },
    "apollo-1969": {
        "book_concentration": (
            "Syndicate 1969 wrote USD 858m gross premium in 2024 under Skyward parent Apollo, with offshore energy "
            "growing roughly 10% year-on-year. Energy is one of ~20 Lloyd's classes — oil and gas focused rather than "
            "power/grid — making it an incidental line within a diversified stamp."
        ),
        "non_firm_intensity": (
            "Energy book is physical oil and gas property and renewables construction rather than grid-connected "
            "merchant generation or curtailable compute. Power-generation availability is largely out of appetite on "
            "the core 1969 stamp; non-firm exposure is minimal."
        ),
        "aggregation_correlation": (
            "Broad diversification across ~20 classes with standalone power and nat-cat exclusions limits correlated "
            "grid accumulation on the USD 858m account. Oil-and-gas asset clustering is geographic rather than "
            "single UK constraint-boundary dependent."
        ),
        "trigger_gap": (
            "Sibling ibott Syndicate 1971 offers parametric capability via the Apollo platform, so 1969 is not "
            "strictly PD-only at group level. Core 1969 energy line remains conventional indemnity PD/BI without "
            "grid-availability triggers."
        ),
        "tenor_mismatch": (
            "Lloyd's annual-venture model on energy policies with no long-tenor availability commitments disclosed. "
            "Standard short-dated cover against long-life upstream assets implies moderate mismatch only."
        ),
        "data_monitoring": (
            "ibott cites an embedded actuarial and data-science function supporting parametric innovation but nothing "
            "grid or power-asset specific on Syndicate 1969. Generic analytics rather than curtailment telemetry."
        ),
        "product_fit": (
            "Demonstrated parametric capability via ibott programmes on sibling Syndicate 1971 but none are energy "
            "or grid-availability specific on the 1969 stamp. Group innovation partially offsets legacy PD wordings "
            "on core offshore energy."
        ),
        "underwriting_expertise": (
            "Named energy team (Stephen Portman, Matt Stubbings) with credible oil-and-gas depth though standalone "
            "power is out of appetite. Specialist upstream bench rather than cross-domain power/availability authority."
        ),
        "capital_reinsurance": (
            "Syndicate 1969 carries Lloyd's market ratings AM Best A+ (Superior) and S&P/Fitch/KBRA AA- (Very Strong). "
            "Skyward group backing and reinsurance purchasing support the USD 858m diversified platform."
        ),
        "pricing_modelling": (
            "References new pricing models and a data-science function via ibott but publishes no curtailment or "
            "connection-status methodology on the 1969 energy line. Rule-of-thumb upstream pricing dominates."
        ),
    },
    "ark-4020": {
        "book_concentration": (
            "Syndicate 4020 wrote £758m gross premium in 2024 with Marine & Energy class £136m (~18% of stamp) under "
            "White Mountains parent Group Ark. Energy is a meaningful segment among ~six franchises — not dominant "
            "but material — with a named renewable team on wind, solar, hydro and BESS."
        ),
        "non_firm_intensity": (
            "Named renewable energy team covers wind, solar, hydro and BESS which are inherently intermittent though "
            "cover is physical-asset PD/BI rather than merchant revenue. Mixed firm and non-firm on renewable elements "
            "without disclosed connection-status share across the £136m Marine & Energy class."
        ),
        "aggregation_correlation": (
            "Book is described as worldwide with broad geographic spread across marine, energy and other segments. "
            "Low single-constraint UK dependency though renewable portfolios can cluster regionally on weather events."
        ),
        "trigger_gap": (
            "All Marine & Energy cover is physical-damage, machinery-breakdown and BI with no parametric or "
            "availability product published. Maximal physical-damage basis risk on curtailable renewable assets "
            "within the £136m class."
        ),
        "tenor_mismatch": (
            "Standard annual Lloyd's tenor with nothing distinctive disclosed on the £758m stamp. Minimal long-dated "
            "cover extension beyond typical annual energy policies."
        ),
        "data_monitoring": (
            "Only a stated evidence-based underwriting philosophy with no telemetry or curtailment monitoring "
            "capability published. Generic submission and loss data rather than proprietary grid feeds."
        ),
        "product_fit": (
            "No parametric or availability product anywhere in the renewable energy line on Syndicate 4020. "
            "Legacy property/BI wordings only despite meaningful renewable exposure in the £136m Marine & Energy class."
        ),
        "underwriting_expertise": (
            "Named renewable energy team (Mundin, Hill, Monk) covering wind, solar, hydro and BESS within Ark's "
            "Marine & Energy franchise. Dedicated specialist bench on conventional renewable property though no "
            "availability product design."
        ),
        "capital_reinsurance": (
            "Syndicate 4020 trades on Lloyd's market ratings AM Best A+ and S&P/Fitch/KBRA AA- per Lloyd's central "
            "disclosure. White Mountains group backing provides strong capacity for the £758m stamp."
        ),
        "pricing_modelling": (
            "Only a stated underwriting philosophy with no published curtailment or connection-status methodology. "
            "Rule-of-thumb pricing on the £136m Marine & Energy renewable book."
        ),
    },
    "atrium-609": {
        "book_concentration": (
            "Syndicate 609 wrote £1.03bn gross premium in 2024 under CRC parent with upstream energy a small line "
            "within a diversified ~£1bn book. Energy premium share is incidental relative to property, casualty and "
            "weather parametric classes — below a core-segment threshold for grid/power concentration."
        ),
        "non_firm_intensity": (
            "Upstream energy line covers discrete oil-and-gas assets with no evidenced power-generation or curtailable "
            "grid-connected exposure on the energy stamp. Weather parametric division is separate from upstream energy; "
            "NFRI-relevant non-firm intensity is effectively nil on the core energy book."
        ),
        "aggregation_correlation": (
            "Discrete upstream assets plus nat-cat rather than concentrated UK grid geography on the £1.03bn stamp. "
            "Weather parametric book adds index clustering but upstream energy aggregation remains low."
        ),
        "trigger_gap": (
            "Energy line is conventional PD/BI but Atrium operates a genuine weather parametric division via AUGold "
            "platform — partial non-damage capability at entity level. Parametric is weather-indexed rather than "
            "power-availability indexed on the small upstream energy line."
        ),
        "tenor_mismatch": (
            "Annually renewable cover with no long-tenor commitments on the £1.03bn diversified platform. "
            "Short-dated policies against long-life upstream assets — minimal NFRI tenor extension."
        ),
        "data_monitoring": (
            "Quantitative Weather & Climate team with AUGold platform provides index and hazard data for parametric "
            "underwriting beyond generic statistics. Upstream energy relies on engineering survey rather than "
            "curtailment telemetry."
        ),
        "product_fit": (
            "Real parametric suite on weather/climate lines but weather-indexed rather than power-availability indexed "
            "for grid clients. Partial entity-level fit that does not extend to the small upstream energy stamp."
        ),
        "underwriting_expertise": (
            "Named upstream energy team (Gault, Bond, Burrows) plus established Weather & Climate parametric bench. "
            "Credible dual capability on upstream property and weather parametric though not combined on availability "
            "products for power."
        ),
        "capital_reinsurance": (
            "Syndicate 609 carries Lloyd's market ratings AM Best A+ and S&P/Fitch AA- per Lloyd's central disclosure. "
            "CRC group backing and reinsurance support the £1.03bn stamp."
        ),
        "pricing_modelling": (
            "AUGold platform implies quantitative weather modelling on parametric lines but no published curtailment "
            "methodology on upstream energy. Generic underwriting philosophy on the small energy book."
        ),
    },
    "beat-4242": {
        "book_concentration": (
            "Syndicate 4242 wrote USD 390m gross premium in 2024 with Energy class USD 29m (~7.4%) via Horace "
            "oil-and-gas franchise under Bain/Ambac-backed Beat Capital Partners. Energy is a dedicated franchise "
            "but moderate concentration within a multi-franchise platform."
        ),
        "non_firm_intensity": (
            "Horace writes upstream, midstream and downstream oil and gas — not interruptible grid-connected "
            "generation or curtailable compute. Physical asset focus on the USD 29m Energy class limits non-firm "
            "exposure relative to power/renewable writers."
        ),
        "aggregation_correlation": (
            "Energy book is asset-level oil and gas rather than shared UK grid geography. Low correlation on "
            "constraint-boundary events across the USD 390m stamp."
        ),
        "trigger_gap": (
            "Horace products are physical damage plus BI/loss of hire with no parametric or availability structures. "
            "Entirely physical-damage triggers on the USD 29m Energy class — maximal basis risk if grid exposure "
            "were added but current book is upstream-focused."
        ),
        "tenor_mismatch": (
            "Annual Lloyd's energy policies against long-life upstream assets imply standard tenor mismatch. "
            "No multi-decade project finance cover disclosed on Syndicate 4242."
        ),
        "data_monitoring": (
            "No published asset monitoring or telemetry capability on Horace energy lines. Submission and "
            "engineering data only on the USD 29m Energy franchise."
        ),
        "product_fit": (
            "No parametric or availability product — only damage-and-BI cover on Horace oil-and-gas lines. "
            "Zero evidenced non-damage structures for firmness or curtailment risk."
        ),
        "underwriting_expertise": (
            "Named specialist energy team led by CEO Chris Charlton (ex-Barents Re, ex-Swiss Re offshore energy) "
            "on the Horace franchise. Credible upstream bench though not power/availability authority."
        ),
        "capital_reinsurance": (
            "Syndicate 4242 is 100% Lloyd's-backed (S&P AA-, AM Best A, Fitch AA-) with Bain/Ambac capital per "
            "Lloyd's central ratings disclosure. Adequate capacity for the USD 390m stamp though not top-tier "
            "relative to AA+ peers."
        ),
        "pricing_modelling": (
            "No published pricing methodology — only a qualitative net-zero transition statement on Horace pages. "
            "Rule-of-thumb upstream pricing on the USD 29m Energy class."
        ),
    },
    "aegis-london-1225": {
        "book_concentration": (
            "Syndicate 1225 wrote £1.01bn gross premium in 2024 under utility mutual parent AEGIS, with Lloyd's "
            "Energy class roughly £24m (~2.4%) alongside Utility Property as a core franchise. Utility and energy "
            "E&P lines define the syndicate's strategic identity even where disclosed Energy GWP share is modest."
        ),
        "non_firm_intensity": (
            "Utility property and E&P cover physical generation and T&D assets with BI extensions but no non-firm "
            "merchant-revenue or curtailable compute products. Parent mutual serves North American utilities — "
            "predominantly firm-generation property rather than Gate-1 flexible load."
        ),
        "aggregation_correlation": (
            "Worldwide power-generation and utility portfolio plus nat cat creates moderate aggregation, mitigated "
            "by modest per-risk limits on the £1.01bn stamp. Utility mutual parent alignment concentrates expertise "
            "but not necessarily single UK constraint dependency."
        ),
        "trigger_gap": (
            "All published products are traditional PD/indemnity (all-risk property, machinery breakdown, BI) with "
            "no parametric or availability triggers on Utility Property or Energy E&P lines. Maximal physical-damage "
            "basis risk against curtailment and SLA losses."
        ),
        "tenor_mismatch": (
            "Annually-renewable cover against multi-decade grid and generation assets implies structural tenor "
            "mismatch typical of utility property writers. No long-dated availability cover disclosed."
        ),
        "data_monitoring": (
            "Operates digital trading platforms (Opal, Digital Lead/Follow) but no asset-level grid-telemetry or "
            "curtailment monitoring published. Platform digitisation rather than availability data partnerships."
        ),
        "product_fit": (
            "Strong fit for physical power, utility and renewable asset PD/BI but no parametric or availability "
            "product for grid output or firmness risk. Legacy property structures on a utility-specialist stamp."
        ),
        "underwriting_expertise": (
            "Deep named bench including Neville Drew (Utility Property, ex-chair LMA Power Generation Panel) on "
            "a utility-mutual-aligned syndicate. Recognised market authority on conventional power and utility "
            "property underwriting."
        ),
        "capital_reinsurance": (
            "Lloyd's chain of security plus parent AEGIS mutual AM Best A (Excellent) / a+ stable affirmed June 2026 "
            "per AEGIS London ratings page. Deep mutual-backed capacity for utility and energy lines on the £1.01bn stamp."
        ),
        "pricing_modelling": (
            "AM Best notes disciplined risk selection and conservative reinsurance but no published curtailment or "
            "connection-status pricing methodology. Engineering-led assessment on utility property rather than "
            "quantitative grid models."
        ),
    },
}


def _sf(
    entity_id: str,
    key: str,
    rec_sf: dict,
    cites: dict[str, list[str]],
    *,
    sources: list[str] | None = None,
    evidence_tier: str = "assessed",
    extra: dict | None = None,
) -> dict:
    out = {
        "rating_0_4": rec_sf["rating_0_4"],
        "rationale": RATIONALES[entity_id][key],
        "sources": sources if sources is not None else list(rec_sf.get("sources") or []),
        "citation_ids": cites[key],
        "confidence": rec_sf.get("confidence", "medium"),
        "evidence_tier": evidence_tier,
    }
    if extra:
        out.update(extra)
    return out


def build_entity_patch(rec: dict, cites: dict[str, list[str]]) -> dict:
    eid = rec["entity_id"]
    acct = SYNDICATE_ACCOUNTS[eid]
    prod = PRODUCT_URLS[eid]
    patch = {"entity_id": eid, "exposure_inputs": {}, "preparedness_inputs": {}}

    exp = rec["exposure_inputs"]
    prep = rec["preparedness_inputs"]

    patch["exposure_inputs"]["book_concentration"] = _sf(
        eid,
        "book_concentration",
        exp["book_concentration"],
        cites,
        sources=[acct, prod],
        evidence_tier="disclosed",
        extra={
            "as_of": "2024-12-31",
            "source_type": "disclosure",
        },
    )
    patch["exposure_inputs"]["non_firm_intensity"] = _sf(
        eid, "non_firm_intensity", exp["non_firm_intensity"], cites, sources=[prod, acct]
    )
    patch["exposure_inputs"]["aggregation_correlation"] = _sf(
        eid, "aggregation_correlation", exp["aggregation_correlation"], cites, sources=[prod, acct]
    )
    patch["exposure_inputs"]["trigger_gap"] = _sf(
        eid,
        "trigger_gap",
        exp["trigger_gap"],
        cites,
        sources=[prod]
        + (
            ["https://apollounderwriting.com/ibott/innovation/"]
            if eid == "apollo-1969"
            else (
                ["https://www.chaucergroup.com/news/chaucer-announces-entry-into-weather-insurance-market"]
                if eid == "chaucer-1084"
                else (
                    ["https://www.atrium-uw.com/underwriting/weather-climate/"]
                    if eid == "atrium-609"
                    else (
                        ["https://www.artemis.bm/news/excessweather-to-offer-index-parametric-weather-catastrophe-covers/"]
                        if eid == "axis-1686"
                        else (
                            ["https://inigoinsurance.com/specialties/reinsurance/reinsurance/"]
                            if eid == "inigo-1301"
                            else [prod]
                        )
                    )
                )
            )
        ),
    )
    patch["exposure_inputs"]["tenor_mismatch"] = _sf(
        eid, "tenor_mismatch", exp["tenor_mismatch"], cites, sources=[prod, acct]
    )

    dm_src = [prod]
    if eid == "inigo-1301":
        dm_src = ["https://inigoinsurance.com/who-we-are/", prod]
    elif eid == "chaucer-1084":
        dm_src = [
            "https://www.insurancebusinessmag.com/uk/news/environmental/chaucer-launches-esg-scorecard-created-with-moodys-419656.aspx",
            prod]
    elif eid == "axis-1686":
        dm_src = [prod, "https://www.axiscapital.com/londonmarket/insurance/global-energy-resilience/renewable-energy"]
    elif eid == "atrium-609":
        dm_src = ["https://www.atrium-uw.com/underwriting/weather-climate/", prod]
    elif eid == "aegis-london-1225":
        dm_src = ["https://www.businesswire.com/news/home/20260605040465/en/", prod]
    patch["preparedness_inputs"]["data_monitoring"] = _sf(
        eid, "data_monitoring", prep["data_monitoring"], cites, sources=dm_src
    )

    pf_src = [prod]
    if eid == "chaucer-1084":
        pf_src = [
            "https://www.chaucergroup.com/news/chaucer-announces-entry-into-weather-insurance-market",
            prod]
    elif eid == "apollo-1969":
        pf_src = ["https://apollounderwriting.com/ibott/innovation/", prod]
    elif eid == "atrium-609":
        pf_src = ["https://www.atrium-uw.com/underwriting/weather-climate/", prod]
    elif eid == "axis-1686":
        pf_src = [prod, "https://www.axiscapital.com/londonmarket/insurance/global-energy-resilience/renewable-energy"]
    patch["preparedness_inputs"]["product_fit"] = _sf(
        eid, "product_fit", prep["product_fit"], cites, sources=pf_src if prep["product_fit"]["rating_0_4"] >= 1 else []
    )

    ue_src = [prod]
    if eid == "beat-4242":
        ue_src = [
            "https://www.haggiepartners.com/beat-capital-partners-launches-specialist-energy-business/",
            prod]
    elif eid == "axis-1686":
        ue_src = [
            "https://www.insurancejournal.com/news/international/2024/03/05/763478.htm",
            prod]
    patch["preparedness_inputs"]["underwriting_expertise"] = _sf(
        eid, "underwriting_expertise", prep["underwriting_expertise"], cites, sources=ue_src
    )

    patch["preparedness_inputs"]["capital_reinsurance"] = _sf(
        eid,
        "capital_reinsurance",
        prep["capital_reinsurance"],
        cites,
        sources=CAPITAL_SOURCES[eid],
        evidence_tier="disclosed",
        extra={"source_type": "rating", "as_of": "2025-07-31"},
    )

    pm_src = [prod]
    if eid == "chaucer-1084":
        pm_src = [
            "https://www.insurancebusinessmag.com/uk/news/environmental/chaucer-launches-esg-scorecard-created-with-moodys-419656.aspx",
            prod]
    elif eid == "inigo-1301":
        pm_src = ["https://inigoinsurance.com/who-we-are/", prod]
    elif eid == "apollo-1969":
        pm_src = ["https://apollounderwriting.com/ibott/innovation/", prod]
    elif eid == "axis-1686":
        pm_src = [prod]
    patch["preparedness_inputs"]["pricing_modelling"] = _sf(
        eid, "pricing_modelling", prep["pricing_modelling"], cites, sources=pm_src
    )

    return patch


def main() -> int:
    records = _load_json("data/records.json")
    rubric = _load_json("contract/rubric.json")
    cites = _citation_map(rubric)

    entities = []
    for eid in BATCH3_ENTITIES:
        rec = _record_by_id(records, eid)
        patch = build_entity_patch(rec, cites)
        validate_patch(patch)
        entities.append(patch)

    out = {
        "_doc": "l1_research pass batch3 — syndicate_researcher + carrier_researcher deep rationales",
        "pass": "l1_research",
        "batch": "batch3",
        "researched_by": "syndicate_researcher+carrier_researcher",
        "last_checked": "2026-06-27",
        "entities": entities,
    }

    out_path = os.path.join(ROOT, "data", "l1_research", "batch3.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"entities: {len(entities)}")
    print(f"output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
