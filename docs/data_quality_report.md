# PhytoStress TF Atlas — Data Quality Report

**Version:** 1.0  
**Phase:** Phase 2 (Data Quality & Integrity Assessment)  
**Status:** Completed  
**Generated:** 2026-10-08  

---

## 1. Inventory Summary

| Asset Category | Count | Status / Notes |
| :--- | :---: | :--- |
| **Excel Workbook Data Rows** | **61** | Rows 2 to 62 in Sheet1 of `Transcription factors regulating plant stress (1).xlsm`. |
| **HTML Prototype Records** | **63** | In `const DATA` array in `PhytoStress_TF_Atlas.html`. |
| **FASTA Sequence Files** | **41** | Located in `FASTA sequence of TFs-20261008T053415Z-1-001/`. |
| **AlphaFold Structure Suites** | **12** | Distinct TF directories containing 303 files in `AlphaFold -20261008T053401Z-1-001/`. |
| **Cytoscape Network Images** | **32** | High-resolution network figures in `Cytoscape protein interactions-20261008T053406Z-1-001/`. |
| **STRING Interaction Datasets** | **45** | Distinct TF network packages containing 488 files in `STRING database information-20261008T053421Z-1-001/`. |

---

## 2. Identified Data Anomalies and Quality Findings

### A. Missing Identifiers
Records where no accession or gene identifier is provided at all:

| Record # | TF Name | Plant | Status in Source | Warning Details |
| :---: | :--- | :--- | :--- | :--- |
| **24** | `MADS-box family` | Multiple plants | `""` (Empty string) | Review paper synthesizing family-level evidence (DOI: `10.3389/fpls.2019.00853`). No single gene accession is applicable. Stored as `NULL`. |

---

### B. Explicitly Unverified / Uncertain Identifiers
Records where the curator explicitly noted that an accession or TF classification was unverified:

| Record # | TF Name | Plant | Supplied Value | Identifier Type | Quality Warning & Action |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **01** | `SlDOF22` | Tomato | `"Not verified"` | `NCBI Gene 101255410 (SlDof22); paper gene symbol` | Verbatim text preserved. Verification status flagged as `'Not verified'`. Gene symbol retained. |
| **10** | `GhDOF1` | Cotton | `"Not verified"` | `Gene symbol GhDof1` | Preserved as unverified. No accession fabricated. |
| **11** | `VaDOF17d` | Grape | `"Not verified"` | `Gene symbol VaDof17d` | Preserved as unverified. No accession fabricated. |
| **13** | `JrDOF3` | Walnut | `"Not verified"` | `Gene symbol JrDOF3` | Preserved as unverified. No accession fabricated. |
| **18** | `CaMADS` | Pepper | `"Not verified"` | `Gene symbol CaMADS` | Preserved as unverified. No accession fabricated. |
| **25** | `OtTCP4` | O. taihangensis | `"Not verified"` | `Gene symbol OtTCP4` | Preserved as unverified. Candidate gene model from genome survey. |
| **26** | `OtTCP9` | O. taihangensis | `"Not verified"` | `Gene symbol OtTCP9` | Preserved as unverified. Candidate gene model from genome survey. |
| **27** | `OtTCP11` | O. taihangensis | `"Not verified"` | `Gene symbol OtTCP11` | Preserved as unverified. Candidate gene model from genome survey. |
| **36** | `NLP family` | Rice | `"Q5N7N1/Q8LNH0\n(not sure whether the proteins are transcription factors or not)"` | `""` (Empty) | **Critical scientific doubt.** Preserved verbatim in `raw_supplied_text` and `notes`. Accessions flagged `'Candidate / Uncertain'`. |
| **37** | `NLP2` | Rice | `"Not verified"` | `Gene symbol OsNLP2` | Preserved as unverified. |
| **40** | `GmNLP7a` | Soybean | `"Not verified"` | `Gene symbol GmNLP7a` | Preserved as unverified. |

---

### C. Multi-Accession / Multi-Locus Identifier Cells
Several rows pack multiple gene accessions or loci into a single text cell:

