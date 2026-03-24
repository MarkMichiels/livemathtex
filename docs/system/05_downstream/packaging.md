# Packaging

## Overview

Packaging is the final step in the downstream process, converting freeze-dried algae into labeled, analyzed, and stored product. The process includes quality control sampling, internal and external analysis, lot assignment, and controlled storage.

## Product Forms

| Form | Description | Typical Use |
|------|-------------|------------|
| Dried powder | Freeze-dried and ground biomass | Primary commercial product |
| Paste/slurry | Concentrated centrifuge output (>100 g/L) | Intermediate before drying |

## Quality Control Flow

Every batch follows a structured analysis pathway before release:

### Per-Batch Analysis

| Check | Method | Frequency | Action on Failure |
|-------|--------|-----------|-------------------|
| Visual microscopy inspection | Microscope (contamination, other algae) | Every batch | Reject batch, store separately, note in analysis file |
| Internal NaCl and water analysis | Internal lab | Every batch (composite sample per 5 batches) | Record in analysis file, notify LRO on deviation |

### Per 5-Batch Analysis (Composite Sample)

| Check | Method | Frequency | Action on Failure |
|-------|--------|-----------|-------------------|
| Fat, protein, ash, moisture | External lab (ECCA) | 1 composite per 5 batches | Recalculate with internal NaCl/water data. Non-conform: notify LRO + PHA, block lot in ATUM |
| Microbiology | External lab (ECCA) | Every 5th batch | Conform: release all 5 batches. Non-conform: block in ATUM, notify PHA + LRO + logistics, assign non-feed-grade lot |

## Lot System (ATUM)

All batches are registered in the ATUM traceability system:

- **Product registration:** Provifeed Nannoprime/Isoprime with specifications per TDS
- **Lot number assignment:** Assigned upon batch entry
- **Microbiology and metals:** YES/NO test recorded
- **Release workflow:**
  - Filled bags stored in holding area pending external analysis
  - Conform results: data entered in ATUM, lot released, bags moved to hall (released product storage)
  - Non-conform results: lot blocked in ATUM, new lot number under non-feed-grade category, non-feed label applied

## Storage Conditions

| Storage Stage | Location | Conditions |
|---------------|----------|------------|
| Pending release | Holding area ("hokje") | Awaiting external analysis results |
| Released product | Production hall (stockage) | Ambient, dry storage |
| Samples | Laboratory refrigerator | Refrigerated |
| Paste (pre-drying) | Cool room (T7/T8/T9) | Refrigerated |

## Batch Numbering

Format: `AAA-YYYYMMDD-BBB`

| Field | Description | Example |
|-------|-------------|---------|
| AAA | Algae number | 092 (Haematococcus Lacustris/Pluvialis) |
| YYYYMMDD | Date | 20241126 |
| BBB | Sequential batch number | 6 |

When recording in SCADA (CHU external menu), both the product type (including strain, e.g., K0084 vs SAG 192.80) and the batch number must be set correctly before pressing "Report and Adjust level now".

## Roles

| Role | Responsibility |
|------|---------------|
| Operator | Sample collection, form completion, ATUM entry |
| LRO | Spot-check internal calculations, review deviations |
| PHA | Notified on non-conformities |
| External lab (ECCA) | Fat, protein, ash, moisture, microbiology analysis |

## Gaps

- Bag/package sizes and materials (vacuum sealed, inert gas, etc.)
- Shelf life specifications per product type
- Labeling requirements (regulatory, nutritional)
- Maximum storage duration in holding area before forced decision
- Temperature and humidity specifications for released product storage
- Shipping and transport requirements
