# NFRI Feature Dictionary

Every sub-factor maps to a **measured or disclosed primary source** wherever one exists. This is the spine of the no-synthetic rule: the harness collects *data*, then a rating is *derived* from the data — the LLM never originates the number. Where no measurement exists, the sub-factor is `assessed`, capped at medium confidence, and must cite specific evidence. The validator reports each entity's **measured share** so assessed signals cannot silently dominate.

`tier` ∈ {measured, disclosed, derived, assessed}. `as_of` required on all measured/disclosed values.

## Exposure axis

| Sub-factor | Target tier | Primary source (verified) | Exact field / computation |
|---|---|---|---|
| **non_firm_intensity** | **measured / derived** | DNO **Embedded Capacity Register** (Opendatasoft v2.1): UKPN `ukpn-embedded-capacity-register`, SSEN `data.ssen.co.uk`, **national** combined ECR on Northern Powergrid; **NESO TEC register** (datastore `17becbab-…`, "Gate" column) | For demand assets: MW-weighted share of `import_capacity` flagged with a **flexible/curtailable connection** or **flexibility-service** in the ECR. For generation/storage: share of MW on **Gate 1** (not yet Gate 2) in the TEC register. Derived = Σ(non-firm MW)/Σ(MW). |
| **book_concentration** | **disclosed / derived** | **Companies House** iXBRL accounts (filing API); **Lloyd's** syndicate annual reports (class of business); **Solvency II SFCR** (premium by line of business) | Share of GWP / segmental revenue in energy + property + data-centre/specialty classes. Derived from disclosed segmental figures. |
| **aggregation_correlation** | **derived** | ECR/TEC location fields (Grid Supply Point, licence area) + **NESO constraint boundaries** | Herfindahl index of covered/owned MW across GSP groups or constraint boundaries; higher concentration → higher score. |
| **trigger_gap** | **disclosed → assessed** | Filed **product wordings** / Lloyd's coverholder binding-authority class; FCA product governance | Boolean: does the entity's relevant cover rely on physical-damage triggers only (no availability/parametric)? Evidenced by product docs; assessed (capped) if only press describes it. |
| **tenor_mismatch** | **disclosed → assessed** | Disclosed facility/policy terms; project-finance tenor in press/filings | Max cover tenor (years) vs years of available claims history. Disclosed where terms are public. |

## Preparedness axis

| Sub-factor | Target tier | Primary source (verified) | Exact field / computation |
|---|---|---|---|
| **capital_reinsurance** | **disclosed** | **AM Best / S&P / Fitch** financial-strength rating; **Solvency II SFCR** SCR-coverage ratio & own funds; Lloyd's capacity | Map (rating, SCR coverage %) → 0–4 via a fixed lookup. Fully disclosed. |
| **product_fit** | **disclosed** | Named, evidenced **availability/parametric products** (company filings, Lloyd's Lab, regulatory approvals, press release with product name) | Count of distinct *evidenced* non-damage/parametric products tied to power/DC risk → 0–4. Disclosed (product exists or it does not). |
| **data_monitoring** | **assessed (capped)** | Verifiable artifacts only: published dataset, patent, third-party audit, named telemetry platform | Assessed 0–4 with cited artifact; **no vendor self-claim alone** (a marketing "260bn data points" page is tier-6 → not scorable). Promote to *disclosed* only if a third party verifies. |
| **underwriting_expertise** | **assessed (capped)** | Named specialist team via **FCA register** approved persons; disclosed hires; Lloyd's syndicate class permissions | Disclosed where regulatory approvals name the function; otherwise assessed with named-person evidence. |
| **pricing_modelling** | **assessed (capped)** | Published methodology, model documentation, patents | Assessed with cited artifact; capped at medium confidence absent a verifiable model. |

## Net effect on the axes

After this dictionary is applied at scale, the **Exposure axis becomes predominantly measured/disclosed** (non_firm_intensity from the ECR/TEC, book_concentration from filings, aggregation derived from grid geography), and **capital_reinsurance and product_fit on the Preparedness axis become disclosed**. Only `data_monitoring`, `underwriting_expertise` and `pricing_modelling` remain irreducibly `assessed` — and those are weight-limited (combined ≤ 0.60 of the Preparedness axis) and reported transparently. Target: **measured/disclosed share ≥ 0.6 per axis** before any entity is published.

## Data-access endpoints (verified)

- **NESO datastore** — `https://api.neso.energy/api/3/action/datastore_search?resource_id=17becbab-e3e8-473f-b303-3806f43a6a10` (TEC); `datastore_search_sql` for filtered queries; CSV twice weekly; NESO Open Data Licence; ≤1 req/s.
- **UK Power Networks** — `https://ukpowernetworks.opendatasoft.com/api/explore/v2.1/catalog/datasets/ukpn-embedded-capacity-register/records` (+ `…-1-under-1mw`).
- **SSEN Distribution** — `https://data.ssen.co.uk/` ECR data asset.
- **Northern Powergrid** — `https://northernpowergrid.opendatasoft.com/` (hosts the **national** ECR combine).
- **National Grid Electricity Distribution** — `https://connecteddata.nationalgrid.co.uk/`.
- **Companies House** — `https://api.company-information.service.gov.uk/` (free API key).
- **FCA** — `https://register.fca.org.uk/` / `https://data.fca.org.uk/` (Financial Services Register API).
