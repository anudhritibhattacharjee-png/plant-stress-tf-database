# PhytoStress TF Atlas — 5-Record Test Import Selection

**Version:** 1.0  
**Phase:** Phase 4 (Controlled Test Import)  
**Status:** Approved Specification  
**Dataset File:** `data/test/test_records.json`

This document details the selection criteria, biological rationale, source provenance, and expected database behavior for the 5-record representative test import of the PhytoStress TF Atlas.

---

## Selection Matrix Overview

| Test Record # | Biological Case | TF Name | Plant Species | Stress Condition | Supplied Identifier(s) | Original Source |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Case A**: Simple TF | `MdDOF54` | Apple | `Drought` | `A0A498K1B1` | Excel Row 8 / Prototype Record #7 |
| **2** | **Case B**: Multiple Stresses | `CDF3` | Arabidopsis | `Drought, cold, osmotic stress` | `Q9LZP7` | Excel Row 6 / Prototype Record #5 |
| **3** | **Case C**: Multiple Identifiers | `OsMADS25` | Rice | `Nitrogen/nitrate availability` | `Q0JEA7, Q7XVR2, Q84NC5, Q01ME4` | Excel Row 22 / Prototype Record #21 |
| **4** | **Case D**: Composite TF Name | `SlCDF1 / SlCDF3` | Tomato | `Salt, drought` | `Solyc02g087980 and Solyc06g074350` | Excel Row 7 / Prototype Record #6 |
| **5** | **Case E**: Unverified Identifier | `SlDOF22` | Tomato | `Salt stress` | `Not verified` | Excel Row 2 / Prototype Record #1 |

---

## Detailed Record Profiles

### Record 1 — Case A: Simple Transcription Factor Record
* **Test Record Number:** 1
* **Transcription Factor:** `MdDOF54`
* **TF Family:** `DOF`
* **Plant:** `Apple`
* **Stress Condition:** `Drought`
* **Identifier:** `A0A498K1B1` (`UniProtKB A0A498K1B1`)
* **Regulatory Effect:** `Positive`
* **Literature:** *"The apple DNA-binding one zinc-finger protein MdDof54 promotes drought resistance."* (*Horticulture Research*, 2020; DOI: `10.1038/s41438-020-00419-5`)
* **Original Source:** Excel Workbook Row 8 (`data/raw/Transcription factors regulating plant stress (1).xlsm`) / Prototype JSON Record #7 (`data/raw/prototype_63_records.json`).
* **Reason for Selection:**
  Serves as the canonical baseline single-gene control. Represents a single plant species, single standardized TF family, single environmental stress condition, and a single verified UniProt accession.
* **Expected Database Behavior:**
  1. Inserts or links `plants` (`display_name = 'Apple'`, `common_name = 'Apple'`).
  2. Inserts or links `tf_families` (`name = 'DOF'`).
  3. Inserts `transcription_factors` (`tf_name = 'MdDOF54'`, `is_verified = True`).
  4. Inserts or links single `stress_conditions` (`stress_name = 'Drought'`) with 1 junction row in `tf_stress_associations`.
  5. Inserts 1 record in `tf_identifiers` (`identifier_type = 'UniProtKB'`, `identifier_value = 'A0A498K1B1'`, `verification_status = 'Verified'`, `is_primary = True`).
  6. Inserts or links 1 `research_papers` (`doi = '10.1038/s41438-020-00419-5'`, `year = 2020`) and 1 junction row in `tf_paper_associations`.
  7. Parses target genes (`MdAPX3`, `MdACO1`, `MdTGD2`, `MdAPL3`) into `target_genes` and associates them via `tf_target_associations`.

---

