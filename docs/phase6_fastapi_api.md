# Phase 6 — FastAPI Backend API Documentation

**Project:** PhytoStress TF Atlas Database Website  
**Project root:** `F:\OMICSNOVA BIOLOGICAL INTELLIGENCE`  
**API entry point:** `backend.api.main:app`  
**Database:** `phytostress.db` (SQLite, read-only for API)  
**Interactive docs:** `http://127.0.0.1:8000/docs` (Swagger UI)  
**OpenAPI spec:** `http://127.0.0.1:8000/openapi.json`

---

## Launch Command

```bash
# From project root
uvicorn backend.api.main:app --reload
```

Default host: `127.0.0.1`, port `8000`.

---

## CORS Configuration

The API allows cross-origin requests from:

| Origin |
|--------|
| `http://localhost:3000` |
| `http://localhost:5173` |
| `http://127.0.0.1:3000` |
| `http://127.0.0.1:5173` |

Allowed methods: `GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`  
Allowed headers: `*`  
Credentials: allowed

---

## Common Response Patterns

### Paginated List

All collection endpoints return a paginated envelope:

```json
{
  "total": 63,
  "page": 1,
  "page_size": 20,
  "items": [ ... ]
}
```

**Pagination query parameters** (all collection endpoints):

| Parameter | Type | Default | Constraints | Description |
|-----------|------|---------|-------------|-------------|
| `page` | int | `1` | ≥ 1 | Page number |
| `page_size` | int | `20` | 1 – 100 | Items per page |

### Error Responses

| Status | Meaning |
|--------|---------|
| `404 Not Found` | Resource with the given ID does not exist |
| `422 Unprocessable Entity` | Invalid query parameter (e.g. `page_size=0`) |

---

## Endpoints

### Health

#### `GET /api/health`

Liveness check — performs a live `SELECT 1` against the database.

**Response 200:**
```json
{ "status": "ok", "database": "connected" }
```

---

### Transcription Factors

#### `GET /api/transcription-factors`

Return a paginated list of all TF records.

**Query parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `family` | string (optional) | Filter by TF family name (case-insensitive substring) |
| `plant` | string (optional) | Filter by plant common name (case-insensitive substring) |
| `stress` | string (optional) | Filter by stress condition name (case-insensitive substring) |
| `search` | string (optional) | Full-text substring search on `tf_name` |
| `page` | int | Page number |
| `page_size` | int | Items per page |

**Example:** `GET /api/transcription-factors?family=WRKY&page=1&page_size=10`

**Response 200 — item schema (`TFSummaryOut`):**
```json
{
  "id": 1,
  "tf_name": "WRKY40",
  "gene_locus": "AT1G80840",
  "expression_pattern": "stress-induced",
  "functional_role": "transcriptional activator",
  "regulation_type": "positive",
  "plant_id": 1,
  "family_id": 2,
  "plant": { "id": 1, "scientific_name": "Arabidopsis thaliana", "common_name": "Arabidopsis thaliana" },
  "family": { "id": 2, "name": "WRKY", "description": "..." }
}
```

---

#### `GET /api/transcription-factors/{tf_id}`

Return detail for a single TF including linked stress associations and paper associations.

**Response 200 — schema (`TFDetailOut`):**  
Extends `TFSummaryOut` with:
```json
{
  "identifiers": [ { "id": 1, "identifier_type": "UniProt", "identifier_value": "Q9SYV0", "is_verified": true } ],
  "stresses": [ { "id": 5, "name": "drought", "category": "abiotic", "association_evidence": "ChIP-seq" } ],
  "papers": [ { "id": 3, "title": "...", "doi": "10.xxx", "year": 2022 } ]
}
```

---

#### `GET /api/transcription-factors/{tf_id}/full`

Return the complete biological dossier for a TF: all 11 linked facets.

**Response 200 — schema (`TFFullOut`):**  
Extends `TFDetailOut` with:
```json
{
  "targets": [ { "id": 12, "gene_symbol": "RD29A", "description": "..." } ],
  "pathways": [ { "id": 7, "pathway_name": "ABA signaling", "pathway_database": "KEGG", "pathway_id": "ath04075" } ],
  "sequences": [ { "id": 1, "sequence_header": "...", "sequence_length": 302, "sequence_text": "MASE..." } ],
  "structures": [ { "id": 1, "pdb_file_path": "...", "confidence_score": 0.93, "model_rank": 1 } ],
  "interactions": [ { "id": 1, "partner_protein": "AT2G38470", "combined_score": 0.85, "interaction_source": "STRING" } ]
}
```

---

#### `GET /api/transcription-factors/{tf_id}/sequence`

Return all protein sequences linked to this TF.

**Response 200:** list of `ProteinSequenceOut` objects.

---

#### `GET /api/transcription-factors/{tf_id}/structures`

Return all AlphaFold structure records linked to this TF.

**Response 200:** list of `ProteinStructureOut` objects.

