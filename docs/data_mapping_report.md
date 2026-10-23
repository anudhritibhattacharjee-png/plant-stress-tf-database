# PhytoStress TF Atlas — Data Mapping Report

**Version:** 1.0  
**Phase:** Phase 2 (Architecture & Data Strategy)  
**Status:** Validated  
**Primary Source References:**
* `Transcription factors regulating plant stress (1).xlsm` (Sheet1, 61 data rows)
* `PhytoStress_TF_Atlas.html` (`const DATA` array, 63 curated records)
* Supporting bioinformatics asset repositories (FASTA, AlphaFold, Cytoscape, STRING)

---

## 1. Executive Summary

This report establishes the authoritative data-mapping blueprint for migrating the **PhytoStress TF Atlas** from a static, hardcoded prototype into a robust, normalized relational database driven by **FastAPI** and **SQLAlchemy** (compatible with SQLite for development and PostgreSQL for production).

Scientific data integrity is paramount. No biological identifiers (UniProt, NCBI, Ensembl, DOI) are fabricated or silently modified. All original verbatim textual strings are preserved alongside clean, normalized relational tables.

---

## 2. Column-by-Column Data Mapping Matrix

The core dataset contains 15 attributes per entry. The table below details how each spreadsheet column maps to the relational schema:

| Original Column Name | Proposed Table | Normalized Field | Data Type | Req / Opt | Transformed? | Transformation & Parsing Rule | Original Value Preserved? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`TF / TF family`** | `transcription_factors` | `tf_name` | VARCHAR(150) | Required | Yes | Strip leading/trailing whitespace. Retain verbatim composite names (e.g. `SlCDF1 / SlCDF3`). Constituents mapped in sub-aliases. | **Yes** (in `tf_name` & `raw_supplied_tf`) |
| **`Standardized TF Family`** | `tf_families` | `name` | VARCHAR(150) | Required | Yes | Strip whitespace. Deduplicate into `tf_families` lookup table. Linked via FK `family_id`. | **Yes** (in `tf_families.name`) |
| **`Plant`** | `plants` | `display_name`<br>`common_name`<br>`scientific_name` | VARCHAR(255)<br>VARCHAR(100)<br>VARCHAR(150) | Required | Yes | Preserves exact text in `display_name`. Parses common name (e.g. `Cotton`) and Latin binomial in parentheses (e.g. `Gossypium hirsutum`). | **Yes** (in `plants.display_name`) |
| **`Validation System`** | `transcription_factors` | `validation_system` | VARCHAR(255) | Optional | Yes | Strip whitespace. Null if blank. Captures native vs heterologous expression systems. | **Yes** |
| **`Stress condition`** | `stress_conditions`<br>`tf_stress_associations` | `stress_name`<br>`tf_id`, `stress_id` | VARCHAR(100)<br>INTEGER FKs | Required | Yes | Retains combined string in `raw_supplied_stress`. Splits on `,\s*` and ` and ` to populate normalized M2M associations. | **Yes** (in `transcription_factors.raw_stress`) |
| **`Regulatory Effect`** | `transcription_factors` | `regulatory_effect` | VARCHAR(100) | Optional | Yes | Strip whitespace. Preserves classification: `Positive`, `Negative`, `Mixed / context-dependent`, `Candidate`. | **Yes** |
| **`How it regulates stress`** | `transcription_factors` | `mechanism_description` | TEXT | Optional | Yes | Strip whitespace. Full biological explanation of physiological/molecular regulatory mechanism. | **Yes** |
| **`Key Target(s) / Pathway`** | `target_genes`<br>`pathways`<br>`tf_target_associations` | `gene_symbol`<br>`pathway_name`<br>`tf_id`, `target_id` | VARCHAR(100)<br>VARCHAR(255)<br>INTEGER FKs | Optional | Yes | Retains raw string in `raw_target_pathway`. Parses target gene symbols (e.g. `SlSOS1`) and pathway terms into relational tables. | **Yes** (in `transcription_factors.raw_targets`) |
| **`Evidence Type`** | `transcription_factors` | `evidence_summary` | TEXT | Optional | Yes | Strip whitespace. Summarizes experimental techniques (e.g. `RNAi`, `ChIP-seq`, `EMSA`, `CRISPR/Cas9`). | **Yes** |
| **`DOI Number`** | `research_papers` | `doi`<br>`doi_url` | VARCHAR(255)<br>VARCHAR(500) | Optional | Yes | Strips `https://doi.org/` prefix for normalized `doi`. Stores full canonical link in `doi_url`. | **Yes** (in `doi_url` & raw records) |
| **`Uniprot Accession ID/Valid Gene ID`** | `tf_identifiers` | `identifier_value`<br>`verification_status` | VARCHAR(100)<br>VARCHAR(50) | Optional | Yes | Verbatim cell retained in `raw_supplied_text`. Valid IDs parsed into individual rows. Flags `"Not verified"`. | **Yes** (in `tf_identifiers.raw_supplied_text`) |
| **`Identifier Type`** | `tf_identifiers` | `identifier_type` | VARCHAR(150) | Optional | Yes | Stores identifier database context (e.g. `UniProtKB`, `TAIR`, `NCBI Gene`, `Gene symbol`). | **Yes** |
| **`Research paper `** *(trailing space)* | `research_papers` | `title` | TEXT | Required | Yes | Strips enclosing decorative quotes (e.g. `“...”`) and whitespace. Deduplicated on canonical title and DOI. | **Yes** |
| **`Journal`** | `research_papers` | `journal` | VARCHAR(255) | Optional | Yes | Strip whitespace. Handles placeholders like `___` and `—` as NULL while retaining citation notes. | **Yes** |
| **`Year`** | `research_papers` | `year` | INTEGER | Optional | Yes | Casts float/string year to INTEGER (e.g. `2016.0` -> `2016`). | **Yes** |

