"""
PhytoStress TF Atlas - Phase 5D: STRING & FunCoup Interaction Ingestion
======================================================================
Parses, normalizes, validates, and imports protein-protein interaction (PPI)
data from 45 packages in STRING database information and associates them with
curated transcription factors in the PhytoStress database. Also links visual
network diagrams from Cytoscape and STRING.

Usage:
    python scripts/import_string.py [--dry-run] [--force] [--verbose]
"""

import os
import sys
import csv
import argparse
import logging
from typing import Dict, List, Optional, Tuple, Any

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath("."))
from backend.app.database import SessionLocal
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.interaction import ProteinInteraction

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Base source directories
STRING_ROOT = os.path.normpath("STRING database information-20261008T053421Z-1-001/STRING database information")
CYTOSCAPE_ROOT = os.path.normpath("Cytoscape protein interactions-20261008T053406Z-1-001/Cytoscape protein interactions")

# Authoritative deterministic mapping of 45 STRING directories to Database TF ID(s)
DIR_TO_TF_IDS: Dict[str, List[int]] = {
    "AHL10": [60],
    "AtBBX21": [53],
    "AtC3H14": [63],
    "AtC3H15": [62],
    "AtDOF5.8": [3],
    "AtPLATZ2": [54],
    "AtPLATZ4": [55],
    "BnCDF1": [9],
    "C3H47": [61],
    "CAMTA3": [43],
    "CDF3": [5],
    "EIN3": [45],
    "GT2": [48],
    "GhGT-3b_A04": [49],
    "GmNLP7a": [40],
    "MdDOF54": [7],
    "MtNLP1": [31],
    "NLP7": [29, 30, 34, 35],
    "NLP8": [39],
    "OsADR3": [51],
    "OsDOF1": [12],
    "OsDOF18": [15],
    "OsGATA8": [42],
    "OsMADS25": [21, 22],
    "OsMADS3": [20],
    "OsNLP1": [28],
    "OsNLP2": [28, 37],
    "OsNLP3": [28],
    "OsNLP4": [38],
    "PtrLBD41": [46],
    "SLNLP1": [33],
    "SlBZR1-SlBZR1D": [59],
    "SlCDF1": [6],
    "SlCDF3": [6],
    "SlDOF22": [1],
    "SlGATA17": [52],
    "SlMBP11": [16],
    "SlMBP8": [17],
    "SlNLP5": [33],
    "TDR6": [23],
    "TaMADS51": [19],
    "TaZNF": [2],
    "VOZ1": [44],
    "VOZ2": [44],
    "ZmBES1-BZR1": [58],
}

# Mapping of Cytoscape PNG files to STRING directories
CYTOSCAPE_MAPPING: Dict[str, str] = {
    "AHL10": "AHL10.png",
    "AtC3H14": "AtC3H14.png",
    "AtC3H15": "AtC3H15.png",
    "AtDOF5.8": "AtDOF5.8.png",
    "NLP8": "AtNLP8.png",
    "AtPLATZ2": "AtPLATZ2.png",
    "AtPLATZ4": "AtPLATZ4.png",
    "ZmBES1-BZR1": "BZR1.png",
    "BnCDF1": "BnCDF1 similar protein.png",
    "CAMTA3": "CAMTA3.png",
    "EIN3": "EIN3.png",
    "MtNLP1": "MtNLP1.png",
    "OsNLP1": "NLP1.png",
    "OsNLP2": "NLP2.png",
    "OsNLP3": "NLP3.png",
    "NLP7": "NLP7.png",
    "OsADR3": "OsADR3.png",
    "C3H47": "OsC3H47.png",
    "OsDOF1": "OsDOF1 similar protein.png",
    "OsDOF18": "OsDOF18.png",
    "OsMADS25": "OsMADS25.png",
    "OsMADS3": "OsMADS3.png",
    "OsNLP4": "OsNLP4.png",
    "SlMBP11": "SlMBP11.png",
    "SlMBP8": "SlMBP8.png",
    "SLNLP1": "SlNLP1.png",
    "SlNLP5": "SlNLP5.png",
    "TDR6": "TDR6.png",
    "TaMADS51": "TaMADS51 similar protein.png",
    "TaZNF": "TaZNF.png",
    "VOZ1": "VOZ1.png",
    "VOZ2": "VOZ2.png",
}