---

#### `GET /api/transcription-factors/{tf_id}/interactions`

Return all protein-protein interaction records where this TF is the query protein.

**Response 200:** list of `ProteinInteractionOut` objects.

---

### Plants

#### `GET /api/plants`

Return a paginated list of all plant records.

**Response 200 item schema (`PlantOut`):**
```json
{
  "id": 1,
  "scientific_name": "Arabidopsis thaliana",
  "common_name": "Arabidopsis thaliana",
  "taxonomy_id": "3702",
  "genome_database": "TAIR"
}
```

---

#### `GET /api/plants/{plant_id}`

Return detail for one plant including all TFs associated with it.

**Response 200 — schema (`PlantDetailOut`):**  
Extends `PlantOut` with:
```json
{
  "transcription_factors": [
    { "id": 1, "tf_name": "WRKY40", "family_id": 2 }
  ]
}
```

---

### TF Families

#### `GET /api/families`

Return a paginated list of all TF family records.

**Response 200 item schema (`TFFamilyOut`):**
```json
{
  "id": 2,
  "name": "WRKY",
  "description": "WRKY domain-containing transcription factors",
  "conserved_domain": "WRKY",
  "member_count": 7
}
```

---

#### `GET /api/families/{family_id}`

Return detail for one TF family including all member TFs.

**Response 200 — schema (`TFFamilyDetailOut`):**  
Extends `TFFamilyOut` with:
```json
{
  "transcription_factors": [
    { "id": 1, "tf_name": "WRKY40" }
  ]
}
```

---

### Stress Conditions

#### `GET /api/stress-conditions`

Return a paginated list of all stress condition records.

**Response 200 item schema (`StressConditionOut`):**
```json
{
  "id": 5,
  "name": "drought",
  "category": "abiotic",
  "description": "Water deficit stress"
}
```

---

#### `GET /api/stress-conditions/{stress_id}`

Return detail for one stress condition including all TF associations.

**Response 200 — schema (`StressConditionDetailOut`):**  
Extends `StressConditionOut` with:
```json
{
  "transcription_factors": [
    { "id": 1, "tf_name": "WRKY40", "association_evidence": "qRT-PCR" }
  ]
}
```

---

### Research Papers

#### `GET /api/papers`

Return a paginated list of all research paper records.

**Response 200 item schema (`ResearchPaperOut`):**
```json
{
  "id": 3,
  "title": "WRKY transcription factors in drought response",
  "authors": "Smith et al.",
  "journal": "Plant Cell",
  "year": 2022,
  "doi": "10.1093/plcell/koab123",
  "pubmed_id": "34012345"
}
```

---

#### `GET /api/papers/{paper_id}`

Return detail for one paper including all linked TFs.

**Response 200 — schema (`ResearchPaperDetailOut`):**  
Extends `ResearchPaperOut` with:
```json
{
  "transcription_factors": [
    { "id": 1, "tf_name": "WRKY40" }
  ]
}
```

---

### Pathways

#### `GET /api/pathways`

Return a paginated list of all pathway records.

**Response 200 item schema (`PathwayOut`):**
```json
{
  "id": 7,
  "pathway_name": "ABA signaling pathway",
  "pathway_database": "KEGG",
  "pathway_id": "ath04075"
}
```

---

#### `GET /api/pathways/{pathway_id}`

Return detail for one pathway including all linked TFs.

**Response 200 — schema (`PathwayDetailOut`):**  
Extends `PathwayOut` with:
```json
{
  "transcription_factors": [
    { "id": 1, "tf_name": "WRKY40" }
  ]
}
```

---

### Target Genes

#### `GET /api/targets`

Return a paginated list of all target gene records.

**Response 200 item schema (`TargetGeneOut`):**
```json
{
  "id": 12,
  "gene_symbol": "RD29A",
  "gene_locus": "AT5G52310",
  "description": "Responsive to desiccation 29A",
  "organism": "Arabidopsis thaliana"
}
```

---

#### `GET /api/targets/{target_id}`

Return detail for one target gene including all TFs that regulate it.

**Response 200 — schema (`TargetGeneDetailOut`):**  
Extends `TargetGeneOut` with:
```json
{
  "transcription_factors": [
    { "id": 1, "tf_name": "WRKY40" }
  ]
}
```

---

### Protein Sequences

#### `GET /api/sequences`

Return a paginated list of all protein sequence records.

**Response 200 item schema (`ProteinSequenceOut`):**
```json
{
  "id": 1,
  "tf_id": 1,
  "sequence_header": ">sp|Q9SYV0|WRKY40_ARATH",
  "sequence_text": "MASEKNEE...",
  "sequence_length": 302,
  "molecular_weight": 33872.5,
  "source_fasta_file": "sequences/ATWRKY40.fasta"
}
```

---

#### `GET /api/sequences/{sequence_id}`

Return a single protein sequence record by ID.

---

### Protein Structures

