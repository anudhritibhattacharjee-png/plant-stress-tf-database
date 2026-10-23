# PhytoStress TF Atlas — Data Dictionary

**Version:** 1.0  
**Phase:** Phase 2 (Data Dictionary)  
**Status:** Validated  
**Target Architecture:** SQLite (Development) / PostgreSQL (Production)  

This data dictionary defines every proposed database entity and field in simple, precise language. It outlines the biological meaning, data origin, formatting rules, requirements, and provenance expectations.

---

## Table of Contents
1. [`tf_families`](#1-tf_families)
2. [`plants`](#2-plants)
3. [`transcription_factors`](#3-transcription_factors)
4. [`stress_conditions`](#4-stress_conditions)
5. [`tf_stress_associations`](#5-tf_stress_associations)
6. [`tf_identifiers`](#6-tf_identifiers)
7. [`research_papers`](#7-research_papers)
8. [`tf_paper_associations`](#8-tf_paper_associations)
9. [`target_genes`](#9-target_genes)
10. [`tf_target_associations`](#10-tf_target_associations)
11. [`pathways`](#11-pathways)
12. [`tf_pathway_associations`](#12-tf_pathway_associations)
13. [`protein_sequences`](#13-protein_sequences)
14. [`protein_structures`](#14-protein_structures)
15. [`protein_interactions`](#15-protein_interactions)
16. [`import_audits`](#16-import_audits)

---

## 1. `tf_families`
Stores standardized transcription factor family classifications.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique numerical primary key for the family. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `name` | Standard biological TF family name. | Spreadsheet: *Standardized TF Family* | `"DOF"`, `"MADS-box"`, `"CCCH zinc finger"` | VARCHAR(150) | Required | Unique; Non-empty string | Standard plant TF family nomenclature (PlantTFDB/iTAK) |
| `description` | High-level summary of family characteristics and DNA-binding domain. | Curated literature | `"DNA-binding One Zinc Finger family containing single C2C2 zinc finger domain"` | TEXT | Optional | Free text | Plant transcription factor domain references |

---

## 2. `plants`
Stores plant species information.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique numerical primary key for the plant. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `display_name` | Full original textual plant description preserved verbatim from the spreadsheet. | Spreadsheet: *Plant* | `"Cotton (Gossypium hirsutum; functional test in Arabidopsis)"` | VARCHAR(255) | Required | Preserves exact original text | Never altered |
| `common_name` | Clean common agricultural or vernacular name of the host plant. | Parsed from *Plant* | `"Cotton"`, `"Tomato"`, `"Rice"` | VARCHAR(100) | Required | Standard plant common name | Validated against NCBI Taxonomy common names |
| `scientific_name` | Formal Latin botanical binomial name. | Parsed from *Plant* | `"Gossypium hirsutum"`, `"Solanum lycopersicum"` | VARCHAR(150) | Optional | Italicized Latin binomial | Validated against NCBI Taxonomy |
| `ncbi_taxonomy_id`| NCBI Taxonomy identifier for the species. | NCBI Taxonomy | `3635` (Cotton), `4081` (Tomato) | INTEGER | Optional | Valid NCBI TaxID | Checked against NCBI Entrez |

---

## 3. `transcription_factors`
The core record representing a transcription factor study entry.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique numerical identifier for the TF record. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_name` | Name or symbol of the transcription factor. | Spreadsheet: *TF / TF family* | `"SlDOF22"`, `"AtDOF5.8"`, `"SlCDF1 / SlCDF3"` | VARCHAR(150) | Required | Non-empty string | Preserves original capitalization and composite slashes |
| `family_id` | Foreign key referencing the parent TF family. | Lookup in `tf_families` | `1` | INTEGER (FK) | Required | Must exist in `tf_families.id` | Referential integrity enforced |
| `plant_id` | Foreign key referencing the associated plant. | Lookup in `plants` | `1` | INTEGER (FK) | Required | Must exist in `plants.id` | Referential integrity enforced |
| `regulatory_effect`| Direction of transcriptional or physiological regulation under stress. | Spreadsheet: *Regulatory Effect* | `"Positive"`, `"Negative"`, `"Mixed / context-dependent"`, `"Candidate"` | VARCHAR(100) | Optional | Standard effect categories | Preserved verbatim from study |
| `mechanism_description`| Biological narrative of how the TF coordinates stress response. | Spreadsheet: *How it regulates stress* | `"Increases ascorbic acid (AsA) accumulation and thereby improves salt tolerance."` | TEXT | Optional | Free text narrative | Extracted directly from published findings |
| `validation_system`| Experimental experimental host or transgenic system used. | Spreadsheet: *Validation System* | `"Native tomato transgenic lines"`, `"Heterologous Arabidopsis"` | VARCHAR(255) | Optional | Free text | Preserved verbatim |
| `evidence_summary`| Laboratory techniques providing evidence. | Spreadsheet: *Evidence Type* | `"RNAi; transgenic phenotype; yeast one-hybrid"` | TEXT | Optional | Semicolon-delimited methods | Preserved verbatim |
| `raw_stress` | Verbatim stress string from source. | Spreadsheet: *Stress condition* | `"Drought, cold, osmotic stress"` | VARCHAR(255) | Required | Exact raw cell text | Preserved for 100% frontend UI compatibility |
| `raw_targets` | Verbatim targets and pathways string from source. | Spreadsheet: *Key Target(s) / Pathway* | `"SlSOS1 / SOS-mediated Na+ homeostasis"` | TEXT | Optional | Exact raw cell text | Preserved for display |
| `is_verified` | Indicates whether the transcription factor identity is verified. | Inferred from identifiers | `True` or `False` | BOOLEAN | Required | Default: `True` | Set to `False` if identifier is `"Not verified"` |
| `notes` | Curator comments and scientific observations. | Curator / Spreadsheet | `"Protein not verified in UniProtKB"` | TEXT | Optional | Free text | Used for uncertainty notes |
| `created_at` | Record creation timestamp. | System | `2026-10-08 12:00:00` | TIMESTAMP | Required | Valid ISO timestamp | System managed |
| `updated_at` | Record update timestamp. | System | `2026-10-08 12:00:00` | TIMESTAMP | Required | Valid ISO timestamp | System managed |

---

## 4. `stress_conditions`
Individual normalized stress types.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique identifier for the stress condition. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `stress_name` | Name of the specific stress condition. | Normalized from *Stress condition* | `"Salt stress"`, `"Drought"`, `"Cold"`, `"Nitrate stress"` | VARCHAR(100) | Required | Unique non-empty string | Standard plant stress terminology |
| `stress_type` | Broad classification of the stress. | Classified | `"Abiotic"`, `"Biotic"`, `"Nutrient / Metabolic"` | VARCHAR(50) | Optional | `Abiotic`, `Biotic`, `Nutrient`, `Other` | Curated category |
| `category` | Physiological grouping. | Classified | `"Osmotic"`, `"Temperature"`, `"Pathogen"`, `"Mineral"` | VARCHAR(50) | Optional | Category label | Curated grouping |

---

## 5. `tf_stress_associations`
Many-to-many junction table between TFs and individual stress conditions.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Junction entry ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `1` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `stress_id` | Foreign key referencing `stress_conditions.id`. | System | `3` | INTEGER (FK) | Required | Existing Stress ID | Cascade on delete |
| `specific_effect`| Specific direction of regulation for this individual condition. | Spreadsheet context | `"Positive"`, `"Negative"` | VARCHAR(100) | Optional | Effect string | Preserved if specified in paper |

---

## 6. `tf_identifiers`
Stores external biological database accession codes and identifiers for TFs.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique ID for the identifier entry. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `1` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `identifier_type` | Database source or type of identifier. | Spreadsheet: *Identifier Type* | `"UniProtKB"`, `"TAIR"`, `"NCBI Gene"`, `"Ensembl Plant"`, `"GenBank"` | VARCHAR(100) | Required | Standard database authority | Standard bio-identifier schemas |
| `identifier_value`| The clean accession code or locus ID. | Parsed from *Uniprot Accession ID...* | `"Q9FGD6"`, `"AT5G66940"`, `"836828"` | VARCHAR(100) | Required | Standard alphanumeric accession | Verified against accession regex; NEVER fabricated |
| `raw_supplied_text`| Verbatim raw text from spreadsheet cell. | Spreadsheet: *Uniprot Accession ID...* | `"AT2G33620; NCBI Gene 817928; UniProt O22812"` | TEXT | Optional | Complete original cell contents | Verbatim source preservation |
| `verification_status`| Status of verification. | Spreadsheet / Curator | `"Verified"`, `"Not verified"`, `"Candidate / Uncertain"` | VARCHAR(50) | Required | Defaults to `'Verified'` | Preserves explicit `"Not verified"` status |

---

## 7. `research_papers`
Bibliographic information for research publications documenting the TFs.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique identifier for the paper. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `title` | Full title of the research paper. | Spreadsheet: *Research paper * | `"The transcription factor SlDof22 involved in ascorbate accumulation and salinity stress in tomato."` | TEXT | Required | Non-empty string | Cleaned of decorative quotes |
| `journal` | Academic journal name. | Spreadsheet: *Journal* | `"Biochemical and Biophysical Research Communications"` | VARCHAR(255) | Optional | Journal name | Placeholders (`___`, `—`) converted to NULL |
| `year` | Publication year. | Spreadsheet: *Year* | `2016` | INTEGER | Optional | Positive integer (e.g. 1990–2026) | Cast from numeric/float |
| `doi` | Clean Digital Object Identifier. | Parsed from *DOI Number* | `"10.1016/j.bbrc.2016.04.148"` | VARCHAR(255) | Optional | Standard DOI format (`10.xxxx/...`) | Unique when present |
| `doi_url` | Full clickable web URL to article. | Spreadsheet: *DOI Number* | `"https://doi.org/10.1016/j.bbrc.2016.04.148"` | VARCHAR(500) | Optional | Valid HTTP/HTTPS URL | Tested for browser navigation |
| `pubmed_id` | PubMed PMID reference. | Literature lookup | `"27107797"` | VARCHAR(50) | Optional | Numeric PMID | Verified against NCBI PubMed |

---

## 8. `tf_paper_associations`
Many-to-many junction between transcription factors and research papers.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Junction ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `1` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `paper_id` | Foreign key referencing `research_papers.id`. | System | `1` | INTEGER (FK) | Required | Existing Paper ID | Cascade on delete |

---

## 9. `target_genes`
Downstream genes directly or indirectly regulated by the TF.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique ID for the target gene. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `gene_symbol` | Symbol or locus of the target gene. | Parsed from *Key Target(s) / Pathway* | `"SlSOS1"`, `"MdAPX3"`, `"WRKY33"` | VARCHAR(100) | Required | Gene symbol string | Standard plant gene symbols |
| `description` | Biological role of target gene. | Literature | `"Plasma membrane Na+/H+ antiporter"` | TEXT | Optional | Free text | Functional annotation |
| `plant_id` | Plant species in which target exists. | Lookup in `plants` | `1` | INTEGER (FK) | Optional | Valid Plant ID | Species linkage |

---

## 10. `tf_target_associations`
Junction table linking TFs to their downstream target genes.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Junction entry ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `1` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `target_gene_id`| Foreign key referencing `target_genes.id`. | System | `5` | INTEGER (FK) | Required | Existing Target Gene ID | Cascade on delete |
| `regulation_mode`| Nature of regulatory control. | Paper context | `"Direct activation"`, `"Direct repression"` | VARCHAR(100) | Optional | Mode string | Based on experimental assay |
| `evidence` | Experimental assay validating target. | Paper context | `"EMSA"`, `"ChIP-seq"`, `"Dual-luciferase"` | VARCHAR(255) | Optional | Assay name | Stored from publication |

---

## 11. `pathways`
Biological pathways and physiological processes modulated by TFs.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique pathway ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `pathway_name` | Name of physiological/signalling pathway. | Parsed from *Key Target(s) / Pathway* | `"Ascorbate recycling"`, `"SOS-mediated Na+ homeostasis"` | VARCHAR(255) | Required | Unique pathway name | Standard KEGG/Plant Reactome nomenclature |
| `pathway_type` | Broad category of the pathway. | Classified | `"Metabolic"`, `"Hormonal signalling"`, `"Antioxidant"` | VARCHAR(100) | Optional | Type category | Curated classification |

---

## 12. `tf_pathway_associations`
Junction table linking TFs to pathways.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Junction entry ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `1` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `pathway_id` | Foreign key referencing `pathways.id`. | System | `2` | INTEGER (FK) | Required | Existing Pathway ID | Cascade on delete |

---

## 13. `protein_sequences`
Stores amino acid sequence information and FASTA file references.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique sequence ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `1` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `accession` | Primary accession associated with sequence. | FASTA header / UniProt | `"Q9FGD6"`, `"O22812"` | VARCHAR(100) | Optional | Alphanumeric accession | Validated against UniProt |
| `fasta_header` | Complete FASTA definition line. | FASTA file: line 1 | `">sp\|Q9FGD6\|DOF58_ARATH Dof zinc finger protein DOF5.8..."` | VARCHAR(500) | Optional | Header line | Preserves original file line |
| `sequence` | Complete amino acid sequence. | FASTA file body | `"MSGSETGLMAATRESMQFTMALH..."` | TEXT | Required | Uppercase standard IUPAC amino acids | Cleaned of whitespace, digits, asterisks |
| `sequence_length`| Number of amino acid residues. | Computed | `348` | INTEGER | Required | Positive integer (`len(sequence)`) | Calculated programmatically |
| `molecular_weight`| Calculated molecular weight in Daltons. | Computed | `37420.5` | FLOAT | Optional | Positive float | Biopython / Isoelectric calculation |
| `source_file` | Relative path or filename in asset repository. | File system | `"AtDOF5.8.txt"` | VARCHAR(255) | Optional | Filename in `sequences/` | File existence checked |

---

## 14. `protein_structures`
Metadata, file references, and quality metrics for AlphaFold 3D protein structures.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique structure ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `3` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `model_identifier`| AlphaFold job or run identifier. | Directory name | `"AHL10_f311a"`, `"AtDOF58_7e6b1"` | VARCHAR(100) | Required | Folder name | Matches folder in `structures/` |
| `structure_type`| Type of structural coordinate model. | AlphaFold metadata | `"AlphaFold2"` | VARCHAR(50) | Required | Default: `'AlphaFold2'` | Model methodology |
| `pdb_file_path` | Relative file path to the rank 001 PDB coordinate file. | File system | `"structures/AHL10_f311a/...rank_001...pdb"` | VARCHAR(500) | Required | Valid relative file path | Verified on disk |
| `pae_image_path`| Relative path to Predicted Aligned Error plot. | File system | `"structures/AHL10_f311a/...pae.png"` | VARCHAR(500) | Optional | Image path | Verified on disk |
| `plddt_image_path`| Relative path to per-residue confidence plot. | File system | `"structures/AHL10_f311a/...plddt.png"` | VARCHAR(500) | Optional | Image path | Verified on disk |
| `coverage_image_path`| Relative path to MSA coverage plot. | File system | `"structures/AHL10_f311a/...coverage.png"` | VARCHAR(500) | Optional | Image path | Verified on disk |
| `mean_plddt` | Average per-residue model confidence score (0–100). | JSON score file | `84.32` | FLOAT | Optional | Float between 0.0 and 100.0 | Extracted from AlphaFold score JSON |

---

## 15. `protein_interactions`
Protein-protein interaction pairs, confidence scores, and network figure references.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique interaction ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `tf_id` | Foreign key referencing `transcription_factors.id`. | System | `60` | INTEGER (FK) | Required | Existing TF ID | Cascade on delete |
| `partner_name` | Name of the interacting protein. | STRING TSV: `node2` | `"ADM"`, `"SUVH9"`, `"MORC2"` | VARCHAR(100) | Required | Gene / protein symbol | Extracted from STRING TSV |
| `partner_uniprot`| UniProt ID of the partner protein. | STRING TSV: `node2_string_id` | `"Q9SZ59"`, `"Q9T0G7"` | VARCHAR(50) | Optional | Alphanumeric UniProt ID | Parsed from STRING format |
| `combined_score`| STRING overall interaction confidence score. | STRING TSV: `combined_score` | `0.740` | FLOAT | Required | Float between 0.000 and 1.000 | Direct value from STRING TSV |
| `experimental_score`| Evidence score from physical experiments. | STRING TSV | `0.000` | FLOAT | Optional | Float between 0.000 and 1.000 | From STRING TSV column |
| `database_score`| Evidence score from curated pathway databases. | STRING TSV | `0.000` | FLOAT | Optional | Float between 0.000 and 1.000 | From STRING TSV column |
| `textmining_score`| Evidence score from automated literature mining. | STRING TSV | `0.740` | FLOAT | Optional | Float between 0.000 and 1.000 | From STRING TSV column |
| `coexpression_score`| Evidence score from RNA co-expression. | STRING TSV | `0.046` | FLOAT | Optional | Float between 0.000 and 1.000 | From STRING TSV column |
| `source_database`| Origin database of interaction evidence. | Metadata | `"STRING"` | VARCHAR(50) | Required | Default: `'STRING'` | Provenance tag |
| `cytoscape_image_path`| Relative path to custom Cytoscape network diagram. | File system | `"interactions/cytoscape/AHL10.png"` | VARCHAR(500) | Optional | Image path | Verified on disk |
| `string_image_path`| Relative path to STRING evidence network figure. | File system | `"interactions/string/AHL10/...network.png"` | VARCHAR(500) | Optional | Image path | Verified on disk |

---

## 16. `import_audits`
Audit trail recording all dataset imports and modifications for data lineage.

| Field Name | Meaning | Source | Example | Data Type | Req / Opt | Allowed Values / Validation | Provenance & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique audit log ID. | Auto-generated | `1` | INTEGER (PK) | Required | Positive integer | Database generated |
| `source_filename`| Name and relative path of imported file. | Ingestion pipeline | `"data/raw/Transcription factors...xlsm"` | VARCHAR(255) | Required | Non-empty file path | Provenance record |
| `records_processed`| Total rows read from file. | Ingestion pipeline | `61` | INTEGER | Required | Non-negative integer | Computed during import |
| `records_inserted`| New records successfully created. | Ingestion pipeline | `61` | INTEGER | Required | Non-negative integer | Computed during import |
| `records_updated` | Existing records updated. | Ingestion pipeline | `0` | INTEGER | Required | Non-negative integer | Computed during import |
| `validation_warnings`| JSON or textual list of warnings encountered. | Ingestion pipeline | `"[{\"row\": 1, \"warning\": \"Unverified UniProt\"}]"` | TEXT | Optional | JSON string | Log of anomalies |
| `imported_at` | Timestamp when import completed. | System | `2026-10-08 12:30:00` | TIMESTAMP | Required | Valid ISO timestamp | System clock |
