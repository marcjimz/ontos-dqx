# ontos-dqx

**ODCS-Driven Data Quality with Ontos** — A demo showing how [Ontos](https://github.com/databrickslabs/ontos) enforces [ODCS v3.0.2](https://bitol-io.github.io/open-data-contract-standard/) data contracts as quality gates across a DEV/QA/PROD promotion lifecycle on Databricks.

## What This Demonstrates

1. **ODCS as source of truth** — Data quality rules are defined in version-controlled ODCS contracts, not scattered across pipelines
2. **Multi-repo governance** — Any team/repo can change the underlying lakehouse, while Ontos DQX ensures the ODCS contract is met before promotion
3. **Lifecycle-aware quality gates** — Contracts progress through `draft` → `proposed` → `active` as data moves DEV → QA → PROD
4. **CI/CD integration** — GitHub Actions trigger Ontos API for DQX checks on every PR, merge, and release

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitHub Repository                            │
│                                                                     │
│  contracts/          sql/ddl/           sql/seed/                   │
│  ├── members.yaml    ├── 001_members    ├── members.sql             │
│  ├── formulary.yaml  ├── 002_formulary  ├── formulary.sql           │
│  └── claims.yaml     └── 003_claims     └── claims.sql (w/defects) │
│                                                                     │
│  .github/workflows/                                                 │
│  ├── pr-quality-gate.yml  ──→ DEV   (draft)                        │
│  ├── promote-qa.yml       ──→ QA    (proposed)                     │
│  └── release-prod.yml     ──→ PROD  (active)                       │
└──────────────┬──────────────────────────────┬───────────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐   ┌──────────────────────────────┐
│   Databricks Workspace   │   │     Ontos (Databricks App)   │
│                          │   │                              │
│  ih_genie_governance2_dev│   │  ODCS Contracts              │
│    └── pharmacy.*        │◄──│    quality rules              │
│  ih_genie_governance2_qa │   │    schema definitions         │
│    └── pharmacy.*        │   │                              │
│  ih_genie_governance2    │   │  DQX Quality Checks          │
│    └── pharmacy.*        │   │    profiling + validation     │
└──────────────────────────┘   └──────────────────────────────┘
```

## Domain: Pharmacy PBM

This demo uses a Pharmacy Benefits Manager (PBM) domain with three simple tables:

| Table | Description | Quality Rules |
|-------|-------------|---------------|
| **members** | PBM member enrollment | ID format, gender codes, date ordering |
| **formulary** | Drug formulary tiers | NDC format, tier range, quantity limits |
| **claims** | Pharmacy claims | Referential integrity, cost validation, status codes, date checks |

The seed data includes **intentional defects** in `claims` (orphaned member IDs, negative costs, future dates, empty status) to demonstrate quality gate failures.

## Quick Start

```bash
# 1. Clone with submodule
git clone --recurse-submodules https://github.com/marcjimz/ontos-dqx.git
cd ontos-dqx

# 2. Set up environment
make setup        # creates .env from template
# Edit .env with your Databricks workspace credentials

# 3. Install dependencies
make install

# 4. Deploy to DEV (creates catalog, schema, tables, and seed data)
make deploy-dev

# 5. Sync ODCS contracts to Ontos
make sync-contracts-dev

# 6. Run DQX quality gate (will show failures from seed defects)
make dqx-dev
```

## Promotion Lifecycle

```
PR opened ──→ Deploy to DEV ──→ Sync contracts (draft) ──→ DQX gate
                                                              │
                                                    Pass? ────┤
                                                    │ No      │ Yes
                                                    ▼         ▼
                                              Block PR    Merge to main
                                                              │
                                              ┌───────────────┘
                                              ▼
                            Deploy to QA ──→ Sync contracts (proposed) ──→ DQX gate
                                                                              │
                                                                    Pass? ────┤
                                                                    │ No      │ Yes
                                                                    ▼         ▼
                                                              Block merge  Tag release
                                                                              │
                                                              ┌───────────────┘
                                                              ▼
                                            Deploy to PROD ──→ Sync contracts (active) ──→ DQX gate
```

## Environment Configuration

| Environment | Catalog | Contract Status | Trigger |
|-------------|---------|-----------------|---------|
| DEV | `ih_genie_governance2_dev` | `draft` | Pull request |
| QA | `ih_genie_governance2_qa` | `proposed` | Merge to main |
| PROD | `ih_genie_governance2` | `active` | Release tag |

## GitHub Actions Setup

Configure these secrets in your repository settings for each environment (`dev`, `qa`, `prod`):

| Secret | Description |
|--------|-------------|
| `DATABRICKS_HOST` | Workspace URL (e.g., `https://adb-xxx.azuredatabricks.net`) |
| `DATABRICKS_TOKEN` | PAT or Service Principal token |
| `DATABRICKS_WAREHOUSE_ID` | SQL Warehouse ID |
| `ONTOS_BASE_URL` | Ontos application URL |

## Repository Structure

```
ontos-dqx/
├── .github/
│   ├── actions/ontos-dqx/action.yml    # Reusable composite action
│   └── workflows/
│       ├── pr-quality-gate.yml         # PR → DEV
│       ├── promote-qa.yml              # Merge → QA
│       └── release-prod.yml            # Release → PROD
├── contracts/                          # ODCS v3.0.2 data contracts
├── sql/ddl/                            # Table DDLs
├── sql/seed/                           # Seed data (with defects)
├── scripts/                            # Deployment and quality scripts
├── config/                             # Environment configuration
├── ontos/                              # Ontos submodule
├── Makefile                            # Developer targets
└── requirements.txt
```

## Make Targets

```
make help               Show all available targets
make deploy-dev         Deploy DDL + seed data to DEV
make deploy-qa          Deploy DDL (no seed) to QA
make sync-contracts-dev Upload ODCS contracts (draft) to Ontos
make dqx-dev            Run DQX quality gate against DEV
make promote-qa         Full DEV→QA promotion (deploy + contracts + DQX)
make promote-prod       Full QA→PROD promotion (deploy + contracts + DQX)
```