---

## 3. Critical Data Preservation Rules

1. **Zero Identifier Fabrication:**  
   Under no circumstances will a missing accession number, NCBI Gene ID, or UniProt entry be guessed or fabricated. If an identifier was not supplied, the field remains `NULL`.
2. **Explicit Verification Status:**  
   Records explicitly labelled `"Not verified"` (e.g. `SlDOF22`, `GhDOF1`, `VaDOF17d`, `JrDOF3`, `CaMADS`, `OtTCP4`, `OtTCP9`, `OtTCP11`) will be assigned an explicit status of `verification_status = 'Not verified'`.
3. **Preservation of Author Doubts & Comments:**  
   Record #36 contains the annotation:  
   `"Q5N7N1/Q8LNH0\n(not sure whether the proteins are transcription factors or not)"`  
   *Storage Rule:* The verbatim text is stored in `tf_identifiers.raw_supplied_text` and `transcription_factors.notes`. The two candidate accessions (`Q5N7N1`, `Q8LNH0`) are flagged with `verification_status = 'Candidate / Uncertain'`.
4. **Preservation of Raw Text Provenance:**  
   Every transcription factor row retains the exact unparsed strings for:
   * `raw_supplied_tf`
   * `raw_supplied_stress`
   * `raw_supplied_targets`
   * `raw_supplied_identifiers`
   This guarantees that the API can deliver both normalized relational data and verbatim prototype output.

---

## 4. Handling Composite Biological Entities

### A. Composite TF Names
In several research papers, gene families, homoeologs, or paralogs were reported together as a single functional module:
* Record #06: `SlCDF1 / SlCDF3` (Tomato)
* Record #08: `BpDOF4 / BpDOF11 / BpDOF17` (Birch)
* Record #24: `MADS-box family` (Multiple plants)
* Record #33: `NLP1 / NLP5` (Tomato)
* Record #44: `VOZ1 / VOZ2` (Arabidopsis thaliana)
* Record #56: `TaSPL6-A/B/D` (Wheat — allohexaploid homoeologs on chromosomes 4A, 5B, 5D)
* Record #58: `ZmBES1/BZR1-1` (Maize)
* Record #59: `SlBZR1 / SlBZR1D` (Tomato)

**Representation Rule:**
1. The primary record in `transcription_factors` retains the exact composite label (`tf_name = 'SlCDF1 / SlCDF3'`).
2. An auxiliary table `tf_gene_members` links individual sub-units (`SlCDF1`, `SlCDF3`) to the parent record.
3. This ensures that searches for either `"SlCDF1"` or `"SlCDF3"` match the record immediately, while preserving the publication's composite biological unit.

### B. Composite Stress Conditions
Plant stress experiments frequently investigate cross-tolerance or multi-stress assays:
* e.g., `"Drought, cold, osmotic stress"`, `"Salt and drought"`, `"Nitrate / nodulation"`, `"Drought, osmotic and salt-associated stress"`.

**Representation Rule:**
1. The exact phrase is stored in `transcription_factors.raw_stress` to ensure 100% fidelity with the prototype UI chips.
2. The phrase is normalized and split on delimiters (`,\s*`, ` and `, ` / `).
3. Individual conditions are registered in `stress_conditions` (`Drought`, `Cold`, `Osmotic stress`, `Salt stress`, `Nitrate`, `Nodulation`).
4. Many-to-many junction entries are created in `tf_stress_associations`, enabling users to filter by single stress conditions.

