# PhytoStress TF Atlas — AlphaFold Structure Asset Inventory

**Version:** 1.0  
**Phase:** Phase 5C (AlphaFold Structure Ingestion & Validation)  
**Status:** Validated Baseline Inventory  
**Source Root:** `AlphaFold -20261008T053401Z-1-001/`  
**Total Physical Files Inventoried:** 303  

---

## 1. Executive Summary & Asset Hierarchy

A recursive audit of `AlphaFold -20261008T053401Z-1-001/` identified **exactly 303 physical files** organized into **12 distinct transcription factor prediction suites**. Each suite corresponds to a complete ColabFold / AlphaFold2-ptm run comprising 5 ranked 3D coordinate PDB models, per-model score JSONs, PAE matrix JSONs, diagnostic evaluation PNG plots (pLDDT, PAE, MSA Coverage), execution logs, alignment files, and local MSA search caches.

### Comprehensive File Type Breakdown

| Asset Category | File Extension | File Count | Primary Function in PhytoStress Atlas |
| :--- | :---: | :---: | :--- |
| **3D Coordinate Structures** | `.pdb` | **60** | Atomic coordinates (Ranks 1 to 5 for each of 12 TFs); B-factor column contains per-residue pLDDT. |
| **Diagnostic Evaluation Plots** | `.png` | **36** | High-resolution visual metrics (12 pLDDT plots, 12 PAE plots, 12 MSA coverage plots). |
| **Confidence & Error Metrics** | `.json` | **84** | 60 rank score files (per-residue pLDDT, max PAE, pTM), 12 PAE matrix files, 12 run config files. |
| **Sequence & Target Summaries** | `.csv` | **12** | Input query FASTA sequence and ColabFold job header identifiers. |
| **Execution Logs & Metadata** | `.txt`, `.bibtex` | **36** | 12 execution logs (`log.txt`), 12 completion flags (`*.done.txt`), 12 citation packages (`cite.bibtex`). |
| **Multiple Sequence Alignments**| `.a3m` | **38** | 12 top-level query MSAs + 26 environment database MSAs (`bfd`, `uniref`). |
| **MSA Environment & Tooling** | `.gz`, `.m8`, `.sh`| **37** | 13 cache archives (`out.tar.gz`), 12 PDB70 matches (`.m8`), 12 execution scripts (`msa.sh`). |
| **Total Asset Count** | *All* | **303** | 100% accounted for with zero exclusions. |

---

## 2. The 12 AlphaFold Prediction Suites & Deterministic TF Mappings

Every prediction suite was deterministically mapped to its parent transcription factor in `phytostress.db` by matching: (1) exact amino acid sequence concordance against `protein_sequences`, (2) UniProt/TAIR accession, and (3) approved gene symbol.

| # | Suite Identifier | Target TF | Plant Species | Seq. Len | PDB Models | Mean pLDDT (Rank 1) | Diagnostic Plots (PAE / pLDDT / Cov) | Template Homolog | Mapping Rule |
| :-: | :--- | :-: | :--- | :-: | :-: | :-: | :-: | :---: | :--- |
| 01 | `AHL10_f311a` | **#60 AHL10** | Arabidopsis thaliana | 351 AA | 5 ranks | 59.8 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 02 | `AtC3H14_781a4` | **#63 AtC3H14** | Arabidopsis thaliana | 310 AA | 5 ranks | 64.7 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 03 | `AtC3H15_262f9` | **#62 AtC3H15** | Arabidopsis thaliana | 307 AA | 5 ranks | 64.2 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 04 | `AtDOF58_7e6b1` | **#3 AtDOF5.8** | Arabidopsis | 225 AA | 5 ranks | 54.0 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 05 | `AtPLATZ2_5dbaf` | **#54 AtPLATZ2** | Arabidopsis thaliana | 245 AA | 5 ranks | 72.6 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 06 | `AtPLATZ4_e1c1e` | **#55 AtPLATZ4** | Arabidopsis thaliana | 213 AA | 5 ranks | 76.5 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 07 | `BBX21_15acd` | **#53 BBX21** | Potato (Solanum tube | 331 AA | 5 ranks | 58.4 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 08 | `BnCDF1` | **#9 BnCDF1** | Brassica | 292 AA | 5 ranks | 56.1 | Yes (3 PNGs) | `AtDOF5.8` | Rule A + Homolog Note |
| 09 | `CDF3_8413b` | **#5 CDF3** | Arabidopsis | 437 AA | 5 ranks | 84.2 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 10 | `GhGT3b_A04_be592` | **#49 GhGT-3b_A04** | Cotton (Gossypium hi | 273 AA | 5 ranks | 74.6 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 11 | `MdDOF54_cff3d` | **#7 MdDOF54** | Apple | 303 AA | 5 ranks | 50.6 | Yes (3 PNGs) | — | Rule A (Stem) + Seq 100% |
| 12 | `MtNLP1_95155` | **#31 NLP1** | Medicago truncatula | 934 AA | 5 ranks | 52.0 | Yes (3 PNGs) | — | Rule B (A0A977NVL6) + Seq 100% |

