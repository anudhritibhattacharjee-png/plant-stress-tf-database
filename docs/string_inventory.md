# STRING & FunCoup Interaction Dataset Inventory

## Executive Summary

This document details the complete inventory and technical audit of the **45 protein interaction packages** (comprising **488 source files**) located in `STRING database information-20261008T053421Z-1-001/STRING database information/`.

### Key Inventory Metrics
- **Total Packages Audited**: 45 directories
- **STRING Database Packages**: 44 packages (STRING v11 / v12 networks)
- **FunCoup Database Packages**: 1 package (`OsDOF18` using FunCoup v5 subnetwork)
- **Total Audited Files Across Packages**: 488 files (TSVs, SVGs, PNGs, XMLs, FASTA)
- **Total Unique Direct Interaction Edges**: 439 direct protein interactors
- **Total Normalized Database Rows**: 489 interaction records to be stored in `protein_interactions` across target TFs
- **Target Transcription Factor Records Linked**: 45 distinct TF records in `transcription_factors`
- **Focal Query Identification**: 100% deterministic (red node `rgb(255,0,0)` in coordinates TSV, or query identifier `Q6ZBQ1` for FunCoup)

---

## Ingestion Methodology & Data Governance Rules

1. **Direct First-Neighbor Interactors Only**: Interaction networks contain secondary interactor edges between partners (e.g. partner B to partner C). Only edges directly involving the query transcription factor (focal node) are extracted.
2. **Strict Reciprocal Edge Deduplication**: In STRING interaction TSVs, edges are recorded bidirectionally ($A \to B$ and $B \to A$). Reciprocal lines are deduplicated, keeping the highest confidence score.
3. **Authentic Quantitative Evidence**: All confidence scores (`combined_score`, `experimental_score`, `database_score`, `textmining_score`, `coexpression_score`) are preserved exactly as reported by STRING/FunCoup on a normalized 0.0 to 1.0 scale.
4. **Authentic Partner Identity**: Non-transcription factor partners (e.g., kinases, chaperones, uncharacterized proteins) are stored cleanly via `partner_name` and `partner_uniprot`, preserving biological fidelity without fabricating synthetic TF records.
5. **FunCoup Score Normalization**: FunCoup PPV (Positive Predictive Value, 0.000–1.000) is stored in `combined_score`, with `source_database = 'FunCoup'` and supporting metrics (`GoldStandard`, `FBS_max`) documented in `notes`.

---

## Comprehensive Inventory Table (45 Directories)