def find_focal_node(d_name: str, d_path: str, files: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Identifies the focal query node from the package.
    In STRING, the query node is marked with color rgb(255,0,0) in string_coordinates_*.tsv.
    In FunCoup (OsDOF18), the query protein is Q6ZBQ1 (identifier 39947.Q6ZBQ1).
    """
    if d_name == "OsDOF18":
        return "Q6ZBQ1", "39947.Q6ZBQ1"

    coord_f = next((f for f in files if "coordinates" in f and f.endswith(".tsv")), None)
    if not coord_f:
        return None, None

    coord_path = os.path.join(d_path, coord_f)
    with open(coord_path, "r", encoding="utf-8", errors="replace") as cf:
        reader = csv.DictReader(cf, delimiter="\t")
        for row in reader:
            color = row.get("color", "").replace(" ", "")
            if "255,0,0" in color:
                return row.get("#node"), row.get("identifier")

    return None, None


def find_network_images(d_name: str, d_path: str, files: List[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Finds relative paths (with forward slashes) for STRING network image and Cytoscape image.
    """
    # 1. STRING diagram
    string_img_rel = None
    if d_name == "OsDOF18":
        if "FunCoup_subnetwork.png" in files:
            string_img_rel = f"{STRING_ROOT}/{d_name}/FunCoup_subnetwork.png".replace("\\", "/")
    else:
        hires = [f for f in files if "evidence_network_hires" in f and f.endswith(".png")]
        if hires:
            string_img_rel = f"{STRING_ROOT}/{d_name}/{hires[0]}".replace("\\", "/")
        else:
            reg = [f for f in files if "evidence_network" in f and f.endswith(".png")]
            if reg:
                string_img_rel = f"{STRING_ROOT}/{d_name}/{reg[0]}".replace("\\", "/")

    # 2. Cytoscape image
    cyto_img_rel = None
    if d_name in CYTOSCAPE_MAPPING:
        cyto_fname = CYTOSCAPE_MAPPING[d_name]
        cyto_full = os.path.join(CYTOSCAPE_ROOT, cyto_fname)
        if os.path.exists(cyto_full):
            cyto_img_rel = f"{CYTOSCAPE_ROOT}/{cyto_fname}".replace("\\", "/")

    return string_img_rel, cyto_img_rel


def parse_package(d_name: str) -> List[Dict[str, Any]]:
    """
    Parses a single STRING or FunCoup directory and extracts direct interaction records.
    """
    d_path = os.path.join(STRING_ROOT, d_name)
    if not os.path.isdir(d_path):
        raise FileNotFoundError(f"Package directory not found: {d_path}")

    files = sorted(os.listdir(d_path))
    focal_node, focal_id = find_focal_node(d_name, d_path, files)
    if not focal_node:
        raise ValueError(f"Focal red node could not be identified in {d_name}")

    string_img, cyto_img = find_network_images(d_name, d_path, files)

    # Locate interaction TSV
    if d_name == "OsDOF18":
        inter_file = "FunCoup_subnetwork.tsv"
        source_db = "FunCoup"
    else:
        inter_candidates = [f for f in files if "interactions" in f and "short" not in f and f.endswith(".tsv")]
        if not inter_candidates:
            raise FileNotFoundError(f"No interactions TSV found in {d_name}")
        inter_file = inter_candidates[0]
        source_db = "STRING"

    tsv_path = os.path.join(d_path, inter_file)
    tsv_rel_path = f"{STRING_ROOT}/{d_name}/{inter_file}".replace("\\", "/")

    # Extract direct interactions with focal query node
    direct_edges: Dict[str, Dict[str, Any]] = {}

    if source_db == "FunCoup":
        with open(tsv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                pA = row.get("#ProteinA")
                pB = row.get("ProteinB")
                partner = pB if pA == focal_node else (pA if pB == focal_node else None)
                if partner:
                    try:
                        ppv = float(row.get("PPV", 0.0))
                    except ValueError:
                        ppv = 0.0
                    
                    if partner not in direct_edges or ppv > direct_edges[partner]["combined_score"]:
                        direct_edges[partner] = {
                            "partner_name": partner,
                            "partner_uniprot": partner,
                            "combined_score": ppv,
                            "experimental_score": None,
                            "database_score": None,
                            "textmining_score": None,
                            "coexpression_score": None,
                            "source_database": "FunCoup",
                            "source_file": tsv_rel_path,
                            "string_image_path": string_img,
                            "cytoscape_image_path": cyto_img,
                            "validation_status": "Verified",
                            "notes": f"FunCoup PPV={ppv}; GoldStandard={row.get('GoldStandard')}; FBS_max={row.get('FBS_max')}; query={focal_node}"
                        }
    else:
        with open(tsv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                n1 = row.get("#node1")
                n2 = row.get("node2")
                
                partner = None
                partner_str_id = None
                if n1 == focal_node:
                    partner = n2
                    partner_str_id = row.get("node2_string_id")
                elif n2 == focal_node:
                    partner = n1
                    partner_str_id = row.get("node1_string_id")

                if partner:
                    try:
                        combined = float(row.get("combined_score", 0.0))
                    except ValueError:
                        combined = 0.0
                    
                    try:
                        exp_score = float(row.get("experimentally_determined_interaction", 0.0))
                    except (ValueError, TypeError):
                        exp_score = None

                    try:
                        db_score = float(row.get("database_annotated", 0.0))
                    except (ValueError, TypeError):
                        db_score = None

                    try:
                        text_score = float(row.get("automated_textmining", 0.0))
                    except (ValueError, TypeError):
                        text_score = None

                    try:
                        coex_score = float(row.get("coexpression", 0.0))
                    except (ValueError, TypeError):
                        coex_score = None

                    # Extract UniProt ID from STRING identifier if present (e.g. "3702.AT1G25550.1" or "3702.Q9LHG0")
                    partner_uniprot = partner_str_id.split(".", 1)[-1] if partner_str_id and "." in partner_str_id else partner_str_id

                    # Keep edge with highest combined score if duplicate exists
                    if partner not in direct_edges or combined > direct_edges[partner]["combined_score"]:
                        notes_parts = []
                        if row.get("neighborhood_on_chromosome"):
                            notes_parts.append(f"neighborhood={row.get('neighborhood_on_chromosome')}")
                        if row.get("gene_fusion"):
                            notes_parts.append(f"fusion={row.get('gene_fusion')}")
                        if row.get("phylogenetic_cooccurrence"):
                            notes_parts.append(f"cooccurrence={row.get('phylogenetic_cooccurrence')}")
                        if row.get("homology"):
                            notes_parts.append(f"homology={row.get('homology')}")
                        notes_str = "; ".join(notes_parts) if notes_parts else None

                        direct_edges[partner] = {
                            "partner_name": partner,
                            "partner_uniprot": partner_uniprot,
                            "combined_score": combined,
                            "experimental_score": exp_score,
                            "database_score": db_score,
                            "textmining_score": text_score,
                            "coexpression_score": coex_score,
                            "source_database": "STRING",
                            "source_file": tsv_rel_path,
                            "string_image_path": string_img,
                            "cytoscape_image_path": cyto_img,
                            "validation_status": "Verified",
                            "notes": notes_str
                        }

    return list(direct_edges.values())


def import_string_interactions(dry_run: bool = False, force: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Main ingestion function for STRING and FunCoup interaction datasets.
    """
    if not os.path.exists(STRING_ROOT):
        raise FileNotFoundError(f"STRING directory not found: {STRING_ROOT}")
    if not os.path.exists(CYTOSCAPE_ROOT):
        raise FileNotFoundError(f"Cytoscape directory not found: {CYTOSCAPE_ROOT}")

    db = SessionLocal()
    try:
        # Check existing records in protein_interactions
        existing_count = db.query(ProteinInteraction).count()
        if existing_count > 0:
            if not force:
                raise RuntimeError(
                    f"Database already contains {existing_count} protein interaction records. "
                    "Use --force to overwrite."
                )
            logger.info(f"Force flag detected: Deleting {existing_count} existing interaction records...")
            db.query(ProteinInteraction).delete()
            db.flush()

        # Verify all target TFs exist in database
        all_target_tf_ids = set()
        for tids in DIR_TO_TF_IDS.values():
            all_target_tf_ids.update(tids)

        existing_tfs = {tf.id: tf for tf in db.query(TranscriptionFactor).filter(TranscriptionFactor.id.in_(all_target_tf_ids)).all()}
        missing_tfs = all_target_tf_ids - set(existing_tfs.keys())
        if missing_tfs:
            raise ValueError(f"Target Transcription Factors not found in database: {missing_tfs}")

        total_packages = 0
        total_unique_edges = 0
        total_rows_to_insert = 0
        rows_by_tf: Dict[int, int] = {}
        inserted_instances: List[ProteinInteraction] = []

        sorted_dirs = sorted(os.listdir(STRING_ROOT))
        if len(sorted_dirs) != 45:
            raise ValueError(f"Expected 45 directories in {STRING_ROOT}, found {len(sorted_dirs)}")

        for d_name in sorted_dirs:
            if d_name not in DIR_TO_TF_IDS:
                raise ValueError(f"Unmapped STRING directory: {d_name}")

            edges = parse_package(d_name)
            target_tf_ids = DIR_TO_TF_IDS[d_name]
            total_packages += 1
            total_unique_edges += len(edges)

            for tf_id in target_tf_ids:
                for edge in edges:
                    obj = ProteinInteraction(
                        tf_id=tf_id,
                        partner_name=edge["partner_name"],
                        partner_uniprot=edge["partner_uniprot"],
                        combined_score=edge["combined_score"],
                        experimental_score=edge["experimental_score"],
                        database_score=edge["database_score"],
                        textmining_score=edge["textmining_score"],
                        coexpression_score=edge["coexpression_score"],
                        source_database=edge["source_database"],
                        source_file=edge["source_file"],
                        cytoscape_image_path=edge["cytoscape_image_path"],
                        string_image_path=edge["string_image_path"],
                        validation_status=edge["validation_status"],
                        notes=edge["notes"],
                    )
                    inserted_instances.append(obj)
                    total_rows_to_insert += 1
                    rows_by_tf[tf_id] = rows_by_tf.get(tf_id, 0) + 1

            if verbose:
                logger.info(f"Parsed {d_name:<18}: {len(edges)} unique edges -> {len(edges) * len(target_tf_ids)} DB rows across TF(s) {target_tf_ids}")

        logger.info("==================================================")
        logger.info(f"Packages parsed: {total_packages}/45")
        logger.info(f"Unique direct edges: {total_unique_edges}")
        logger.info(f"Total database rows to insert: {total_rows_to_insert}")
        logger.info(f"Target TFs linked: {len(rows_by_tf)}")
        logger.info("==================================================")

        if dry_run:
            logger.info("DRY RUN MODE: Validating object constraints without committing to database.")
            # Verify score bounds and non-null fields
            for item in inserted_instances:
                assert item.tf_id in existing_tfs, f"Invalid tf_id: {item.tf_id}"
                assert item.partner_name, f"Missing partner_name"
                assert 0.0 <= item.combined_score <= 1.0, f"Combined score out of bounds: {item.combined_score}"
                if item.experimental_score is not None:
                    assert 0.0 <= item.experimental_score <= 1.0
                if item.database_score is not None:
                    assert 0.0 <= item.database_score <= 1.0
                if item.textmining_score is not None:
                    assert 0.0 <= item.textmining_score <= 1.0
                if item.coexpression_score is not None:
                    assert 0.0 <= item.coexpression_score <= 1.0
                assert item.source_database in ("STRING", "FunCoup")
                assert item.validation_status == "Verified"

            db.rollback()
            logger.info("Dry run complete: All validations passed successfully. Session rolled back.")
            return {
                "dry_run": True,
                "total_packages": total_packages,
                "total_unique_edges": total_unique_edges,
                "total_rows": total_rows_to_insert,
                "target_tfs_count": len(rows_by_tf),
            }

        # Perform actual commit
        db.bulk_save_objects(inserted_instances)
        db.commit()
        logger.info(f"SUCCESS: Successfully committed {len(inserted_instances)} records to 'protein_interactions'.")

        # Verify post-commit count
        final_count = db.query(ProteinInteraction).count()
        logger.info(f"Verified database row count: {final_count}")

        return {
            "dry_run": False,
            "total_packages": total_packages,
            "total_unique_edges": total_unique_edges,
            "total_rows": final_count,
            "target_tfs_count": len(rows_by_tf),
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Ingestion failed with error: {e}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Import STRING and FunCoup interaction datasets into PhytoStress DB.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate ingestion without writing to database.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing records in protein_interactions table.")
    parser.add_argument("--verbose", action="store_true", help="Output verbose progress per package.")
    args = parser.parse_args()

    import_string_interactions(dry_run=args.dry_run, force=args.force, verbose=args.verbose)


if __name__ == "__main__":
    main()
