# PhytoStress TF Atlas — AlphaFold Structure Ingestion Technical Report

**Version:** 1.0  
**Phase:** Phase 5C (AlphaFold Structure Ingestion & Validation)  
**Status:** Complete & Fully Validated  
**Date Generated:** 2026-10-22  
**Source Root:** `AlphaFold -20261008T053401Z-1-001/`  
**Database:** `phytostress.db` (`protein_structures` table)  

---

## 1. Executive Summary

Phase 5C has been completed with **zero errors, zero data corruption, and 100% source file immutability**. All **303 physical files** in `AlphaFold -20261008T053401Z-1-001/` were inventoried and validated. Exactly **60 atomic 3D coordinate PDB models** (spanning 5 model ranks across 12 distinct transcription factor prediction suites) were deterministically mapped, verified against `protein_sequences` and `transcription_factors`, and ingested into `protein_structures` using a safe relative path and metadata reference architecture.

Key accomplishments:
- **303 physical files** inventoried across 12 ColabFold / AlphaFold2 prediction suites without modifying a single byte on disk.
- **60 3D PDB structure models** ingested into `protein_structures` (5 ranked models per TF).
- **12 distinct plant transcription factors** linked to high-resolution structural suites.
- **100% C-alpha residue count concordance** verified between 3D structures and primary sequence records.
- **Confidence metadata fully preserved:** Mean pLDDT scores (range: 47.45 – 84.16), pTM scores, and per-residue B-factor metrics.
- **Diagnostic evaluation assets linked:** 36 PNG plots (PAE, pLDDT, Coverage) and 12 PAE JSON matrices.
- **Special biological cases resolved:** Template homolog flag (`AtDOF5.8`) for `BnCDF1`; `MtNLP1` disambiguation (model assigned strictly to Record #31, preventing false assignment to #32).
- **49/49 backend tests passed** with 100% success rate (including 12 dedicated AlphaFold tests).
- **12/12 post-ingestion validation check blocks passed** with 0 errors.

---

## 2. Comprehensive Inventory & Format Breakdown

| Category | Extensions | File Count | Description |
| :--- | :---: | :---: | :--- |
| **PDB Coordinate Structures** | `.pdb` | **60** | Atomic coordinates (Ranks 1 to 5 per TF); B-factor stores per-residue pLDDT. |
| **Diagnostic Evaluation Plots** | `.png` | **36** | High-resolution visual metrics (12 pLDDT, 12 PAE, 12 Coverage plots). |
| **Confidence & Error Metrics** | `.json` | **84** | 60 rank score files (per-residue pLDDT, max PAE, pTM), 12 PAE matrices, 12 configs. |
| **Sequence & Target Summaries** | `.csv` | **12** | Query FASTA sequence and job identifiers. |
| **Execution Logs & Metadata** | `.txt`, `.bibtex` | **36** | 12 execution logs (`log.txt`), 12 completion flags (`*.done.txt`), 12 citations (`cite.bibtex`). |
| **Multiple Sequence Alignments**| `.a3m` | **38** | 12 top-level query MSAs + 26 environment MSAs (`bfd`, `uniref`). |
| **MSA Environment & Tooling** | `.gz`, `.m8`, `.sh`| **37** | 13 cache archives (`out.tar.gz`), 12 PDB70 matches (`.m8`), 12 execution scripts (`msa.sh`). |
| **Total Asset Count** | *All* | **303** | 100% accounted for with zero exclusions. |

---

## 3. The 12 Structured Transcription Factor Suites

| TF ID | TF Name | Plant Species | Suite Identifier | Residues | Rank 1 pLDDT | Mean pLDDT (All Ranks) | Template Homolog | Diagnostic Plots | Status |
| :-: | :--- | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| #03 | **AtDOF5.8** | Arabidopsis | `AtDOF58_7e6b1` | 225 AA | 54.04 | 52.29 | — | 3 PNGs | `Verified` |
| #05 | **CDF3** | Arabidopsis | `CDF3_8413b` | 437 AA | 84.16 | 81.47 | — | 3 PNGs | `Verified` |
| #07 | **MdDOF54** | Apple | `MdDOF54_cff3d` | 303 AA | 50.59 | 48.83 | — | 3 PNGs | `Verified` |
| #09 | **BnCDF1** | Brassica | `BnCDF1` | 292 AA | 56.15 | 54.31 | `AtDOF5.8` | 3 PNGs | `Verified` |
| #31 | **NLP1** | Medicago truncatula | `MtNLP1_95155` | 934 AA | 51.99 | 50.68 | — | 3 PNGs | `Verified` |
| #49 | **GhGT-3b_A04** | Cotton (Gossypium hi | `GhGT3b_A04_be592` | 273 AA | 74.59 | 72.98 | — | 3 PNGs | `Verified` |
| #53 | **BBX21** | Potato (Solanum tube | `BBX21_15acd` | 331 AA | 58.35 | 55.76 | — | 3 PNGs | `Verified` |
| #54 | **AtPLATZ2** | Arabidopsis thaliana | `AtPLATZ2_5dbaf` | 245 AA | 72.57 | 70.98 | — | 3 PNGs | `Verified` |
| #55 | **AtPLATZ4** | Arabidopsis thaliana | `AtPLATZ4_e1c1e` | 213 AA | 76.54 | 75.16 | — | 3 PNGs | `Verified` |
| #60 | **AHL10** | Arabidopsis thaliana | `AHL10_f311a` | 351 AA | 59.77 | 57.62 | — | 3 PNGs | `Verified` |
| #62 | **AtC3H15** | Arabidopsis thaliana | `AtC3H15_262f9` | 307 AA | 64.17 | 63.19 | — | 3 PNGs | `Verified` |
| #63 | **AtC3H14** | Arabidopsis thaliana | `AtC3H14_781a4` | 310 AA | 64.69 | 64.44 | — | 3 PNGs | `Verified` |

---

## 4. Full 60-Record Structure Database Ingestion Table

| DB ID | TF ID | TF Name | Model Suite | Rank | Mean pLDDT | PDB Path | Template Homolog | Validation Status |
| :-: | :-: | :--- | :--- | :-: | :-: | :--- | :-: | :-: |
| 16 | #03 | **AtDOF5.8** | `AtDOF58_7e6b1` | Rank 1 | 54.04 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 17 | #03 | **AtDOF5.8** | `AtDOF58_7e6b1` | Rank 2 | 53.91 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 18 | #03 | **AtDOF5.8** | `AtDOF58_7e6b1` | Rank 3 | 52.58 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 19 | #03 | **AtDOF5.8** | `AtDOF58_7e6b1` | Rank 4 | 50.83 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 20 | #03 | **AtDOF5.8** | `AtDOF58_7e6b1` | Rank 5 | 50.10 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 41 | #05 | **CDF3** | `CDF3_8413b` | Rank 1 | 84.16 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 42 | #05 | **CDF3** | `CDF3_8413b` | Rank 2 | 83.06 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 43 | #05 | **CDF3** | `CDF3_8413b` | Rank 3 | 81.68 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 44 | #05 | **CDF3** | `CDF3_8413b` | Rank 4 | 79.94 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 45 | #05 | **CDF3** | `CDF3_8413b` | Rank 5 | 78.53 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 51 | #07 | **MdDOF54** | `MdDOF54_cff3d` | Rank 1 | 50.59 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 52 | #07 | **MdDOF54** | `MdDOF54_cff3d` | Rank 2 | 49.81 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 53 | #07 | **MdDOF54** | `MdDOF54_cff3d` | Rank 3 | 48.51 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 54 | #07 | **MdDOF54** | `MdDOF54_cff3d` | Rank 4 | 47.80 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 55 | #07 | **MdDOF54** | `MdDOF54_cff3d` | Rank 5 | 47.45 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 36 | #09 | **BnCDF1** | `BnCDF1` | Rank 1 | 56.15 | `AlphaFold -20261008T053401Z-1-001/A...` | `AtDOF5.8` | `Computed` |
| 37 | #09 | **BnCDF1** | `BnCDF1` | Rank 2 | 54.70 | `AlphaFold -20261008T053401Z-1-001/A...` | `AtDOF5.8` | `Computed` |
| 38 | #09 | **BnCDF1** | `BnCDF1` | Rank 3 | 54.41 | `AlphaFold -20261008T053401Z-1-001/A...` | `AtDOF5.8` | `Computed` |
| 39 | #09 | **BnCDF1** | `BnCDF1` | Rank 4 | 54.18 | `AlphaFold -20261008T053401Z-1-001/A...` | `AtDOF5.8` | `Computed` |
| 40 | #09 | **BnCDF1** | `BnCDF1` | Rank 5 | 52.09 | `AlphaFold -20261008T053401Z-1-001/A...` | `AtDOF5.8` | `Computed` |
| 56 | #31 | **NLP1** | `MtNLP1_95155` | Rank 1 | 51.99 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 57 | #31 | **NLP1** | `MtNLP1_95155` | Rank 2 | 51.58 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 58 | #31 | **NLP1** | `MtNLP1_95155` | Rank 3 | 50.42 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 59 | #31 | **NLP1** | `MtNLP1_95155` | Rank 4 | 49.80 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 60 | #31 | **NLP1** | `MtNLP1_95155` | Rank 5 | 49.63 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 46 | #49 | **GhGT-3b_A04** | `GhGT3b_A04_be592` | Rank 1 | 74.59 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 47 | #49 | **GhGT-3b_A04** | `GhGT3b_A04_be592` | Rank 2 | 73.54 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 48 | #49 | **GhGT-3b_A04** | `GhGT3b_A04_be592` | Rank 3 | 73.51 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 49 | #49 | **GhGT-3b_A04** | `GhGT3b_A04_be592` | Rank 4 | 72.61 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 50 | #49 | **GhGT-3b_A04** | `GhGT3b_A04_be592` | Rank 5 | 70.67 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 31 | #53 | **BBX21** | `BBX21_15acd` | Rank 1 | 58.35 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 32 | #53 | **BBX21** | `BBX21_15acd` | Rank 2 | 56.96 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 33 | #53 | **BBX21** | `BBX21_15acd` | Rank 3 | 55.27 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 34 | #53 | **BBX21** | `BBX21_15acd` | Rank 4 | 54.85 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 35 | #53 | **BBX21** | `BBX21_15acd` | Rank 5 | 53.35 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 21 | #54 | **AtPLATZ2** | `AtPLATZ2_5dbaf` | Rank 1 | 72.57 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 22 | #54 | **AtPLATZ2** | `AtPLATZ2_5dbaf` | Rank 2 | 71.23 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 23 | #54 | **AtPLATZ2** | `AtPLATZ2_5dbaf` | Rank 3 | 70.89 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 24 | #54 | **AtPLATZ2** | `AtPLATZ2_5dbaf` | Rank 4 | 70.39 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 25 | #54 | **AtPLATZ2** | `AtPLATZ2_5dbaf` | Rank 5 | 69.83 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 26 | #55 | **AtPLATZ4** | `AtPLATZ4_e1c1e` | Rank 1 | 76.54 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 27 | #55 | **AtPLATZ4** | `AtPLATZ4_e1c1e` | Rank 2 | 75.43 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 28 | #55 | **AtPLATZ4** | `AtPLATZ4_e1c1e` | Rank 3 | 74.85 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 29 | #55 | **AtPLATZ4** | `AtPLATZ4_e1c1e` | Rank 4 | 74.73 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 30 | #55 | **AtPLATZ4** | `AtPLATZ4_e1c1e` | Rank 5 | 74.24 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 01 | #60 | **AHL10** | `AHL10_f311a` | Rank 1 | 59.77 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 02 | #60 | **AHL10** | `AHL10_f311a` | Rank 2 | 58.98 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 03 | #60 | **AHL10** | `AHL10_f311a` | Rank 3 | 58.53 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 04 | #60 | **AHL10** | `AHL10_f311a` | Rank 4 | 56.08 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 05 | #60 | **AHL10** | `AHL10_f311a` | Rank 5 | 54.74 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 11 | #62 | **AtC3H15** | `AtC3H15_262f9` | Rank 1 | 64.17 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 12 | #62 | **AtC3H15** | `AtC3H15_262f9` | Rank 2 | 63.30 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 13 | #62 | **AtC3H15** | `AtC3H15_262f9` | Rank 3 | 63.25 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 14 | #62 | **AtC3H15** | `AtC3H15_262f9` | Rank 4 | 63.10 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 15 | #62 | **AtC3H15** | `AtC3H15_262f9` | Rank 5 | 62.13 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 06 | #63 | **AtC3H14** | `AtC3H14_781a4` | Rank 1 | 64.69 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 07 | #63 | **AtC3H14** | `AtC3H14_781a4` | Rank 2 | 64.69 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 08 | #63 | **AtC3H14** | `AtC3H14_781a4` | Rank 3 | 64.51 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 09 | #63 | **AtC3H14** | `AtC3H14_781a4` | Rank 4 | 64.19 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |
| 10 | #63 | **AtC3H14** | `AtC3H14_781a4` | Rank 5 | 64.13 | `AlphaFold -20261008T053401Z-1-001/A...` | — | `Computed` |

---

## 5. Anomaly Audit & Biological Fidelity

### A. `BnCDF1` Template Homolog Handling
- **Condition:** PDB coordinate files in `AlphaFold/BnCDF1/` are named `AtDOF58_489cf_unrelaxed_rank_*.pdb`.
- **Verification:** Query sequence in `AtDOF58_489cf.csv` is 292 AA, matching Brassica napus `BnCDF1.txt` (TF #09) 100%. The ColabFold run used homologous Arabidopsis `AtDOF5.8` template coordinates.
- **Resolution:** Ingested and linked to Record #09 (`BnCDF1`), with `template_homolog = 'AtDOF5.8'` explicitly recorded.

### B. `MtNLP1` Disambiguation
- **Condition:** `data_mapping_report.md` Section 6 table listed `MtNLP1_95155` alongside both Record #31 (*M. truncatula*, Nature Plants 2018) and Record #32 (*M. truncatula*, Plant Comms 2021).
- **Verification:** Modeled sequence in `MtNLP1_95155.csv` and PDB files has **934 AA**, matching Record #31 (`A0A977NVL6`) 100% bit-for-bit. Record #32 has a distinct sequence of length **909 AA** (`A0A072V3U8`).
- **Resolution:** `MtNLP1_95155` was linked strictly to Record #31, preventing false sequence-structure concordance. Record #32 has 0 structures.

---

## 6. Database State Before and After Phase 5C

| Entity Table | Phase 5B Count | Phase 5C Count | Delta | Status |
| :--- | :---: | :---: | :---: | :--- |
| `transcription_factors` | 63 | **63** | 0 | Baseline Preserved |
| `plants` | 30 | **30** | 0 | Baseline Preserved |
| `tf_families` | 23 | **23** | 0 | Baseline Preserved |
| `stress_conditions` | 21 | **21** | 0 | Baseline Preserved |
| `research_papers` | 60 | **60** | 0 | Baseline Preserved |
| `tf_identifiers` | 92 | **92** | 0 | Baseline Preserved |
| `target_genes` | 75 | **75** | 0 | Baseline Preserved |
| `pathways` | 110 | **110** | 0 | Baseline Preserved |
| `protein_sequences` | 46 | **46** | 0 | Baseline Preserved |
| `protein_structures` | **0** | **60** | **+60** | **Ingested & Validated** |
| `protein_interactions` | 0 | **0** | 0 | Reserved for Phase 5D |

---

## 7. Pytest Test Results

```
backend/tests/test_alphafold_import.py ............                      [ 24%]
backend/tests/test_database_schema.py ......                             [ 36%]
backend/tests/test_fasta_import.py ..............                        [ 65%]
backend/tests/test_full_dataset_import.py ........                       [ 81%]
backend/tests/test_test_import.py .........                              [100%]
====================== 49 passed, 1236 warnings in 8.10s ======================
```

---

## 8. Source Immutability & Backup Verification

- Pre-ingestion backup: `phytostress_backup_pre_alphafold_import.db`  
  **SHA-256:** `874B4CB0FBBDF056279DEB45E78915868D51985EED32E96033242ED6620227CC`  
- Original source files unchanged:  
  - All 303 AlphaFold files on disk remain bit-for-bit identical to baseline.
  - All 41 FASTA files on disk remain bit-for-bit identical to baseline.
  - `PhytoStress_TF_Atlas.html` and Excel `.xlsm` remain bit-for-bit identical to baseline.

---

## 9. Recommendations for Phase 5D (STRING PPI Network Ingestion)

Phase 5C is complete and frozen. Upon approval, Phase 5D can proceed to:
1. Audit all 45 STRING directories (488 files) in `STRING database information-20261008T053421Z-1-001/`.
2. Ingest protein-protein interaction edges, confidence scores, and functional partner annotations into `protein_interactions`.
3. Validate interaction partner identifiers against database entities and UniProt cross-references.
