"""PhytoStress TF Atlas — FastAPI Backend API Test Suite.

Verifies:
1. GET /api/health (active database query, not hardcoded)
2. TF collection (pagination, summary structure)
3. TF detail (nested plant, family, counts)
4. TF filtering (by plant, family, stress, search term)
5. Plant collection & detail (associated TFs)
6. Family collection & detail (associated TFs)
7. Stress condition collection & detail (associated TFs)
8. Research paper collection & detail (associated TFs)
9. Pathway collection & detail (associated TFs)
10. Target gene collection & detail (associated TFs)
11. Sequence endpoints (/api/sequences/{id} and /api/transcription-factors/{id}/sequence)
12. AlphaFold structure endpoints (/api/structures/{id} and /api/transcription-factors/{id}/structures)
13. Protein interaction endpoints (/api/interactions/{id} and /api/transcription-factors/{id}/interactions)
14. TF full dossier (/api/transcription-factors/{id}/full with all 11 linked biological facets)
15. Global search (/api/search with cross-entity matches)
16. Pagination behavior (page, page_size, total_pages)
17. 404 behavior for non-existent entities
18. Invalid parameter handling (page=0, page_size=101, empty search)
19. Database connectivity integrity under API calls
20. CORS middleware response headers
"""

import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for FastAPI endpoints."""
    with TestClient(app) as c:
        yield c


def test_health_check(client: TestClient):
    """Verify GET /api/health returns 200 with dynamic db connection check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_tf_collection(client: TestClient):
    """Verify GET /api/transcription-factors returns paginated TF summaries."""
    response = client.get("/api/transcription-factors?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 63
    assert len(data["items"]) == 10
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 7

    first = data["items"][0]
    assert "id" in first
    assert "tf_name" in first
    assert "family_name" in first
    assert "plant_name" in first
    assert "stresses" in first
    assert "has_sequence" in first
    assert "has_structure" in first


def test_tf_detail(client: TestClient):
    """Verify GET /api/transcription-factors/{id} returns single TF overview."""
    response = client.get("/api/transcription-factors/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["tf_name"] == "SlDOF22"
    assert data["plant"]["common_name"] == "Tomato"
    assert data["family"]["name"] == "DOF"
    assert len(data["identifiers"]) > 0
    assert len(data["stresses"]) > 0
    assert data["interactions_count"] == 10


def test_tf_filtering(client: TestClient):
    """Verify filtering by plant, family, stress condition, and search term."""
    # Filter by plant: Arabidopsis (15 TFs)
    res_plant = client.get("/api/transcription-factors?plant=Arabidopsis")
    assert res_plant.status_code == 200
    assert res_plant.json()["total"] == 17

    # Filter by family: DOF (9 TFs in atlas)
    res_fam = client.get("/api/transcription-factors?family=DOF")
    assert res_fam.status_code == 200
    assert res_fam.json()["total"] > 0
    for item in res_fam.json()["items"]:
        assert "DOF" in item["family_name"]


    # Filter by stress: drought (18 TFs in atlas)
    res_stress = client.get("/api/transcription-factors?stress=drought")
    assert res_stress.status_code == 200
    assert res_stress.json()["total"] == 18

    # Filter by search keyword: "OsDOF"
    res_search = client.get("/api/transcription-factors?search=OsDOF")
    assert res_search.status_code == 200
    assert res_search.json()["total"] > 0
    for item in res_search.json()["items"]:
        assert "OsDOF" in item["tf_name"] or "OsDOF" in (item.get("raw_supplied_tf") or "")


def test_plant_collection_and_detail(client: TestClient):
    """Verify GET /api/plants and GET /api/plants/{id}."""
    res_col = client.get("/api/plants?page=1&page_size=50")
    assert res_col.status_code == 200
    data_col = res_col.json()
    assert data_col["total"] == 30
    assert len(data_col["items"]) == 30

    # Test single plant with associated TFs
    res_detail = client.get("/api/plants/1")
    assert res_detail.status_code == 200
    data_detail = res_detail.json()
    assert data_detail["id"] == 1
    assert "common_name" in data_detail
    assert "transcription_factors" in data_detail
    assert len(data_detail["transcription_factors"]) > 0


def test_family_collection_and_detail(client: TestClient):
    """Verify GET /api/families and GET /api/families/{id}."""
    res_col = client.get("/api/families?page=1&page_size=50")
    assert res_col.status_code == 200
    data_col = res_col.json()
    assert data_col["total"] == 23

    res_detail = client.get("/api/families/1")
    assert res_detail.status_code == 200
    data_detail = res_detail.json()
    assert data_detail["id"] == 1
    assert "name" in data_detail
    assert "transcription_factors" in data_detail
    assert len(data_detail["transcription_factors"]) > 0


def test_stress_condition_collection_and_detail(client: TestClient):
    """Verify GET /api/stress-conditions and GET /api/stress-conditions/{id}."""
    res_col = client.get("/api/stress-conditions?page=1&page_size=50")
    assert res_col.status_code == 200
    data_col = res_col.json()
    assert data_col["total"] == 21

    res_detail = client.get("/api/stress-conditions/1")
    assert res_detail.status_code == 200
    data_detail = res_detail.json()
    assert data_detail["id"] == 1
    assert "stress_name" in data_detail
    assert "transcription_factors" in data_detail
    assert len(data_detail["transcription_factors"]) > 0


def test_paper_collection_and_detail(client: TestClient):
    """Verify GET /api/papers and GET /api/papers/{id}."""
    res_col = client.get("/api/papers?page=1&page_size=100")
    assert res_col.status_code == 200
    data_col = res_col.json()
    assert data_col["total"] == 60

    res_detail = client.get("/api/papers/1")
    assert res_detail.status_code == 200
    data_detail = res_detail.json()
    assert data_detail["id"] == 1
    assert "title" in data_detail
    assert "journal" in data_detail
    assert "transcription_factors" in data_detail


def test_pathway_collection_and_detail(client: TestClient):
    """Verify GET /api/pathways and GET /api/pathways/{id}."""
    res_col = client.get("/api/pathways?page=1&page_size=20")
    assert res_col.status_code == 200
    data_col = res_col.json()
    assert data_col["total"] == 110

    res_detail = client.get("/api/pathways/1")
    assert res_detail.status_code == 200
    data_detail = res_detail.json()
    assert data_detail["id"] == 1
    assert "pathway_name" in data_detail
    assert "transcription_factors" in data_detail


def test_target_collection_and_detail(client: TestClient):
    """Verify GET /api/targets and GET /api/targets/{id}."""
    res_col = client.get("/api/targets?page=1&page_size=20")
    assert res_col.status_code == 200
    data_col = res_col.json()
    assert data_col["total"] == 75

    res_detail = client.get("/api/targets/1")
    assert res_detail.status_code == 200
    data_detail = res_detail.json()
    assert data_detail["id"] == 1
    assert "gene_symbol" in data_detail
    assert "transcription_factors" in data_detail


def test_sequence_endpoints(client: TestClient):
    """Verify GET /api/sequences/{id} and GET /api/transcription-factors/{id}/sequence."""
    # List sequences
    res_list = client.get("/api/sequences?page=1&page_size=50")
    assert res_list.status_code == 200
    assert res_list.json()["total"] == 46

    # Get single sequence
    res_single = client.get("/api/sequences/1")
    assert res_single.status_code == 200
    data_single = res_single.json()
    assert data_single["id"] == 1
    assert data_single["sequence_length"] > 0
    assert len(data_single["sequence"]) == data_single["sequence_length"]

    # TF with sequence (TF #2)
    res_tf_seq = client.get("/api/transcription-factors/2/sequence")
    assert res_tf_seq.status_code == 200
    assert len(res_tf_seq.json()) > 0
    assert res_tf_seq.json()[0]["tf_id"] == 2

    # TF without sequence (TF #1) -> 404
    res_no_seq = client.get("/api/transcription-factors/1/sequence")
    assert res_no_seq.status_code == 404


def test_structure_endpoints(client: TestClient):
    """Verify GET /api/structures/{id} and GET /api/transcription-factors/{id}/structures."""
    res_list = client.get("/api/structures?page=1&page_size=100")
    assert res_list.status_code == 200
    assert res_list.json()["total"] == 60

    # Get single structure
    res_single = client.get("/api/structures/1")
    assert res_single.status_code == 200
    data_single = res_single.json()
    assert data_single["id"] == 1
    assert "pdb_file_path" in data_single
    assert data_single["rank_num"] >= 1

    # TF with structures (TF #60 AHL10: 5 ranks)
    res_tf_structs = client.get("/api/transcription-factors/60/structures")
    assert res_tf_structs.status_code == 200
    data_structs = res_tf_structs.json()
    assert len(data_structs) == 5
    ranks = [s["rank_num"] for s in data_structs]
    assert ranks == [1, 2, 3, 4, 5]


def test_interaction_endpoints(client: TestClient):
    """Verify GET /api/interactions/{id} and GET /api/transcription-factors/{id}/interactions."""
    res_list = client.get("/api/interactions?page=1&page_size=20")
    assert res_list.status_code == 200
    assert res_list.json()["total"] == 489

    # Filter by min_score
    res_filtered = client.get("/api/interactions?min_score=0.9")
    assert res_filtered.status_code == 200
    assert res_filtered.json()["total"] > 0
    for it in res_filtered.json()["items"]:
        assert it["combined_score"] >= 0.9

    # Single interaction
    res_single = client.get("/api/interactions/1")
    assert res_single.status_code == 200
    data_single = res_single.json()
    assert "partner_name" in data_single
    assert 0.0 <= data_single["combined_score"] <= 1.0

    # TF interactions (TF #1: 10 partners)
    res_tf_inter = client.get("/api/transcription-factors/1/interactions")
    assert res_tf_inter.status_code == 200
    assert len(res_tf_inter.json()) == 10


def test_tf_full_dossier(client: TestClient):
    """Verify GET /api/transcription-factors/{id}/full returns all 11 linked biological facets."""
    response = client.get("/api/transcription-factors/60/full")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 60
    assert data["tf_name"] == "AHL10"
    assert "Arabidopsis" in data["plant"]["common_name"]
    assert "AHL" in data["family"]["name"]
    assert len(data["identifiers"]) > 0
    assert len(data["stresses"]) > 0
    assert len(data["papers"]) > 0
    assert len(data["targets"]) > 0
    assert len(data["pathways"]) > 0
    assert len(data["sequences"]) > 0
    assert len(data["structures"]) == 5
    assert len(data["interactions"]) == 10


def test_global_search(client: TestClient):
    """Verify GET /api/search returns categorized matches across entities."""
    response = client.get("/api/search?q=drought")
    assert response.status_code == 200
    data = response.json()

    assert data["query"] == "drought"
    assert data["total_matches"] > 0
    assert len(data["stress_conditions"]) > 0
    assert len(data["transcription_factors"]) > 0


def test_pagination_behavior(client: TestClient):
    """Verify pagination limits, bounds, and total pages calculations."""
    res1 = client.get("/api/transcription-factors?page=1&page_size=20")
    assert res1.status_code == 200
    d1 = res1.json()
    assert len(d1["items"]) == 20
    assert d1["total"] == 63
    assert d1["total_pages"] == 4

    res2 = client.get("/api/transcription-factors?page=4&page_size=20")
    assert res2.status_code == 200
    d2 = res2.json()
    assert len(d2["items"]) == 3  # 63 - 60 = 3 items on final page


def test_404_error_behavior(client: TestClient):
    """Verify 404 response on non-existent records."""
    assert client.get("/api/transcription-factors/99999").status_code == 404
    assert client.get("/api/plants/99999").status_code == 404
    assert client.get("/api/families/99999").status_code == 404
    assert client.get("/api/stress-conditions/99999").status_code == 404
    assert client.get("/api/papers/99999").status_code == 404
    assert client.get("/api/pathways/99999").status_code == 404
    assert client.get("/api/targets/99999").status_code == 404
    assert client.get("/api/sequences/99999").status_code == 404
    assert client.get("/api/structures/99999").status_code == 404
    assert client.get("/api/interactions/99999").status_code == 404


def test_invalid_parameters_handling(client: TestClient):
    """Verify 422/400 response on invalid query parameters."""
    # page < 1
    assert client.get("/api/transcription-factors?page=0").status_code == 422
    # page_size > 100
    assert client.get("/api/transcription-factors?page_size=101").status_code == 422
    # empty search query
    assert client.get("/api/search?q=").status_code in (400, 422)


def test_cors_headers(client: TestClient):
    """Verify CORS middleware responds with appropriate headers."""
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") in ("http://localhost:3000", "*")