| Record # | TF Name | Plant | Cell Value | Action Required |
| :---: | :--- | :--- | :--- | :--- |
| **08** | `BpDOF4 / BpDOF11 / BpDOF17` | Birch | `BPChr12G08354, BPChr10G04282 and BPChr01G16472 (gene ID as mentioned)` | Parse into 3 individual locus records in `tf_identifiers` while keeping full string in `raw_supplied_text`. |
| **21** | `OsMADS25` | Rice | `Q0JEA7, Q7XVR2, Q84NC5, Q01ME4` | Parse into 4 UniProt accessions in `tf_identifiers`; primary accession: `Q84NC5`. |
| **28** | `NLP family` | Rice | `Q10S83/Q0JC27/Q5NB82` | Parse into 3 distinct UniProt accessions in `tf_identifiers`. |
| **33** | `NLP1 / NLP5` | Tomato | `A0A3Q7HL32/A0A3Q7HUP0` | Parse into 2 UniProt accessions in `tf_identifiers`. |
| **42** | `OsGATA8` | Rice | `LOC_Os01g24070; NCBI accession KU377163 (OUP Academic)` | Parse locus `LOC_Os01g24070` and GenBank `KU377163`. |
| **44** | `VOZ1 / VOZ2` | Arabidopsis | `VOZ1: AT1G28520 / UniProt Q9SGQ0; VOZ2: AT2G42400 / NCBI Gene 818841 (UniProt)` | Parse TAIR and UniProt for each constituent gene. |
| **45** | `EIN3` | Arabidopsis | `AT3G20770; NCBI Gene 821625 (NCBI)` | Parse TAIR `AT3G20770` and NCBI `821625`. |
| **56** | `TaSPL6-A/B/D` | Wheat | `TaSPL6-A: TraesCS4A02G359500; TaSPL6-B: TraesCS5B02G512800; TaSPL6-D: TraesCS5D02G513300` | Parse 3 IWGSC wheat homoeologous gene models. |
| **58** | `ZmBES1/BZR1-1` | Maize | `ZmBES1/BZR1-1: legacy Gramene ID GRMZM5G812774; GenBank KX702328; maize B73 gene model reported as Zm00001d046305` | Parse Gramene, GenBank, and MaizeGDB models. |
| **60** | `AHL10` | Arabidopsis | `AT2G33620; NCBI Gene 817928; UniProt O22812` | Parse TAIR `AT2G33620`, NCBI `817928`, UniProt `O22812`. |
| **61** | `OsC3H47` | Rice | `LOC_Os07g04580 / Os07g0138400; NCBI Gene 9266125; UniProt Q8GW05` | Parse MSU/RAP loci, NCBI `9266125`, UniProt `Q8GW05`. |
| **62** | `AtC3H15` | Arabidopsis | `AT1G68200; NCBI Gene 843149; UniProt Q9C9F5` | Parse TAIR `AT1G68200`, NCBI `843149`, UniProt `Q9C9F5`. |
| **63** | `AtC3H14` | Arabidopsis | `AT1G66810; NCBI Gene 842999; UniProt Q9C9N3` | Parse TAIR `AT1G66810`, NCBI `842999`, UniProt `Q9C9N3`. |

---

### D. Duplicate TF Names Across Independent Studies
Multiple rows share the same TF name because they represent distinct research papers reporting different stresses, mechanisms, or evidence:

| TF Name | Occurrences | Records & Distinctions |
| :--- | :---: | :--- |
| **`NLP7`** | 3 | • **Record #29:** Arabidopsis, Nitrate stress, Science 2022 (DOI: `10.1126/science.add1104`)<br>• **Record #30:** Arabidopsis, Nitrate response, Nat Comms 2013 (DOI: `10.1038/ncomms2650`)<br>• **Record #34:** Arabidopsis, Cold stress, Overview 2022 (DOI: `10.1007/s12298-024-01485-y`) |
| **`NLP1`** | 2 | • **Record #31:** *M. truncatula*, Nitrate/nodulation, Nature Plants 2018 (DOI: `10.1038/s41477-018-0261-3`)<br>• **Record #32:** *M. truncatula*, Nitrate/nodulation, Plant Comms 2021 (DOI: `10.1016/j.xplc.2021.100183`) |
| **`OsMADS25`** | 2 | • **Record #21:** Rice, Nitrate accumulation, PLoS ONE 2015 (DOI: `10.1371/journal.pone.0135196`)<br>• **Record #22:** Rice, Root auxin signalling, Plant J 2018 (DOI: `10.1111/tpj.14007`) |
| **`NLP family`** | 3 | • **Record #28:** Rice, Nitrogen stress, Sci Rep 2020 (DOI: `10.1038/s41598-020-66338-6`)<br>• **Record #35:** Arabidopsis, Drought, Castaings 2009 (DOI: `10.1007/s12298-024-01485-y`)<br>• **Record #36:** Rice, Chilling/cold stress, BMC Plant Bio 2019 (DOI: `10.1186/s12870-019-1922-8`) |

*Quality Decision:* These rows must NOT be merged or collapsed into a single row. Each represents a distinct published experimental study with unique evidence, mechanisms, and literature citations. In the database, they will be represented as separate study records linked to the shared gene entity.

---