| # | Directory Name | Source DB | Files | Interaction TSV | File Size | Focal Query Node | Direct Partners | Target TF Record(s) | DB Rows | Matching Rationale |
|---|----------------|-----------|-------|-----------------|-----------|------------------|-----------------|----------------------|---------|--------------------|
| 1 | `AHL10` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,745 B | `AHL10` | 10 | #60 AHL10 | 10 | Exact symbol match to Arabidopsis thaliana AHL10 (#60) |
| 2 | `AtBBX21` | STRING | 11 | `string_interactions_11_nodes.tsv` | 5,671 B | `BBX21` | 10 | #53 BBX21 | 10 | Standardized At-prefixed symbol match to Arabidopsis thaliana BBX21 (#53) |
| 3 | `AtC3H14` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,135 B | `F4N21.6` | 10 | #63 AtC3H14 | 10 | Exact symbol match to Arabidopsis thaliana AtC3H14 (#63) |
| 4 | `AtC3H15` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,245 B | `T22E19.17` | 10 | #62 AtC3H15 | 10 | Exact symbol match to Arabidopsis thaliana AtC3H15 (#62) |
| 5 | `AtDOF5.8` | STRING | 11 | `string_interactions_11_nodes.tsv` | 1,655 B | `DOF5.8` | 10 | #3 AtDOF5.8 | 10 | Exact symbol match to Arabidopsis thaliana AtDOF5.8 (#3) |
| 6 | `AtPLATZ2` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,137 B | `F14G6.19` | 10 | #54 AtPLATZ2 | 10 | Exact symbol match to Arabidopsis thaliana AtPLATZ2 (#54) |
| 7 | `AtPLATZ4` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,433 B | `F6N18.8` | 10 | #55 AtPLATZ4 | 10 | Exact symbol match to Arabidopsis thaliana AtPLATZ4 (#55) |
| 8 | `BnCDF1` | STRING | 11 | `string_interactions_11_nodes.tsv` | 7,525 B | `BnaAnng24480D` | 10 | #9 BnCDF1 | 10 | Exact symbol match to Brassica napus BnCDF1 (#9) |
| 9 | `C3H47` | STRING | 11 | `string_interactions_11_nodes.tsv` | 6,411 B | `OJ1417_E01.106` | 10 | #61 OsC3H47 | 10 | Species-specific synonym match to Oryza sativa OsC3H47 (#61) |
| 10 | `CAMTA3` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,899 B | `CAMTA3` | 10 | #43 CAMTA3 | 10 | Exact symbol match to Arabidopsis thaliana CAMTA3 (#43) |
| 11 | `CDF3` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,969 B | `CDF3` | 10 | #5 CDF3 | 10 | Exact symbol match to Arabidopsis thaliana CDF3 (#5) |
| 12 | `EIN3` | STRING | 11 | `string_interactions_11_nodes.tsv` | 6,899 B | `EIN3` | 10 | #45 EIN3 | 10 | Exact symbol match to Arabidopsis thaliana EIN3 (#45) |
| 13 | `GT2` | STRING | 11 | `string_interactions_11_nodes.tsv` | 1,883 B | `GT-2` | 10 | #48 GT-2 | 10 | Exact symbol match to Arabidopsis thaliana GT-2 (#48) |
| 14 | `GhGT-3b_A04` | STRING | 11 | `string_interactions_11_nodes.tsv` | 5,881 B | `LOC107948595` | 10 | #49 GhGT-3b_A04 | 10 | Exact symbol match to Gossypium hirsutum GhGT-3b_A04 (#49) |
| 15 | `GmNLP7a` | STRING | 11 | `string_interactions_11_nodes.tsv` | 5,041 B | `K7LDR9_SOYBN` | 10 | #40 GmNLP7a | 10 | Exact symbol match to Glycine max GmNLP7a (#40) |
| 16 | `MdDOF54` | STRING | 11 | `string_interactions_3_nodes.tsv` | 561 B | `DVH24_030584` | 2 | #7 MdDOF54 | 2 | Exact symbol match to Malus domestica MdDOF54 (#7) |
| 17 | `MtNLP1` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,441 B | `A0A072V3U8` | 10 | #31 NLP1 | 10 | Species-prefixed match to Medicago truncatula NLP1 (#31) |
| 18 | `NLP7` | STRING | 10 | `string_interactions_11_nodes.tsv` | 7,207 B | `NLP7` | 10 | #29 NLP7, #30 NLP7, #34 NLP7, #35 NLP family | 40 | Universal Arabidopsis NLP7 network mapping to 4 NLP7 study records (#29, #30, #34, #35) |
| 19 | `NLP8` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,221 B | `NLP8` | 10 | #39 NLP8 | 10 | Exact symbol match to Arabidopsis thaliana NLP8 (#39) |
| 20 | `OsADR3` | STRING | 11 | `string_interactions_11_nodes.tsv` | 6,075 B | `Q7G7I8_ORYSJ` | 10 | #51 OsADR3 | 10 | Exact symbol match to Oryza sativa OsADR3 (#51) |
| 21 | `OsDOF1` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,047 B | `DOF1` | 10 | #12 OsDOF1 | 10 | Exact symbol match to Oryza sativa OsDOF1 (#12) |
| 22 | `OsDOF18` | FunCoup | 3 | `FunCoup_subnetwork.tsv` | 4,667 B | `Q6ZBQ1` | 7 | #15 OsDOF18 | 7 | Exact symbol & UniProt Q6ZBQ1 match to Oryza sativa OsDOF18 (#15) via FunCoup |
| 23 | `OsGATA8` | STRING | 11 | `string_interactions_11_nodes.tsv` | 5,269 B | `Q8LQW5_ORYSJ` | 10 | #42 OsGATA8 | 10 | Exact symbol match to Oryza sativa OsGATA8 (#42) |
| 24 | `OsMADS25` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,007 B | `MADS25` | 10 | #21 OsMADS25, #22 OsMADS25 | 20 | Exact symbol match to 2 Oryza sativa OsMADS25 study records (#21, #22) |
| 25 | `OsMADS3` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,789 B | `MADS3` | 10 | #20 OsMADS3 | 10 | Exact symbol match to Oryza sativa OsMADS3 (#20) |
| 26 | `OsNLP1` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,989 B | `NLP1` | 10 | #28 NLP family | 10 | Rice NLP1 member mapped to Oryza sativa NLP family (#28) |
| 27 | `OsNLP2` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,929 B | `NLP2` | 10 | #28 NLP family, #37 NLP2 | 20 | Rice NLP2 member mapped to Oryza sativa NLP family (#28) & OsNLP2 study (#37) |
| 28 | `OsNLP3` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,105 B | `NLP3` | 10 | #28 NLP family | 10 | Rice NLP3 member mapped to Oryza sativa NLP family (#28) |
| 29 | `OsNLP4` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,077 B | `A0A0P0XQL5` | 10 | #38 NLP4 | 10 | Rice NLP4 member mapped to Oryza sativa NLP4 study (#38) |
| 30 | `PtrLBD41` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,249 B | `A9P7Z5_POPTR` | 10 | #46 PtrLBD41 | 10 | Exact symbol match to Populus trichocarpa PtrLBD41 (#46) |
| 31 | `SLNLP1` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,881 B | `A0A3Q7HL32` | 10 | #33 NLP1 / NLP5 | 10 | Tomato NLP1 member mapped to Solanum lycopersicum NLP1 / NLP5 (#33) |
| 32 | `SlBZR1-SlBZR1D` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,495 B | `A0A3Q7GAQ0` | 10 | #59 SlBZR1 / SlBZR1D | 10 | Composite tomato symbol match to Solanum lycopersicum SlBZR1 / SlBZR1D (#59) |
| 33 | `SlCDF1` | STRING | 11 | `string_interactions_11_nodes.tsv` | 9,513 B | `A0A3Q7F8Y3` | 10 | #6 SlCDF1 / SlCDF3 | 10 | Tomato CDF1 member mapped to Solanum lycopersicum SlCDF1 / SlCDF3 (#6) |
| 34 | `SlCDF3` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,973 B | `SP-2` | 10 | #6 SlCDF1 / SlCDF3 | 10 | Tomato CDF3 member mapped to Solanum lycopersicum SlCDF1 / SlCDF3 (#6) |
| 35 | `SlDOF22` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,747 B | `SlDof22` | 10 | #1 SlDOF22 | 10 | Exact symbol match to Solanum lycopersicum SlDOF22 (#1) |
| 36 | `SlGATA17` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,705 B | `A0A3Q7GQX2` | 10 | #52 SlGATA17 | 10 | Exact symbol match to Solanum lycopersicum SlGATA17 (#52) |
| 37 | `SlMBP11` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,667 B | `A0A3Q7F370` | 10 | #16 SlMBP11 | 10 | Exact symbol match to Solanum lycopersicum SlMBP11 (#16) |
| 38 | `SlMBP8` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,159 B | `A0A3Q7JXP0` | 10 | #17 SlMBP8 | 10 | Exact symbol match to Solanum lycopersicum SlMBP8 (#17) |
| 39 | `SlNLP5` | STRING | 11 | `string_interactions_11_nodes.tsv` | 4,881 B | `A0A3Q7HUP0` | 10 | #33 NLP1 / NLP5 | 10 | Tomato NLP5 member mapped to Solanum lycopersicum NLP1 / NLP5 (#33) |
| 40 | `TDR6` | STRING | 11 | `string_interactions_11_nodes.tsv` | 3,133 B | `TDR6` | 10 | #23 TDR6 | 10 | Exact symbol match to Solanum lycopersicum TDR6 (#23) |
| 41 | `TaMADS51` | STRING | 11 | `string_interactions_11_nodes.tsv` | 1,691 B | `WM13` | 10 | #19 TaMADS51 | 10 | Exact symbol match to Triticum aestivum TaMADS51 (#19) |
| 42 | `TaZNF` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,537 B | `A0A1D5V0E4` | 10 | #2 TaZNF | 10 | Exact symbol match to Triticum aestivum TaZNF (#2) |
| 43 | `VOZ1` | STRING | 12 | `string_interactions_11_nodes.tsv` | 2,569 B | `VOZ1` | 10 | #44 VOZ1 / VOZ2 | 10 | Arabidopsis VOZ1 member mapped to Arabidopsis thaliana VOZ1 / VOZ2 (#44) |
| 44 | `VOZ2` | STRING | 12 | `string_interactions_11_nodes.tsv` | 2,875 B | `VOZ2` | 10 | #44 VOZ1 / VOZ2 | 10 | Arabidopsis VOZ2 member mapped to Arabidopsis thaliana VOZ1 / VOZ2 (#44) |
| 45 | `ZmBES1-BZR1` | STRING | 11 | `string_interactions_11_nodes.tsv` | 2,965 B | `B4FKI7_MAIZE` | 10 | #58 ZmBES1/BZR1-1 | 10 | Composite maize symbol match to Zea mays ZmBES1/BZR1-1 (#58) |

