# Cytoscape Asset Audit and Integration Verification

## Executive Summary

This document provides a comprehensive technical audit of the **32 visual network diagram assets** located in `Cytoscape protein interactions-20261008T053406Z-1-001/Cytoscape protein interactions/`.

> [!IMPORTANT]
> **Strict Policy on Cytoscape Assets: Inspection and Visual Linking Only**
> 1. **Zero Structured Network Data**: The Cytoscape directory contains exclusively PNG raster image files (`.png`). It contains **0 structured network files** (such as `.cys`, `.xgmml`, `.sif`, `.tsv`, `.json`, or `.xml`).
> 2. **No Interaction Fabrication**: Under no circumstances are protein-protein interactions (PPI), edge scores, or partner nodes inferred or fabricated from visual PNG diagrams alone.
> 3. **Authentic Quantitative Evidence**: All quantitative interaction scores (combined confidence score, experimental score, database score, textmining score, and coexpression score) are ingested strictly from authoritative TSV datasets in `STRING database information/` (STRING v11/v12 and FunCoup v5).
> 4. **Visual Diagram Linkage**: The verified Cytoscape PNG image paths are linked into the normalized `protein_interactions` database table as `cytoscape_image_path` to power high-resolution network visualizers in the UI.

---

## Inventory & Concordance Table (32 PNG Files)

| # | Cytoscape Image File | Dimensions | Size (Bytes) | SHA-256 Hash | Mapped STRING Directory | Target TF ID(s) & Name | Plant Species |
|---|----------------------|------------|--------------|--------------|-------------------------|------------------------|---------------|
| 1 | `AHL10.png` | 600x533 | 76,268 | `a27858f9085a4b96...` | `AHL10` | #60 AHL10 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 2 | `AtC3H14.png` | 600x533 | 78,777 | `3ddedb5fb311abca...` | `AtC3H14` | #63 AtC3H14 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 3 | `AtC3H15.png` | 600x533 | 99,265 | `8006029830477a69...` | `AtC3H15` | #62 AtC3H15 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 4 | `AtDOF5.8.png` | 600x354 | 31,500 | `3e8ed755716ad2b8...` | `AtDOF5.8` | #3 AtDOF5.8 | Arabidopsis thaliana (Arabidopsis) |
| 5 | `AtNLP8.png` | 600x368 | 50,139 | `8510549ff007e14f...` | `NLP8` | #39 NLP8 | Arabidopsis thaliana (Arabidopsis) |
| 6 | `AtPLATZ2.png` | 600x533 | 78,502 | `fd9e54789e1de7ca...` | `AtPLATZ2` | #54 AtPLATZ2 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 7 | `AtPLATZ4.png` | 600x533 | 84,199 | `14794e9d9a2e4771...` | `AtPLATZ4` | #55 AtPLATZ4 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 8 | `BZR1.png` | 600x533 | 47,986 | `6df5bc579ab63170...` | `ZmBES1-BZR1` | #58 ZmBES1/BZR1-1 | Zea mays (Zea mays) |
| 9 | `BnCDF1 similar protein.png` | 608x498 | 69,285 | `62880920f62f7e91...` | `BnCDF1` | #9 BnCDF1 | Brassica napus (Brassica) |
| 10 | `CAMTA3.png` | 600x533 | 113,509 | `779e57055c9691d1...` | `CAMTA3` | #43 CAMTA3 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 11 | `EIN3.png` | 600x533 | 124,860 | `e963381ccebc6f20...` | `EIN3` | #45 EIN3 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 12 | `MtNLP1.png` | 600x368 | 38,953 | `a14ee38f43b7fb92...` | `MtNLP1` | #31 NLP1 | Medicago truncatula (Medicago truncatula) |
| 13 | `NLP1.png` | 600x368 | 87,836 | `9e4b18c4f0eb12bc...` | `OsNLP1` | #28 NLP family | Oryza sativa (Rice) |
| 14 | `NLP2.png` | 600x368 | 76,140 | `71ffb65c5c5ba7a9...` | `OsNLP2` | #28 NLP family, #37 NLP2 | Oryza sativa (Rice) |
| 15 | `NLP3.png` | 600x368 | 75,754 | `506f6b216749c21e...` | `OsNLP3` | #28 NLP family | Oryza sativa (Rice) |
| 16 | `NLP7.png` | 600x368 | 80,791 | `3141c305e25c25c0...` | `NLP7` | #29 NLP7, #30 NLP7, #34 NLP7, #35 NLP family | Arabidopsis thaliana (Arabidopsis) |
| 17 | `OsADR3.png` | 600x533 | 79,552 | `bfbe77f0682c3d68...` | `OsADR3` | #51 OsADR3 | Oryza sativa (Rice) |
| 18 | `OsC3H47.png` | 600x533 | 124,457 | `a2aff1e2dea16a75...` | `C3H47` | #61 OsC3H47 | rice (Oryza sativa) |
| 19 | `OsDOF1 similar protein.png` | 600x354 | 62,890 | `9d76ed4c103f0c96...` | `OsDOF1` | #12 OsDOF1 | Oryza sativa (Rice) |
| 20 | `OsDOF18.png` | 4585x2780 | 1,205,833 | `b50e8ae2bf076e73...` | `OsDOF18` | #15 OsDOF18 | Oryza sativa (Rice) |
| 21 | `OsMADS25.png` | 600x368 | 33,152 | `fba1292af46249df...` | `OsMADS25` | #21 OsMADS25, #22 OsMADS25 | Oryza sativa (Rice) |
| 22 | `OsMADS3.png` | 600x368 | 61,200 | `676983783b3c8217...` | `OsMADS3` | #20 OsMADS3 | Oryza sativa (Rice) |
| 23 | `OsNLP4.png` | 600x368 | 62,778 | `9b30845a931e4069...` | `OsNLP4` | #38 NLP4 | Oryza sativa (Rice) |
| 24 | `SlMBP11.png` | 600x368 | 31,201 | `70248766fa6d022c...` | `SlMBP11` | #16 SlMBP11 | Solanum lycopersicum (Tomato) |
| 25 | `SlMBP8.png` | 600x368 | 24,843 | `031c65c0074a08c3...` | `SlMBP8` | #17 SlMBP8 | Solanum lycopersicum (Tomato) |
| 26 | `SlNLP1.png` | 600x368 | 48,625 | `6d100bc09b01355a...` | `SLNLP1` | #33 NLP1 / NLP5 | Solanum lycopersicum (Tomato) |
| 27 | `SlNLP5.png` | 600x368 | 48,514 | `2407a4e2aa6aad7a...` | `SlNLP5` | #33 NLP1 / NLP5 | Solanum lycopersicum (Tomato) |
| 28 | `TDR6.png` | 600x368 | 23,834 | `5117f11a26725412...` | `TDR6` | #23 TDR6 | Solanum lycopersicum (Tomato) |
| 29 | `TaMADS51 similar protein.png` | 600x368 | 38,615 | `90bf7f206895d4c9...` | `TaMADS51` | #19 TaMADS51 | Triticum aestivum (Wheat) |
| 30 | `TaZNF.png` | 608x498 | 51,412 | `4a0526537e5094a3...` | `TaZNF` | #2 TaZNF | Triticum aestivum (Wheat) |
| 31 | `VOZ1.png` | 600x533 | 67,210 | `517981958c8c0020...` | `VOZ1` | #44 VOZ1 / VOZ2 | Arabidopsis thaliana (Arabidopsis thaliana) |
| 32 | `VOZ2.png` | 600x533 | 76,163 | `eec543b3a99cb92e...` | `VOZ2` | #44 VOZ1 / VOZ2 | Arabidopsis thaliana (Arabidopsis thaliana) |