---

## 3. Complete 60-Structure PDB Coordinate Models Inventory

The table below details all 60 physical `.pdb` files that represent 3D molecular structures in the repository:

| # | Target TF | Model Suite | Rank | Filename | Size (B) | Atoms | Residues | Chains | Mean pLDDT | pTM | Status |
| :-: | :--- | :--- | :-: | :--- | :-: | :-: | :-: | :-: | :-: | :-: | :---: |
| 01 | #60 AHL10 | `AHL10_f311a` | Rank 1 | `AHL10_f311a_unrelaxed_rank_001...pdb` | 206,145 | 2,541 | 351 | A | 59.77 | 0.43 | Verified |
| 02 | #60 AHL10 | `AHL10_f311a` | Rank 2 | `AHL10_f311a_unrelaxed_rank_002...pdb` | 206,145 | 2,541 | 351 | A | 58.98 | 0.40 | Verified |
| 03 | #60 AHL10 | `AHL10_f311a` | Rank 3 | `AHL10_f311a_unrelaxed_rank_003...pdb` | 206,145 | 2,541 | 351 | A | 58.53 | 0.40 | Verified |
| 04 | #60 AHL10 | `AHL10_f311a` | Rank 4 | `AHL10_f311a_unrelaxed_rank_004...pdb` | 206,145 | 2,541 | 351 | A | 56.08 | 0.41 | Verified |
| 05 | #60 AHL10 | `AHL10_f311a` | Rank 5 | `AHL10_f311a_unrelaxed_rank_005...pdb` | 206,145 | 2,541 | 351 | A | 54.74 | 0.42 | Verified |
| 06 | #63 AtC3H14 | `AtC3H14_781a4` | Rank 1 | `AtC3H14_781a4_unrelaxed_rank_0...pdb` | 198,774 | 2,450 | 310 | A | 64.69 | 0.36 | Verified |
| 07 | #63 AtC3H14 | `AtC3H14_781a4` | Rank 2 | `AtC3H14_781a4_unrelaxed_rank_0...pdb` | 198,774 | 2,450 | 310 | A | 64.69 | 0.34 | Verified |
| 08 | #63 AtC3H14 | `AtC3H14_781a4` | Rank 3 | `AtC3H14_781a4_unrelaxed_rank_0...pdb` | 198,774 | 2,450 | 310 | A | 64.51 | 0.30 | Verified |
| 09 | #63 AtC3H14 | `AtC3H14_781a4` | Rank 4 | `AtC3H14_781a4_unrelaxed_rank_0...pdb` | 198,774 | 2,450 | 310 | A | 64.19 | 0.28 | Verified |
| 10 | #63 AtC3H14 | `AtC3H14_781a4` | Rank 5 | `AtC3H14_781a4_unrelaxed_rank_0...pdb` | 198,774 | 2,450 | 310 | A | 64.13 | 0.34 | Verified |
| 11 | #62 AtC3H15 | `AtC3H15_262f9` | Rank 1 | `AtC3H15_262f9_unrelaxed_rank_0...pdb` | 193,590 | 2,386 | 307 | A | 64.17 | 0.30 | Verified |
| 12 | #62 AtC3H15 | `AtC3H15_262f9` | Rank 2 | `AtC3H15_262f9_unrelaxed_rank_0...pdb` | 193,590 | 2,386 | 307 | A | 63.30 | 0.28 | Verified |
| 13 | #62 AtC3H15 | `AtC3H15_262f9` | Rank 3 | `AtC3H15_262f9_unrelaxed_rank_0...pdb` | 193,590 | 2,386 | 307 | A | 63.25 | 0.32 | Verified |
| 14 | #62 AtC3H15 | `AtC3H15_262f9` | Rank 4 | `AtC3H15_262f9_unrelaxed_rank_0...pdb` | 193,590 | 2,386 | 307 | A | 63.10 | 0.31 | Verified |
| 15 | #62 AtC3H15 | `AtC3H15_262f9` | Rank 5 | `AtC3H15_262f9_unrelaxed_rank_0...pdb` | 193,590 | 2,386 | 307 | A | 62.13 | 0.32 | Verified |
| 16 | #3 AtDOF5.8 | `AtDOF58_7e6b1` | Rank 1 | `AtDOF58_7e6b1_unrelaxed_rank_0...pdb` | 138,186 | 1,702 | 225 | A | 54.04 | 0.26 | Verified |
| 17 | #3 AtDOF5.8 | `AtDOF58_7e6b1` | Rank 2 | `AtDOF58_7e6b1_unrelaxed_rank_0...pdb` | 138,186 | 1,702 | 225 | A | 53.91 | 0.29 | Verified |
| 18 | #3 AtDOF5.8 | `AtDOF58_7e6b1` | Rank 3 | `AtDOF58_7e6b1_unrelaxed_rank_0...pdb` | 138,186 | 1,702 | 225 | A | 52.58 | 0.27 | Verified |
| 19 | #3 AtDOF5.8 | `AtDOF58_7e6b1` | Rank 4 | `AtDOF58_7e6b1_unrelaxed_rank_0...pdb` | 138,186 | 1,702 | 225 | A | 50.83 | 0.28 | Verified |
| 20 | #3 AtDOF5.8 | `AtDOF58_7e6b1` | Rank 5 | `AtDOF58_7e6b1_unrelaxed_rank_0...pdb` | 138,186 | 1,702 | 225 | A | 50.10 | 0.27 | Verified |
| 21 | #54 AtPLATZ2 | `AtPLATZ2_5dbaf` | Rank 1 | `AtPLATZ2_5dbaf_unrelaxed_rank_...pdb` | 157,302 | 1,938 | 245 | A | 72.57 | 0.58 | Verified |
| 22 | #54 AtPLATZ2 | `AtPLATZ2_5dbaf` | Rank 2 | `AtPLATZ2_5dbaf_unrelaxed_rank_...pdb` | 157,302 | 1,938 | 245 | A | 71.23 | 0.58 | Verified |
| 23 | #54 AtPLATZ2 | `AtPLATZ2_5dbaf` | Rank 3 | `AtPLATZ2_5dbaf_unrelaxed_rank_...pdb` | 157,302 | 1,938 | 245 | A | 70.89 | 0.57 | Verified |
| 24 | #54 AtPLATZ2 | `AtPLATZ2_5dbaf` | Rank 4 | `AtPLATZ2_5dbaf_unrelaxed_rank_...pdb` | 157,302 | 1,938 | 245 | A | 70.39 | 0.59 | Verified |
| 25 | #54 AtPLATZ2 | `AtPLATZ2_5dbaf` | Rank 5 | `AtPLATZ2_5dbaf_unrelaxed_rank_...pdb` | 157,302 | 1,938 | 245 | A | 69.83 | 0.58 | Verified |
| 26 | #55 AtPLATZ4 | `AtPLATZ4_e1c1e` | Rank 1 | `AtPLATZ4_e1c1e_unrelaxed_rank_...pdb` | 138,348 | 1,704 | 213 | A | 76.54 | 0.62 | Verified |
| 27 | #55 AtPLATZ4 | `AtPLATZ4_e1c1e` | Rank 2 | `AtPLATZ4_e1c1e_unrelaxed_rank_...pdb` | 138,348 | 1,704 | 213 | A | 75.43 | 0.62 | Verified |
| 28 | #55 AtPLATZ4 | `AtPLATZ4_e1c1e` | Rank 3 | `AtPLATZ4_e1c1e_unrelaxed_rank_...pdb` | 138,348 | 1,704 | 213 | A | 74.85 | 0.61 | Verified |
| 29 | #55 AtPLATZ4 | `AtPLATZ4_e1c1e` | Rank 4 | `AtPLATZ4_e1c1e_unrelaxed_rank_...pdb` | 138,348 | 1,704 | 213 | A | 74.73 | 0.63 | Verified |
| 30 | #55 AtPLATZ4 | `AtPLATZ4_e1c1e` | Rank 5 | `AtPLATZ4_e1c1e_unrelaxed_rank_...pdb` | 138,348 | 1,704 | 213 | A | 74.24 | 0.61 | Verified |
| 31 | #53 BBX21 | `BBX21_15acd` | Rank 1 | `BBX21_15acd_unrelaxed_rank_001...pdb` | 208,656 | 2,572 | 331 | A | 58.35 | 0.37 | Verified |
| 32 | #53 BBX21 | `BBX21_15acd` | Rank 2 | `BBX21_15acd_unrelaxed_rank_002...pdb` | 208,656 | 2,572 | 331 | A | 56.96 | 0.34 | Verified |
| 33 | #53 BBX21 | `BBX21_15acd` | Rank 3 | `BBX21_15acd_unrelaxed_rank_003...pdb` | 208,656 | 2,572 | 331 | A | 55.27 | 0.36 | Verified |
| 34 | #53 BBX21 | `BBX21_15acd` | Rank 4 | `BBX21_15acd_unrelaxed_rank_004...pdb` | 208,656 | 2,572 | 331 | A | 54.85 | 0.34 | Verified |
| 35 | #53 BBX21 | `BBX21_15acd` | Rank 5 | `BBX21_15acd_unrelaxed_rank_005...pdb` | 208,656 | 2,572 | 331 | A | 53.35 | 0.36 | Verified |
| 36 | #9 BnCDF1 | `BnCDF1` | Rank 1 | `AtDOF58_489cf_unrelaxed_rank_0...pdb` | 190,188 | 2,344 | 292 | A | 56.15 | 0.28 | Verified |
| 37 | #9 BnCDF1 | `BnCDF1` | Rank 2 | `AtDOF58_489cf_unrelaxed_rank_0...pdb` | 190,188 | 2,344 | 292 | A | 54.70 | 0.28 | Verified |
| 38 | #9 BnCDF1 | `BnCDF1` | Rank 3 | `AtDOF58_489cf_unrelaxed_rank_0...pdb` | 190,188 | 2,344 | 292 | A | 54.41 | 0.26 | Verified |
| 39 | #9 BnCDF1 | `BnCDF1` | Rank 4 | `AtDOF58_489cf_unrelaxed_rank_0...pdb` | 190,188 | 2,344 | 292 | A | 54.18 | 0.25 | Verified |
| 40 | #9 BnCDF1 | `BnCDF1` | Rank 5 | `AtDOF58_489cf_unrelaxed_rank_0...pdb` | 190,188 | 2,344 | 292 | A | 52.09 | 0.28 | Verified |
| 41 | #5 CDF3 | `CDF3_8413b` | Rank 1 | `CDF3_8413b_unrelaxed_rank_001_...pdb` | 284,553 | 3,509 | 437 | A | 84.16 | 0.84 | Verified |
| 42 | #5 CDF3 | `CDF3_8413b` | Rank 2 | `CDF3_8413b_unrelaxed_rank_002_...pdb` | 284,553 | 3,509 | 437 | A | 83.06 | 0.82 | Verified |
| 43 | #5 CDF3 | `CDF3_8413b` | Rank 3 | `CDF3_8413b_unrelaxed_rank_003_...pdb` | 284,553 | 3,509 | 437 | A | 81.68 | 0.82 | Verified |
| 44 | #5 CDF3 | `CDF3_8413b` | Rank 4 | `CDF3_8413b_unrelaxed_rank_004_...pdb` | 284,553 | 3,509 | 437 | A | 79.94 | 0.81 | Verified |
| 45 | #5 CDF3 | `CDF3_8413b` | Rank 5 | `CDF3_8413b_unrelaxed_rank_005_...pdb` | 284,553 | 3,509 | 437 | A | 78.53 | 0.80 | Verified |
| 46 | #49 GhGT-3b_A04 | `GhGT3b_A04_be592` | Rank 1 | `GhGT3b_A04_be592_unrelaxed_ran...pdb` | 184,680 | 2,276 | 273 | A | 74.59 | 0.43 | Verified |
| 47 | #49 GhGT-3b_A04 | `GhGT3b_A04_be592` | Rank 2 | `GhGT3b_A04_be592_unrelaxed_ran...pdb` | 184,680 | 2,276 | 273 | A | 73.54 | 0.40 | Verified |
| 48 | #49 GhGT-3b_A04 | `GhGT3b_A04_be592` | Rank 3 | `GhGT3b_A04_be592_unrelaxed_ran...pdb` | 184,680 | 2,276 | 273 | A | 73.51 | 0.45 | Verified |
| 49 | #49 GhGT-3b_A04 | `GhGT3b_A04_be592` | Rank 4 | `GhGT3b_A04_be592_unrelaxed_ran...pdb` | 184,680 | 2,276 | 273 | A | 72.61 | 0.40 | Verified |
| 50 | #49 GhGT-3b_A04 | `GhGT3b_A04_be592` | Rank 5 | `GhGT3b_A04_be592_unrelaxed_ran...pdb` | 184,680 | 2,276 | 273 | A | 70.67 | 0.39 | Verified |
| 51 | #7 MdDOF54 | `MdDOF54_cff3d` | Rank 1 | `MdDOF54_cff3d_unrelaxed_rank_0...pdb` | 192,375 | 2,371 | 303 | A | 50.59 | 0.27 | Verified |
| 52 | #7 MdDOF54 | `MdDOF54_cff3d` | Rank 2 | `MdDOF54_cff3d_unrelaxed_rank_0...pdb` | 192,375 | 2,371 | 303 | A | 49.81 | 0.25 | Verified |
| 53 | #7 MdDOF54 | `MdDOF54_cff3d` | Rank 3 | `MdDOF54_cff3d_unrelaxed_rank_0...pdb` | 192,375 | 2,371 | 303 | A | 48.51 | 0.26 | Verified |
| 54 | #7 MdDOF54 | `MdDOF54_cff3d` | Rank 4 | `MdDOF54_cff3d_unrelaxed_rank_0...pdb` | 192,375 | 2,371 | 303 | A | 47.80 | 0.28 | Verified |
| 55 | #7 MdDOF54 | `MdDOF54_cff3d` | Rank 5 | `MdDOF54_cff3d_unrelaxed_rank_0...pdb` | 192,375 | 2,371 | 303 | A | 47.45 | 0.26 | Verified |
| 56 | #31 NLP1 | `MtNLP1_95155` | Rank 1 | `MtNLP1_95155_unrelaxed_rank_00...pdb` | 583,524 | 7,200 | 934 | A | 51.99 | 0.40 | Verified |
| 57 | #31 NLP1 | `MtNLP1_95155` | Rank 2 | `MtNLP1_95155_unrelaxed_rank_00...pdb` | 583,524 | 7,200 | 934 | A | 51.58 | 0.35 | Verified |
| 58 | #31 NLP1 | `MtNLP1_95155` | Rank 3 | `MtNLP1_95155_unrelaxed_rank_00...pdb` | 583,524 | 7,200 | 934 | A | 50.42 | 0.35 | Verified |
| 59 | #31 NLP1 | `MtNLP1_95155` | Rank 4 | `MtNLP1_95155_unrelaxed_rank_00...pdb` | 583,524 | 7,200 | 934 | A | 49.80 | 0.34 | Verified |
| 60 | #31 NLP1 | `MtNLP1_95155` | Rank 5 | `MtNLP1_95155_unrelaxed_rank_00...pdb` | 583,524 | 7,200 | 934 | A | 49.63 | 0.36 | Verified |

