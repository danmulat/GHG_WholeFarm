# Whole-farm greenhouse-gas model

This repository starts the implementation of a whole-farm greenhouse-gas (GHG)
model for mixed crop-livestock systems in East Africa.  The first deliverable is
the **master variable and equation registry**: a machine-readable contract that
must be reviewed before calculation engines are added.

The proposed architecture and the decisions that need to be resolved before
implementation are recorded in [`docs/architecture_review.md`](docs/architecture_review.md).
The registry itself is in [`registry/model_registry.csv`](registry/model_registry.csv).

## Validate the registry

The validator has no third-party runtime dependencies:

```bash
python -m wholefarm.registry validate registry/model_registry.csv
```

Run the tests with:

```bash
python -m unittest discover -s tests -v
```

## Implemented foundations

The first executable model components are intentionally method-neutral:

* `wholefarm.flows` records carbon and nitrogen transfers as a double-entry-style
  compartment ledger and blocks reporting when physical balances do not close;
* `wholefarm.climate` converts gas masses with an explicitly supplied GWP set and
  reports gross emissions, removals, net emissions, and source subtotals without
  conflating them; and
* `wholefarm.scenario` phases changes to physical activity data. It does not apply
  an assumed percentage reduction directly to final emissions.

These components provide integration boundaries for later GLEAM, crop, manure,
RothC, QRF, agroforestry, and accounting adapters. No methodology equation is
presented as verified at this stage.

## Registry status

This is a **foundation registry**, not a claim that the cited methodologies have
already been completely transcribed.  Rows marked `provisional` must be checked
against an archived primary source before they can be used for audited results.
The registry deliberately separates scientific estimates from eligibility or
crediting decisions.
