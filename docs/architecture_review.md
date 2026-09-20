# Architecture review and implementation gate

## Decision

The proposed layered architecture is suitable as a research roadmap, but it is
**not yet frozen as an auditable calculation specification**.  Development may
proceed on data contracts, provenance, unit handling, mass-balance checks and
independently testable engines.  Normative equations must not be implemented
from summaries alone.

The immediate implementation sequence is:

1. approve and version the variable/equation registry;
2. archive primary methodology documents and record page/table/equation locators;
3. implement the farm boundary and carbon/nitrogen flow ledger;
4. implement and independently verify one engine at a time;
5. integrate engines only after their interface and conservation tests pass; and
6. add reporting and methodology-specific accounting as views over scientific
   results, not as hidden changes to those results.

## Required corrections and safeguards

### Evidence terminology

A QRF prediction is a **modelled estimate**, not a measurement. Laboratory and
field observations, remote-sensing covariates, mapped predictions and process
model outputs require separate evidence classes and provenance. The digital SOC
branch may estimate a baseline distribution, but it cannot turn pixel values
into observations.

### Methodology versioning

Every normative source needs a document checksum, effective date, archived
copy, version, jurisdiction, and exact page/table/equation locator. Web pages and
repository commit hashes are useful provenance but do not replace methodology
text. Corrections and clarifications must be separate, dated source records.

The claimed GLEAM, RothC and Florida repository revisions are therefore recorded
as proposed pins only until they have been fetched, checksummed, license-reviewed
and verified against the implementation. GLEAM's AGPL terms also require an
explicit integration and distribution decision before its code is copied or
linked into this project.

### System boundary and functional units

Each result must identify organization, farm, production unit, field/herd,
reporting period, scenario, geography, gas, GWP assessment/version, and whether
the quantity is biogenic stock, removal, direct emission, upstream emission or
avoided emission. Product intensity additionally requires a declared functional
unit and allocation method. Results with different boundaries must not be added.

### Closed flow ledger

Carbon, nitrogen, dry matter, energy and area transfers need stable flow IDs.
Transfers between farm compartments are internal flows, not emissions. Manure
carbon and nitrogen must be conserved across excretion, grazing deposition,
housing, storage, treatment, export and field application, with explicit gaseous
and aqueous losses. Crop residues used as feed or fuel cannot also enter soil.
Tree biomass carbon and tree-derived soil inputs must remain distinct.

### SOC stock and depth

SOC concentration, bulk density, coarse fragments, sampled thickness and stock
are distinct variables. For consistent units, a basic layer calculation is:

`SOC stock (t C/ha) = SOC (g/kg) * bulk density (g/cm3) * depth (cm) * (1 - coarse fragments fraction) * 0.1`

Depth harmonization must retain raw horizons and method metadata. Equivalent
soil mass and fixed-depth estimates must not be mixed silently. Baseline stock
uncertainty and change uncertainty must be reported separately, including their
spatial and temporal covariance assumptions.

### Validation design

Spatial block size is a fitted design choice based on sampling geometry and
autocorrelation, never a copied constant. All transformations, feature selection,
encoding and tuning must occur within training folds. A spatially independent
holdout should be retained where sample size permits. Coverage must be checked
conditionally by geography, land use and applicability domain, not only in
aggregate.

### Accounting separation

CAP'2ER-style indicators, CARBON AGRI comparisons and Verra outputs are separate
reporting adapters. A configuration must state which equations are scientific
estimates and which quantities are eligible under a named methodology version.
No output should be labelled creditable solely because it was produced by the
scientific engine.

## Registry conventions

The CSV registry is the canonical initial interchange format. Each row represents
one variable or equation output and contains:

- stable identifier and human-readable name;
- kind (`input`, `derived`, `output`, `parameter`, or `state`);
- canonical unit and data type;
- spatial and temporal scale;
- requirement, default and validation constraints;
- equation or calculation rule;
- owning module and methodological origin;
- evidence class, source identifier and source locator;
- lifecycle status and notes.

`provisional` rows are design hypotheses. `verified` will only be permitted once
the primary source and an independent test fixture are present.