---

## 4. Special Anomaly Audit & Biological Fidelity

### A. `BnCDF1` Template Homolog Handling
- **Condition:** Inside `AlphaFold/BnCDF1/`, the coordinate PDB files and plots are prefixed with `AtDOF58_489cf` (e.g. `AtDOF58_489cf_unrelaxed_rank_001_...pdb`).
- **Biological Verification:** The query sequence inside `AtDOF58_489cf.csv` is 292 AA, which matches the Brassica napus `BnCDF1.txt` sequence (TF #09) 100%. The ColabFold prediction utilized the homologous Arabidopsis `AtDOF5.8` template.
- **Resolution:** Retained and linked as the authentic structural model for Record #09 (`BnCDF1`), with `template_homolog = 'AtDOF5.8'` recorded explicitly in the database.

### B. `MtNLP1` Multi-Publication Disambiguation
- **Condition:** `data_mapping_report.md` Section 6 table listed `MtNLP1_95155` alongside both Record #31 (*M. truncatula*, Nature Plants 2018) and Record #32 (*M. truncatula*, Plant Comms 2021).
- **Biological Verification:** The modeled query sequence inside `MtNLP1_95155.csv` and the PDB coordinate models has length **934 AA**, matching Record #31 (`A0A977NVL6`) 100% bit-for-bit. Record #32 has a distinct sequence of length **909 AA** (`A0A072V3U8`).
- **Resolution:** `MtNLP1_95155` is assigned exclusively to Record #31 (`NLP1`, Nature Plants 2018) to preserve scientific accuracy and prevent false sequence-structure concordance. Record #32 is noted in the manual-review report.

---

## 5. Storage Architecture Decision (Safe Path Reference)

In accordance with Step 9 guidelines, raw multi-megabyte coordinate text is **not stored directly as BLOBs/TEXT inside SQLite**. Instead:
1. `pdb_file_path` stores the relative filesystem path to the valid `.pdb` file.
2. `pae_image_path`, `plddt_image_path`, and `coverage_image_path` store relative filesystem paths to diagnostic visual assets.
3. High-value quantitative metrics (`mean_plddt`, `rank_num`, `template_homolog`, `model_identifier`) are indexed directly in `protein_structures`.
4. Web frontend 3D molecular viewers (Mol*, 3Dmol.js) will stream structural coordinates via static file serving endpoints, ensuring sub-millisecond query performance and zero database bloat.