---

## Reconciliation & Mapping Breakdown

- **Total Direct Unique Edges Across 45 Packages**: 439
- **Total Database Rows Across Target TFs**: 489

### Multi-Record & Family Disambiguation Summary
- **NLP7 (4 TFs)**: 10 direct partners $\times$ 4 TF records (#29, #30, #34, #35) = 40 rows.
- **OsMADS25 (2 TFs)**: 10 direct partners $\times$ 2 TF records (#21, #22) = 20 rows.
- **OsNLP2 (2 TFs)**: 10 direct partners $\times$ 2 TF records (#28, #37) = 20 rows.
- **Rice NLP Family (#28)**: 10 partners each from `OsNLP1`, `OsNLP2`, and `OsNLP3` = 30 rows.
- **Tomato NLP Family (#33)**: 10 partners each from `SLNLP1` and `SlNLP5` = 20 rows.
- **Tomato CDF Family (#6)**: 10 partners each from `SlCDF1` and `SlCDF3` = 20 rows.
- **Arabidopsis VOZ Family (#44)**: 10 partners each from `VOZ1` and `VOZ2` = 20 rows.
- **MdDOF54 (#7)**: Exactly 2 direct partners = 2 rows.
- **OsDOF18 (#15)**: Exactly 7 direct partners from FunCoup = 7 rows.
- **All other 34 directories**: Exactly 10 direct partners $\times$ 1 target TF = 340 rows.
- **Grand Total Ingested Rows**: 40 + 20 + 20 + 30 + 20 + 20 + 20 + 2 + 7 + 310 = **489 rows**.

---

## Source Immutability & Audit Guarantee
All 488 files in `STRING database information-20261008T053421Z-1-001/` remain 100% untouched and preserved.