### Record 2 — Case B: TF Associated with Multiple Stress Conditions
* **Test Record Number:** 2
* **Transcription Factor:** `CDF3`
* **TF Family:** `DOF / Cycling DOF Factor (CDF)`
* **Plant:** `Arabidopsis`
* **Stress Condition:** `Drought, cold, osmotic stress`
* **Identifier:** `Q9LZP7` (`UniProtKB Q9LZP7`)
* **Regulatory Effect:** `Positive`
* **Literature:** *"Multifaceted role of cycling DOF factor 3 (CDF3) in the regulation of flowering time and abiotic stress responses in Arabidopsis."* (*Plant Cell Environ.*, 2017; DOI: `10.1111/pce.12894`)
* **Original Source:** Excel Workbook Row 6 (`data/raw/Transcription factors regulating plant stress (1).xlsm`) / Prototype JSON Record #5 (`data/raw/prototype_63_records.json`).
* **Reason for Selection:**
  Validates the normalization and multi-association mapping of composite stress strings without data loss. Highlights abiotic stress cross-tolerance.
* **Expected Database Behavior:**
  1. Preserves the exact unparsed string `"Drought, cold, osmotic stress"` in `transcription_factors.raw_stress`.
  2. Parses and creates/links 3 distinct normalized entities in `stress_conditions`:
     - `"Drought"`
     - `"Cold"`
     - `"Osmotic stress"`
  3. Creates 3 distinct junction entries in `tf_stress_associations` linking `CDF3` to all three stress conditions.
  4. Preserves single verified UniProt accession `Q9LZP7` in `tf_identifiers`.
  5. Links single research paper via `tf_paper_associations`.

---

### Record 3 — Case C: TF Containing Multiple Identifiers / Accessions
* **Test Record Number:** 3
* **Transcription Factor:** `OsMADS25`
* **TF Family:** `MADS-box`
* **Plant:** `Rice`
* **Stress Condition:** `Nitrogen/nitrate availability`
* **Identifier:** `Q0JEA7, Q7XVR2, Q84NC5, Q01ME4` (`UniProtKB accessions supplied: Q0JEA7, Q7XVR2, Q84NC5, Q01ME4`)
* **Regulatory Effect:** `Positive`
* **Literature:** *"MADS-box transcription factor OsMADS25 regulates root development through affection of nitrate accumulation in rice."* (*PLoS ONE*, 2015; DOI: `10.1371/journal.pone.0135196`)
* **Original Source:** Excel Workbook Row 22 (`data/raw/Transcription factors regulating plant stress (1).xlsm`) / Prototype JSON Record #21 (`data/raw/prototype_63_records.json`).
* **Reason for Selection:**
  Specifically validates the 1-to-many relationship of `tf_identifiers`. Verifies that multi-accession cells are parsed into discrete database rows without dropping accessions or fabricating identifiers.
* **Expected Database Behavior:**
  1. Preserves the full cell text in `tf_identifiers.raw_supplied_text`.
  2. Inserts 4 distinct records into `tf_identifiers`:
     - `identifier_value = 'Q0JEA7'` (`UniProtKB`, `Verified`)
     - `identifier_value = 'Q7XVR2'` (`UniProtKB`, `Verified`)
     - `identifier_value = 'Q84NC5'` (`UniProtKB`, `Verified`, `is_primary = True`)
     - `identifier_value = 'Q01ME4'` (`UniProtKB`, `Verified`)
  3. All 4 identifiers maintain foreign keys to the single `OsMADS25` transcription factor.
  4. Parses `"Nitrogen/nitrate availability"` into `stress_conditions` (`"Nitrate"`, `"Nitrogen limitation"`) and links them via `tf_stress_associations`.

---