### C. Plant Species and Experimental Systems
Spreadsheet plant names frequently encode both the donor organism and the heterologous test organism:
* `"Cotton (Gossypium hirsutum; functional test in Arabidopsis)"`
* `"Potato (Solanum tuberosum; AtBBX21 used for functional analysis)"`
* `"Maize (Zea mays; functional test in Arabidopsis)"`
* `"Triticum aestivum (wheat)"`

**Representation Rule:**
1. `plants.display_name` retains the complete unmodified string (e.g. `"Cotton (Gossypium hirsutum; functional test in Arabidopsis)"`).
2. `plants.common_name` is parsed to the primary crop (e.g. `"Cotton"`).
3. `plants.scientific_name` is parsed to the botanical binomial (e.g. `"Gossypium hirsutum"`).
4. Heterologous assay details (e.g. `"functional test in Arabidopsis"`) are linked into `transcription_factors.validation_system`.

---

## 5. HTML Prototype vs. Excel Workbook Discrepancy

### Discrepancy Analysis
* **Excel Workbook (`Transcription factors regulating plant stress (1).xlsm`):** Contains **61 non-empty data rows** (rows 2 through 62).
* **HTML Prototype (`PhytoStress_TF_Atlas.html`):** Contains **63 items** in its `DATA` array.

### Identified Extra Records
Both extra records represent valid literature entries on plant transcription factor stress regulation:

1. **Record #30 (Index 29):**
   * **TF:** `NLP7`
   * **Family:** `NIN-like protein (NLP / RWP-RK)`
   * **Plant:** `Arabidopsis`
   * **Stress:** `Nitrate response`
   * **Regulatory Effect:** `Positive / regulatory`
   * **Mechanism:** `Nuclear retention of NLP7 coordinates the early transcriptional response to nitrate.`
   * **Evidence:** `T-DNA mutants; nuclear localization/retention assays; transcriptional profiling`
   * **Paper Title:** *"Nuclear retention of the transcription factor NLP7 orchestrates the early response to nitrate in plants."*
   * **Journal:** `Nature Communications` (Year: 2013)
   * **DOI:** `https://doi.org/10.1038/ncomms2650`
   * **UniProt:** `Q84TH9`

2. **Record #36 (Index 35):**
   * **TF:** `NLP family`
   * **Family:** `NIN-like protein (NLP / RWP-RK)`
   * **Plant:** `Rice`
   * **Stress:** `Chilling/cold stress`
   * **Regulatory Effect:** `Association / expression only`
   * **Mechanism:** `NLP genes are associated with early chilling responses and may participate in stress signalling, antioxidant defence and osmotic regulation.`
   * **Evidence:** `RNA-seq differential-expression analysis`
   * **Paper Title:** *"Genes, pathways and transcription factors involved in seedling stage chilling stress tolerance in Indica rice through RNA-Seq analysis."*
   * **Journal:** `BMC Plant Biology` (Year: 2019)
   * **DOI:** `https://doi.org/10.1186/s12870-019-1922-8`
   * **UniProt:** `Q5N7N1/Q8LNH0 (not sure whether the proteins are transcription factors or not)`

### Reconciliation Strategy
1. **Source of Truth:** Both sources represent curated biological data. The Excel workbook is the base curation table; the HTML prototype contains an updated 63-record curation snapshot.
2. **Authoritative Database Population:** The database will ingest **all 63 unique records**.
3. **Audit Trail:** An `import_source` attribute will denote whether a record originated from `EXCEL_BASE` or `HTML_SUPPLEMENT`.
4. **Resolution Priority:** If any cell value conflicts between Excel and HTML for identical DOIs, the Excel value takes precedence for biological fields, with the HTML value preserved in the audit log.

---

## 6. Supporting Bioinformatics Asset Mapping

The database links transcription factors to physical sequence, structure, and network files using **strict deterministic matching rules**. No fuzzy matching is permitted.

### Deterministic Matching Rules
1. **FASTA Sequences (`FASTA sequence of TFs-20261008T053415Z-1-001`):**
   * Rule A: Match exact filename stem against TF name or constituent gene symbol (e.g. `TaZNF.fasta.txt` -> `TaZNF`).
   * Rule B: For multi-protein papers, match UniProt accession inside FASTA header:
     * `MtNLP1.txt` (`>tr|A0A977NVL6...`) -> Record #31 (`A0A977NVL6`, Nature Plants 2018).
     * `MtNLP1 (2).txt` (`>tr|A0A072V3U8...`) -> Record #32 (`A0A072V3U8`, Plant Comms 2021).