---

## Analysis of STRING Directories Without Cytoscape PNGs

Of the **45 STRING packages**, **32 packages** correspond to a dedicated Cytoscape visual diagram. The remaining **13 packages** do not have a separate Cytoscape PNG export; their interactions are fully supported by high-resolution STRING evidence diagrams (`string_evidence_network_hires_11_nodes.png` / `FunCoup_subnetwork.png`) stored within their respective directories:

1. `AtBBX21` (TF #53: *Arabidopsis thaliana* `BBX21`)
2. `CDF3` (TF #5: *Arabidopsis thaliana* `CDF3`)
3. `GT2` (TF #48: *Arabidopsis thaliana* `GT-2`)
4. `GhGT-3b_A04` (TF #49: *Gossypium hirsutum* `GhGT-3b_A04`)
5. `GmNLP7a` (TF #40: *Glycine max* `GmNLP7a`)
6. `MdDOF54` (TF #7: *Malus domestica* `MdDOF54`)
7. `OsGATA8` (TF #42: *Oryza sativa* `OsGATA8`)
8. `PtrLBD41` (TF #46: *Populus trichocarpa* `PtrLBD41`)
9. `SlBZR1-SlBZR1D` (TF #59: *Solanum lycopersicum* `SlBZR1 / SlBZR1D` — Note: `BZR1.png` is specifically maize `ZmBES1-BZR1` as verified by `B4FKI7_MAIZE` focal node)
10. `SlCDF1` (TF #6: *Solanum lycopersicum* `SlCDF1 / SlCDF3`)
11. `SlCDF3` (TF #6: *Solanum lycopersicum* `SlCDF1 / SlCDF3`)
12. `SlDOF22` (TF #1: *Solanum lycopersicum* `SlDOF22`)
13. `SlGATA17` (TF #52: *Solanum lycopersicum* `SlGATA17`)

For these 13 packages, `protein_interactions.cytoscape_image_path` is cleanly stored as `NULL`, while `protein_interactions.string_image_path` points to the authentic native STRING/FunCoup network diagram.

---

## Verification Integrity & Immutability

- **Directory Integrity**: All 32 Cytoscape PNG files remain bit-for-bit identical to their source archive.
- **Permissions**: Read-only inspection; no files were modified, moved, renamed, or deleted.
- **Audit Date**: 2026-10-26