### E. Composite TF Names
The following 10 records represent multi-gene or family-level reports:
* Record #06: `SlCDF1 / SlCDF3`
* Record #08: `BpDOF4 / BpDOF11 / BpDOF17`
* Record #24: `MADS-box family`
* Record #33: `NLP1 / NLP5`
* Record #44: `VOZ1 / VOZ2`
* Record #48: `GT-2`
* Record #49: `GhGT-3b_A04`
* Record #56: `TaSPL6-A/B/D`
* Record #58: `ZmBES1/BZR1-1`
* Record #59: `SlBZR1 / SlBZR1D`

---

### F. Composite Stress Conditions
20 records contain multi-stress descriptions that require both raw display retention and parsed multi-association links:
* Record #05: `Drought, cold, osmotic stress`
* Record #06: `Salt, drought`
* Record #15: `Nitrogen limitation / N metabolism`
* Record #17: `Drought, salt`
* Record #18: `Cold, salt, osmotic stress`
* Record #21: `Nitrogen/nitrate availability`
* Record #22: `Nitrate / root response`
* Record #24: `Drought, salt, cold, heat, oxidative stress`
* Record #31: `Nitrate / nodulation`
* Record #32: `Nitrate / nodulation`
* Record #36: `Chilling/cold stress`
* Record #39: `Nitrate / seed germination`
* Record #40: `Nitrate / nodulation`
* Record #41: `Salt and drought`
* Record #42: `Salinity and drought`
* Record #43: `Salt / abiotic stress; broader biotic-stress regulation`
* Record #47: `Drought and salt`
* Record #48: `Drought and salt`
* Record #51: `Drought and oxidative stress`
* Record #61: `Drought, osmotic and salt-associated stress`

---

### G. Missing or Non-Canonical DOIs
* All 63 records have valid HTTP DOI links starting with `https://doi.org/` or `https://link.springer.com/`.
* Missing DOI count: **0**.

---

### H. Journal Formatting Anomalies
* Record #34: Journal is recorded as `"___"`. (Study cited inside review: Ding et al., 2022).
* Record #35: Journal is recorded as `"—"`. (Study cited inside review: Castaings et al., 2009).
* *Action:* Store `journal = NULL` and preserve citation context in `paper_notes`.

---

### I. FASTA Sequence Formatting Anomalies

| File Name | Anomaly Description | Biological Verification & Fix |
| :--- | :--- | :--- |
| `AtPLATZ2.txt` | **Missing `>` FASTA header line.** Starts directly with amino acid sequence. Contains an embedded space: `...PRIGK GVTNT...`. | Strip internal whitespace during ingestion. Auto-construct standard FASTA header `>AtPLATZ2_AT1G76590`. |
| `AtPLATZ4.txt` | **Missing `>` FASTA header line.** Raw sequence text spanning multiple lines without header. | Auto-construct standard FASTA header `>AtPLATZ4_AT1G32700`. |
| `OsDOF1.txt` | **Missing `>` FASTA header line.** Raw sequence starting with `MEVAEGRTV...`. | Auto-construct standard FASTA header `>OsDOF1_Q9FE00`. |
| `TaZNF.fasta.txt` | **Double file extension:** `.fasta.txt`. | Normalizer will accept both `.fasta` and `.fasta.txt`. |
| `MtNLP1.txt`<br>`MtNLP1 (2).txt` | Two sequence files with identical base name. | • `MtNLP1.txt` is accession `A0A977NVL6` (Record #31).<br>• `MtNLP1 (2).txt` is accession `A0A072V3U8` (Record #32). Match via UniProt header. |

---

### J. Asset-to-TF Mismatch and Disambiguation Warnings

1. **`BnCDF1` AlphaFold Model Prefix:**  
   Inside `AlphaFold -20261008T053401Z-1-001/AlphaFold/BnCDF1/`, the PDB files are named `AtDOF58_489cf_unrelaxed_rank_...pdb`.  
   *Reason:* AlphaFold prediction was generated using the homologous Arabidopsis template.  
   *Action:* Retain file as structural model for BnCDF1, but explicitly flag `template_homolog = 'AtDOF5.8'` in structure notes.
2. **`BZR1.png` in Cytoscape Interactions:**  
   `Cytoscape protein interactions` contains a single file `BZR1.png` which relates to both `ZmBES1/BZR1-1` (Record #58) and `SlBZR1 / SlBZR1D` (Record #59).  
   *Action:* Associate `BZR1.png` to both records as a shared family-level interaction graphic.
3. **STRING Folder Casing:**  
   STRING contains folder `SLNLP1` (all uppercase SL) while corresponding tomato entries use `SlNLP1`. Matcher will apply case-insensitive directory resolution.