### Record 4 — Case D: Composite Transcription Factor Name
* **Test Record Number:** 4
* **Transcription Factor:** `SlCDF1 / SlCDF3`
* **TF Family:** `DOF / Cycling DOF Factor (CDF)`
* **Plant:** `Tomato`
* **Stress Condition:** `Salt, drought`
* **Identifier:** `Solyc02g087980 and Solyc06g074350 (gene ID reported in the paper)`
* **Regulatory Effect:** `Positive / mixed`
* **Literature:** *"Characterization of tomato cycling dof factors reveals conserved and new functions in the control offlowering time and abiotic stress responses."* (*J. Exp. Bot.*, 2014; DOI: `10.1093/jxb/ert451`)
* **Original Source:** Excel Workbook Row 7 (`data/raw/Transcription factors regulating plant stress (1).xlsm`) / Prototype JSON Record #6 (`data/raw/prototype_63_records.json`).
* **Reason for Selection:**
  Tests preservation of composite TF designations where multiple paralogs/homoeologs are co-published. Verifies that composite names are NOT destructively split into unrelated records or silently mangled, complying strictly with `docs/data_mapping_report.md` Section 4.A.
* **Expected Database Behavior:**
  1. `transcription_factors.tf_name` retains the verbatim composite string `'SlCDF1 / SlCDF3'`.
  2. `transcription_factors.raw_supplied_tf` preserves `'SlCDF1 / SlCDF3'`.
  3. `transcription_factors.raw_stress` preserves `'Salt, drought'`.
  4. Parses the two constituent Sol Genomics Network gene models (`Solyc02g087980`, `Solyc06g074350`) into `tf_identifiers`.
  5. Links both `"Salt stress"` and `"Drought"` in `stress_conditions` via `tf_stress_associations`.
  6. Reuses existing `plants` (`"Tomato"`) and `tf_families` (`"DOF / Cycling DOF Factor (CDF)"`) entities deterministically.

---

### Record 5 — Case E: Unverified / Uncertain Identifier Record
* **Test Record Number:** 5
* **Transcription Factor:** `SlDOF22`
* **TF Family:** `DOF`
* **Plant:** `Tomato`
* **Stress Condition:** `Salt stress`
* **Identifier:** `Not verified` (`NCBI Gene 101255410 (SlDof22); paper gene symbol`)
* **Regulatory Effect:** `Mixed / context-dependent`
* **Literature:** *"The transcription factor SlDof22 involved in ascorbate accumulation and salinity stress in tomato."* (*Biochem. Biophys. Res. Commun.*, 2016; DOI: `10.1016/j.bbrc.2016.04.148`)
* **Original Source:** Excel Workbook Row 2 (`data/raw/Transcription factors regulating plant stress (1).xlsm`) / Prototype JSON Record #1 (`data/raw/prototype_63_records.json`).
* **Reason for Selection:**
  Validates strict zero-fabrication rules. The curator explicitly noted `"Not verified"`. Proves that the system stores the record, preserves explicit unverified status, sets `is_verified = False`, extracts legitimate auxiliary NCBI Gene identifiers, and never invents a UniProt accession.
* **Expected Database Behavior:**
  1. `transcription_factors.is_verified` is set to `False`.
  2. `transcription_factors.notes` records unverified UniProt status.
  3. An entry is created in `tf_identifiers` with `identifier_value = '101255410'`, `identifier_type = 'NCBI Gene'`, `verification_status = 'Not verified'`, and `raw_supplied_text = 'Not verified'`.
  4. Zero UniProt accessions are fabricated or guessed.
  5. Target pathways (`Ascorbate recycling`, `SOS-mediated Na+ homeostasis`) and target gene (`SlSOS1`) are properly associated.

---

## Shared Entity Deduplication Expectations

When these 5 records are imported:
* **Plants Deduplication:**
  - `Apple` (from Record 1)
  - `Arabidopsis` (from Record 2)
  - `Rice` (from Record 3)
  - `Tomato` (shared across Records 4 and 5)
  - *Expected total distinct plants:* **4**
* **TF Families Deduplication:**
  - `DOF` (shared across Records 1 and 5)
  - `DOF / Cycling DOF Factor (CDF)` (shared across Records 2 and 4)
  - `MADS-box` (from Record 3)
  - *Expected total distinct families:* **3**
* **Total Transcription Factors:** **5**