2. **AlphaFold Structures (`AlphaFold -20261008T053401Z-1-001`):**
   * Rule: Match folder prefix before the hash delimiter (e.g. `AHL10_f311a` -> `AHL10`, `AtC3H14_781a4` -> `AtC3H14`, `BBX21_15acd` -> `BBX21`).
3. **STRING PPI Subnets (`STRING database information-20261008T053421Z-1-001`):**
   * Rule: Match directory name against TF name, gene symbol, or plant-prefixed locus (e.g. `SlDOF22` -> `SlDOF22`, `AtDOF5.8` -> `AtDOF5.8`, `OsGATA8` -> `OsGATA8`).
4. **Cytoscape Diagrams (`Cytoscape protein interactions-20261008T053406Z-1-001`):**
   * Rule: Match file basename stripped of `" similar protein.png"` against TF name (e.g. `BnCDF1 similar protein.png` -> `BnCDF1`, `TaMADS51 similar protein.png` -> `TaMADS51`).

### Complete Asset Mapping Table (All 63 Records)

| # | TF Record | Plant Species | Linked FASTA File | AlphaFold Model Folder | Cytoscape Image | STRING Interaction Directory |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| 01 | **SlDOF22** | Tomato | — | — | — | `SlDOF22` |
| 02 | **TaZNF** | Wheat | `TaZNF.fasta.txt` | — | `TaZNF.png` | `TaZNF` |
| 03 | **AtDOF5.8** | Arabidopsis | `AtDOF5.8.txt` | `AtDOF58_7e6b1` | `AtDOF5.8.png` | `AtDOF5.8` |
| 04 | **ClDOF29** | Watermelon | — | — | — | — |
| 05 | **CDF3** | Arabidopsis | `CDF3.txt` | `CDF3_8413b` | — | `CDF3` |
| 06 | **SlCDF1 / SlCDF3** | Tomato | `SlCDF1.txt`, `SlCDF3.txt` | — | — | `SlCDF1`, `SlCDF3` |
| 07 | **MdDOF54** | Apple | `MdDOF54.txt` | `MdDOF54_cff3d` | — | `MdDOF54` |
| 08 | **BpDOF4 / 11 / 17** | Birch | — | — | — | — |
| 09 | **BnCDF1** | Brassica | `BnCDF1.txt` | `BnCDF1` | `BnCDF1 similar protein.png` | `BnCDF1` |
| 10 | **GhDOF1** | Cotton | — | — | — | — |
| 11 | **VaDOF17d** | Grape | — | — | — | — |
| 12 | **OsDOF1** | Rice | `OsDOF1.txt` | — | `OsDOF1 similar protein.png` | `OsDOF1` |
| 13 | **JrDOF3** | Walnut | — | — | — | — |
| 14 | **OsDOF15** | Rice | `OsDOF15.txt` | — | — | — |
| 15 | **OsDOF18** | Rice | `OsDOF18.txt` | — | `OsDOF18.png` | `OsDOF18` |
| 16 | **SlMBP11** | Tomato | `SlMBP11.txt` | — | `SlMBP11.png` | `SlMBP11` |
| 17 | **SlMBP8** | Tomato | `SlMBP8.txt` | — | `SlMBP8.png` | `SlMBP8` |
| 18 | **CaMADS** | Pepper | — | — | — | — |
| 19 | **TaMADS51** | Wheat | `TaMADS51.txt` | — | `TaMADS51 similar protein.png` | `TaMADS51` |
| 20 | **OsMADS3** | Rice | `OsMADS3.txt` | — | `OsMADS3.png` | `OsMADS3` |
| 21 | **OsMADS25** | Rice | `OsMADS25.txt` | — | `OsMADS25.png` | `OsMADS25` |
| 22 | **OsMADS25** | Rice | `OsMADS25.txt` | — | `OsMADS25.png` | `OsMADS25` |
| 23 | **TDR6** | Tomato | `TDR6.txt` | — | `TDR6.png` | `TDR6` |
| 24 | **MADS-box family** | Multiple plants | — | — | — | — |
| 25 | **OtTCP4** | O. taihangensis | — | — | — | — |
| 26 | **OtTCP9** | O. taihangensis | — | — | — | — |
| 27 | **OtTCP11** | O. taihangensis | — | — | — | — |
| 28 | **NLP family** | Rice | — | — | — | — |
| 29 | **NLP7** | Arabidopsis | `NLP7.txt` | — | `NLP7.png` | `NLP7` |
| 30 | **NLP7** | Arabidopsis | `NLP7.txt` | — | `NLP7.png` | `NLP7` |
| 31 | **NLP1** | Medicago truncatula | `MtNLP1.txt` (A0A977NVL6) | `MtNLP1_95155` | `MtNLP1.png`, `NLP1.png` | `MtNLP1` |
| 32 | **NLP1** | Medicago truncatula | `MtNLP1 (2).txt` (A0A072V3U8)| `MtNLP1_95155` | `MtNLP1.png`, `NLP1.png` | `MtNLP1` |
| 33 | **NLP1 / NLP5** | Tomato | `SlNLP1.txt`, `SlNLP5.txt` | — | `SlNLP1.png`, `SlNLP5.png` | `SLNLP1`, `SlNLP5` |
| 34 | **NLP7** | Arabidopsis | `NLP7.txt` | — | `NLP7.png` | `NLP7` |
| 35 | **NLP family** | Arabidopsis | — | — | — | — |
| 36 | **NLP family** | Rice | — | — | — | — |
| 37 | **NLP2** | Rice | `NLP2.txt` | — | `NLP2.png` | `OsNLP2` |
| 38 | **NLP4** | Rice | `NLP4.txt` | — | `OsNLP4.png` | `OsNLP4` |
| 39 | **NLP8** | Arabidopsis | `NLP8.txt` | — | `AtNLP8.png` | `NLP8` |
| 40 | **GmNLP7a** | Soybean | `GmNLP7a.txt` | — | — | `GmNLP7a` |
| 41 | **GmNFYA13** | Soybean | — | — | — | — |
| 42 | **OsGATA8** | Rice | — | — | — | `OsGATA8` |
| 43 | **CAMTA3** | Arabidopsis | — | — | `CAMTA3.png` | `CAMTA3` |
| 44 | **VOZ1 / VOZ2** | Arabidopsis | `VOZ1.txt`, `VOZ2.txt` | — | `VOZ1.png`, `VOZ2.png` | `VOZ1`, `VOZ2` |
| 45 | **EIN3** | Arabidopsis | — | — | `EIN3.png` | `EIN3` |
| 46 | **PtrLBD41** | Black poplar | — | — | — | `PtrLBD41` |
| 47 | **ZmGRAS72** | Maize | — | — | — | — |
| 48 | **GT-2** | Cotton | `GT2.txt` | — | — | `GT2` |
| 49 | **GhGT-3b_A04** | Cotton | `GhGT-3b_A04.txt` | `GhGT3b_A04_be592` | — | `GhGT-3b_A04` |
| 50 | **OsZFP213** | Rice | `OsZFP213.txt` | — | — | — |
| 51 | **OsADR3** | Rice | — | — | `OsADR3.png` | `OsADR3` |
| 52 | **SlGATA17** | Tomato | `SlGATA17.txt` | — | — | `SlGATA17` |
| 53 | **BBX21** | Potato | `BBX21.txt` | `BBX21_15acd` | — | `AtBBX21` |
| 54 | **AtPLATZ2** | Arabidopsis | `AtPLATZ2.txt` | `AtPLATZ2_5dbaf` | `AtPLATZ2.png` | `AtPLATZ2` |
| 55 | **AtPLATZ4** | Arabidopsis | `AtPLATZ4.txt` | `AtPLATZ4_e1c1e` | `AtPLATZ4.png` | `AtPLATZ4` |
| 56 | **TaSPL6-A/B/D** | Wheat | — | — | — | — |
| 57 | **AcYABBY4** | Pineapple | — | — | — | — |
| 58 | **ZmBES1/BZR1-1** | Maize | — | — | `BZR1.png` | `ZmBES1-BZR1` |
| 59 | **SlBZR1 / SlBZR1D**| Tomato | `SlBZR1.txt` | — | `BZR1.png` | `SlBZR1-SlBZR1D` |
| 60 | **AHL10** | Arabidopsis | `AHL10.txt` | `AHL10_f311a` | `AHL10.png` | `AHL10` |
| 61 | **OsC3H47** | Rice | `OsC3H47.txt` | — | `OsC3H47.png` | `C3H47` |
| 62 | **AtC3H15** | Arabidopsis | `AtC3H15.txt` | `AtC3H15_262f9` | `AtC3H15.png` | `AtC3H15` |
| 63 | **AtC3H14** | Arabidopsis | `AtC3H14.txt` | `AtC3H14_781a4` | `AtC3H14.png` | `AtC3H14` |

*Summary:* **45 out of 63 TF records** are matched to one or more high-value structural, sequence, or network files.