#### `GET /api/structures`

Return a paginated list of all AlphaFold structure records.

**Response 200 item schema (`ProteinStructureOut`):**
```json
{
  "id": 1,
  "tf_id": 1,
  "pdb_file_path": "alphafold/ATWRKY40/ranked_0.pdb",
  "model_rank": 1,
  "confidence_score": 0.93,
  "is_template_based": false,
  "diagnostic_plot_path": "alphafold/ATWRKY40/plddt_plot.png"
}
```

---

#### `GET /api/structures/{structure_id}`

Return a single AlphaFold structure record by ID.

---

### Protein Interactions

#### `GET /api/interactions`

Return a paginated list of all protein-protein interaction records.

**Response 200 item schema (`ProteinInteractionOut`):**
```json
{
  "id": 1,
  "tf_id": 1,
  "partner_protein": "AT2G38470",
  "interaction_source": "STRING",
  "combined_score": 0.85,
  "experimental_score": 0.72,
  "coexpression_score": 0.60,
  "neighborhood_score": 0.0,
  "fusion_score": 0.0,
  "cooccurrence_score": 0.0,
  "textmining_score": 0.45,
  "database_score": 0.80,
  "has_cytoscape_visualization": true,
  "cytoscape_image_path": "cytoscape/ATWRKY40/network.png"
}
```

---

#### `GET /api/interactions/{interaction_id}`

Return a single protein interaction record by ID.

---

### Search

#### `GET /api/search?q={term}`

Global multi-facet search across TF names, stress conditions, plants, and TF families.

**Query parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search term (case-insensitive substring match) |

**Example:** `GET /api/search?q=drought`

**Response 200 — schema (`SearchResultOut`):**
```json
{
  "query": "drought",
  "total_matches": 23,
  "transcription_factors": [
    { "id": 1, "tf_name": "WRKY40", "match_field": "stress_condition", "match_value": "drought" }
  ],
  "stress_conditions": [
    { "id": 5, "name": "drought", "category": "abiotic" }
  ],
  "plants": [],
  "families": []
}
```

---

## File Structure

```
backend/
├── api/
│   ├── __init__.py          # re-exports app
│   ├── main.py              # FastAPI app, CORS, route registration
│   ├── dependencies.py      # get_pagination() dependency
│   └── routes/
│       ├── __init__.py
│       ├── health.py
│       ├── transcription_factors.py
│       ├── plants.py
│       ├── families.py
│       ├── stress_conditions.py
│       ├── papers.py
│       ├── pathways.py
│       ├── targets.py
│       ├── sequences.py
│       ├── structures.py
│       ├── interactions.py
│       └── search.py
├── schemas/
│   ├── __init__.py
│   ├── pagination.py
│   ├── transcription_factors.py
│   ├── plants.py
│   ├── families.py
│   ├── stress_conditions.py
│   ├── papers.py
│   ├── pathways.py
│   ├── targets.py
│   ├── sequences.py
│   ├── structures.py
│   ├── interactions.py
│   └── search.py
└── tests/
    └── test_api.py          # 19 FastAPI API tests
```

---

## Endpoint Summary Table

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Liveness check |
| GET | `/api/transcription-factors` | Paginated TF list (filterable) |
| GET | `/api/transcription-factors/{id}` | TF detail with stresses, papers, identifiers |
| GET | `/api/transcription-factors/{id}/full` | Complete biological dossier (11 facets) |
| GET | `/api/transcription-factors/{id}/sequence` | TF protein sequences |
| GET | `/api/transcription-factors/{id}/structures` | TF AlphaFold structures |
| GET | `/api/transcription-factors/{id}/interactions` | TF protein interactions |
| GET | `/api/plants` | Paginated plant list |
| GET | `/api/plants/{id}` | Plant detail with TF list |
| GET | `/api/families` | Paginated TF family list |
| GET | `/api/families/{id}` | Family detail with member TFs |
| GET | `/api/stress-conditions` | Paginated stress condition list |
| GET | `/api/stress-conditions/{id}` | Stress detail with associated TFs |
| GET | `/api/papers` | Paginated research paper list |
| GET | `/api/papers/{id}` | Paper detail with linked TFs |
| GET | `/api/pathways` | Paginated pathway list |
| GET | `/api/pathways/{id}` | Pathway detail with linked TFs |
| GET | `/api/targets` | Paginated target gene list |
| GET | `/api/targets/{id}` | Target gene detail with regulators |
| GET | `/api/sequences` | Paginated protein sequence list |
| GET | `/api/sequences/{id}` | Single protein sequence record |
| GET | `/api/structures` | Paginated AlphaFold structure list |
| GET | `/api/structures/{id}` | Single structure record |
| GET | `/api/interactions` | Paginated protein interaction list |
| GET | `/api/interactions/{id}` | Single interaction record |
| GET | `/api/search` | Global multi-facet search |

**Total: 25 endpoints**
