# PhytoStress TF Atlas — Controlled Test Import Report

**Phase:** Phase 4 (Controlled 5-Record Test Import)  
**Status:** Successfully Executed & Validated  
**Date:** 2026-10-14  
**Target Database:** `phytostress.db` (SQLite)  
**Database Backup:** `phytostress_backup_pre_test_import.db` (SHA-256: `95210D7FCD4EA7ECAB2CFC202A351A9ACB56F214B869E3AA0F9FFE188B54E68E`)  
**Test Data Source:** `data/test/test_records.json` (SHA-256: `7a9be95e2950f821f0d9437ebf58a9d5edb4ea282335f81a2bd33b15667528a6`)  

---

## 1. Executive Summary

A controlled test import was executed using exactly 5 curated representative records from `data/test/test_records.json`. The import was executed using SQLAlchemy ORM through [`scripts/import_test_data.py`](file:///f:/OMICSNOVA%20BIOLOGICAL%20INTELLIGENCE/scripts/import_test_data.py). 

All 5 core biological scenarios (simple TF, multiple stresses, multiple identifiers, composite TF name, and unverified identifier) were successfully normalized into the relational database. Zero biological data fabrication occurred. Idempotent duplicate-safety was verified, and 15 out of 15 automated test cases in `backend/tests` passed.

---

## 2. Exact Five Records Imported

| # | TF Name | Plant Species | TF Family | Stress Condition | Supplied Identifier(s) | Original Source | Biological Scenario |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `MdDOF54` | Apple | `DOF` | `Drought` | `A0A498K1B1` | Excel Row 8 / Prototype #7 | **Case A**: Simple TF with single UniProt ID |
| **2** | `CDF3` | Arabidopsis | `DOF / Cycling DOF Factor (CDF)` | `Drought, cold, osmotic stress` | `Q9LZP7` | Excel Row 6 / Prototype #5 | **Case B**: TF with multiple stress conditions |
| **3** | `OsMADS25` | Rice | `MADS-box` | `Nitrogen/nitrate availability` | `Q0JEA7, Q7XVR2, Q84NC5, Q01ME4` | Excel Row 22 / Prototype #21 | **Case C**: TF with multiple UniProt accessions |
| **4** | `SlCDF1 / SlCDF3` | Tomato | `DOF / Cycling DOF Factor (CDF)` | `Salt, drought` | `Solyc02g087980 and Solyc06g074350` | Excel Row 7 / Prototype #6 | **Case D**: Composite TF name & paralogs |
| **5** | `SlDOF22` | Tomato | `DOF` | `Salt stress` | `Not verified` | Excel Row 2 / Prototype #1 | **Case E**: Unverified accession / zero fabrication |

---

## 3. Database Tables Affected and Rows Inserted

Before import, `phytostress.db` was verified to be completely empty (0 biological rows across all tables). After executing `scripts/import_test_data.py`, the database was queried to verify rows inserted into each table:

| Database Table | Rows Before | Rows Inserted | Current Total Rows | Deduplication / Normalization Rationale |
| :--- | :---: | :---: | :---: | :--- |
| `transcription_factors` | 0 | **5** | **5** | 1 record per curated test entry |
| `plants` | 0 | **4** | **4** | Deduplicated: Apple, Arabidopsis, Rice, Tomato (Tomato reused by SlCDF1/SlCDF3 and SlDOF22) |
| `tf_families` | 0 | **3** | **3** | Deduplicated: DOF, DOF / Cycling DOF Factor (CDF), MADS-box |
| `stress_conditions` | 0 | **6** | **6** | Normalized: Drought, Cold, Osmotic stress, Nitrate availability, Nitrogen limitation, Salt stress |
| `tf_stress_associations` | 0 | **9** | **9** | Many-to-many associations linking TFs to all applicable stress conditions |
| `tf_identifiers` | 0 | **10** | **10** | 1 for MdDOF54, 1 for CDF3, 4 for OsMADS25, 2 for SlCDF1/SlCDF3, 2 for SlDOF22 |
| `research_papers` | 0 | **5** | **5** | 1 per unique publication (deduplicated by clean DOI and canonical title) |
| `tf_paper_associations` | 0 | **5** | **5** | Many-to-many associations linking each TF to its citing publication |
| `target_genes` | 0 | **9** | **9** | Downstream targets (MdAPX3, MdACO1, MdTGD2, MdAPL3, CBF, DREB2A, ZAT10, ZAT12, SlSOS1) |
| `tf_target_associations` | 0 | **9** | **9** | Many-to-many associations linking TFs to regulated target genes |
| `pathways` | 0 | **10** | **10** | Normalized physiological/signalling pathways |
| `tf_pathway_associations` | 0 | **10** | **10** | Many-to-many associations linking TFs to pathways |
| `import_audits` | 0 | **1** | **1** | Audit log capturing provenance, source SHA-256, record count, and table metrics |
| `protein_sequences` | 0 | 0 | 0 | Reserved for FASTA import phase |
| `protein_structures` | 0 | 0 | 0 | Reserved for AlphaFold import phase |
| `protein_interactions` | 0 | 0 | 0 | Reserved for STRING/Cytoscape import phase |

---

## 4. Normalized Relationships Created

### Profile 1: `MdDOF54` (ID #1)
* **Plant:** `Apple` (`Plant` ID #1)
* **Family:** `DOF` (`TFFamily` ID #1)
* **Stresses (1):** `Drought`
* **Identifiers (1):** `UniProtKB` = `A0A498K1B1` (`Verified`, `is_primary = True`)
* **Publication:** *"The apple DNA-binding one zinc-finger protein MdDof54 promotes drought resistance."* (*Horticulture Research*, 2020; DOI: `10.1038/s41438-020-00419-5`)
* **Target Genes (4):** `MdAPX3`, `MdACO1`, `MdTGD2`, `MdAPL3`
* **Pathways (2):** `Hydraulic water transport`, `Photosynthetic drought response`

### Profile 2: `CDF3` (ID #2)
* **Plant:** `Arabidopsis` (`Plant` ID #2)
* **Family:** `DOF / Cycling DOF Factor (CDF)` (`TFFamily` ID #2)
* **Raw Stress Preserved:** `"Drought, cold, osmotic stress"`
* **Stresses (3):** `Drought`, `Cold`, `Osmotic stress`
* **Identifiers (1):** `UniProtKB` = `Q9LZP7` (`Verified`, `is_primary = True`)
* **Publication:** *"Multifaceted role of cycling DOF factor 3 (CDF3) in the regulation of flowering time and abiotic stress responses in Arabidopsis."* (*Plant Cell Environ.*, 2017; DOI: `10.1111/pce.12894`)
* **Target Genes (4):** `CBF`, `DREB2A`, `ZAT10`, `ZAT12`
* **Pathways (2):** `Osmoprotection`, `Oxidative-stress metabolism`

### Profile 3: `OsMADS25` (ID #3)
* **Plant:** `Rice` (`Plant` ID #3)
* **Family:** `MADS-box` (`TFFamily` ID #3)
* **Raw Stress Preserved:** `"Nitrogen/nitrate availability"`
* **Stresses (2):** `Nitrate availability`, `Nitrogen limitation`
* **Identifiers (4):**
  1. `UniProtKB` = `Q0JEA7` (`Verified`, `is_primary = False`)
  2. `UniProtKB` = `Q7XVR2` (`Verified`, `is_primary = False`)
  3. `UniProtKB` = `Q84NC5` (`Verified`, `is_primary = True`, designated primary)
  4. `UniProtKB` = `Q01ME4` (`Verified`, `is_primary = False`)
* **Publication:** *"MADS-box transcription factor OsMADS25 regulates root development through affection of nitrate accumulation in rice."* (*PLoS ONE*, 2015; DOI: `10.1371/journal.pone.0135196`)
* **Pathways (2):** `Nitrate accumulation`, `Nitrate-dependent root development`

### Profile 4: `SlCDF1 / SlCDF3` (ID #4)
* **Plant:** `Tomato` (`Plant` ID #4, shared)
* **Family:** `DOF / Cycling DOF Factor (CDF)` (`TFFamily` ID #2, shared)
* **Raw TF Name Preserved:** `"SlCDF1 / SlCDF3"`
* **Raw Stress Preserved:** `"Salt, drought"`
* **Stresses (2):** `Salt stress`, `Drought`
* **Identifiers (2):**
  1. `Sol Genomics Network` = `Solyc02g087980` (`Verified`, `is_primary = True`)
  2. `Sol Genomics Network` = `Solyc06g074350` (`Verified`, `is_primary = False`)
* **Publication:** *"Characterization of tomato cycling dof factors reveals conserved and new functions in the control offlowering time and abiotic stress responses."* (*J. Exp. Bot.*, 2014; DOI: `10.1093/jxb/ert451`)
* **Pathways (2):** `Flowering-time network`, `Abiotic-stress response`

### Profile 5: `SlDOF22` (ID #5)
* **Plant:** `Tomato` (`Plant` ID #4, shared)
* **Family:** `DOF` (`TFFamily` ID #1, shared)
* **Verification Status:** `is_verified = False` (explicitly unverified)
* **Notes:** `"Accession explicitly flagged as 'Not verified' in literature source."`
* **Stresses (1):** `Salt stress`
* **Identifiers (2):**
  1. `NCBI Gene` = `101255410` (`Not verified`, `is_primary = False`, raw text = `"Not verified"`)
  2. `Gene symbol` = `SlDof22` (`Not verified`, `is_primary = False`, raw text = `"Not verified"`)
* **Fabricated Identifiers:** **0** (no UniProt ID fabricated)
* **Publication:** *"The transcription factor SlDof22 involved in ascorbate accumulation and salinity stress in tomato."* (*Biochem. Biophys. Res. Commun.*, 2016; DOI: `10.1016/j.bbrc.2016.04.148`)
* **Target Genes (1):** `SlSOS1`
* **Pathways (2):** `Ascorbate recycling`, `SOS-mediated Na+ homeostasis`

---

## 5. Duplicate-Import Behavior & Idempotency

* The importer implements deterministic duplicate detection by matching `(tf_name, paper.doi)`.
* When executed a second time against `phytostress.db` without `--force`, the importer recognized all 5 records already exist and exited safely:
  ```
  [DUPLICATE-SAFETY] All 5 test records are already present in the database.
  [DUPLICATE-SAFETY] Skipping re-import to guarantee idempotent duplicate-safety.
  Status: SKIPPED_EXISTING, records_inserted: 0
  ```
* Database integrity is maintained; no duplicate rows were created.

---

## 6. Pytest Validation Results

Automated tests in `backend/tests` were executed with `pytest`:

```
backend/tests/test_database_schema.py ......                             [ 40%]
backend/tests/test_test_import.py .........                              [100%]
====================== 15 passed, 124 warnings in 1.74s =======================
```

All 9 test-import-specific unit tests passed:
1. `test_import_completes_successfully` — PASSED
2. `test_expected_entity_counts` — PASSED
3. `test_case_a_simple_tf` — PASSED
4. `test_case_b_multiple_stresses` — PASSED
5. `test_case_c_multiple_identifiers` — PASSED
6. `test_case_d_composite_tf_name` — PASSED
7. `test_case_e_unverified_identifier` — PASSED
8. `test_provenance_and_audit` — PASSED
9. `test_duplicate_safety_idempotency` — PASSED

---

## 7. Mapping Findings and Observations

1. **UniProt Accession Regular Expression:**
   UniProtKB accessions comprise two valid patterns: standard 6-character accessions (`[OPQ][0-9][A-Z0-9]{3}[0-9]`) and 6- or 10-character accessions (`[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2}`). Using this official pattern successfully matches both single-entry accessions (e.g. `A0A498K1B1`, `Q9LZP7`) and multi-entry accessions (e.g. `Q0JEA7, Q7XVR2, Q84NC5, Q01ME4`).
2. **Plant and Family Normalization:**
   Entity deduplication performed properly: 5 distinct records collapsed into 4 plants and 3 families without collision.
3. **Zero Fabrication:**
   Unverified records (`SlDOF22`) preserve the literal `"Not verified"` text and set `is_verified = False`, while extracting genuine auxiliary identifiers (NCBI Gene `101255410`).

---

## 8. Readiness Assessment for Full Data Import

The database schema, SQLAlchemy models, migration scripts, and data parsing architecture have successfully passed all controlled validation benchmarks. 

The system is fully prepared to execute Phase 5 (Full Dataset Ingestion: 63 curated records + FASTA + AlphaFold + STRING + Cytoscape assets) upon user authorization.
