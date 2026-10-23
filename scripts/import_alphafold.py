#!/usr/bin/env python3
"""PhytoStress TF Atlas — AlphaFold Structure Ingestion Script.

Parses, validates, normalizes, stores, and links all 60 AlphaFold2 predicted 3D
coordinate models (12 prediction suites x 5 ranks) to their respective transcription
factor records in phytostress.db.

Authoritative reference documents:
- docs/data_mapping_report.md (Section 6)
- docs/data_quality_report.md (Section 2.J.1)
- docs/data_dictionary.md
- docs/alphafold_inventory.md
"""

import os
import sys
import re
import csv
import json
import argparse
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.database import SessionLocal, Base, engine
from backend.app.models.tf import TranscriptionFactor
from backend.app.models.sequence import ProteinSequence
from backend.app.models.structure import ProteinStructure


# Authoritative mapping specifications for the 12 AlphaFold suites
AF_SUITE_SPECS = {
    "AHL10_f311a": {
        "tf_id": 60,
        "tf_name": "AHL10",
        "accession": "O22812",
        "seq_file": "AHL10.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "AtC3H14_781a4": {
        "tf_id": 63,
        "tf_name": "AtC3H14",
        "accession": "Q9C9N3",
        "seq_file": "AtC3H14.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "AtC3H15_262f9": {
        "tf_id": 62,
        "tf_name": "AtC3H15",
        "accession": "Q9C9F5",
        "seq_file": "AtC3H15.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "AtDOF58_7e6b1": {
        "tf_id": 3,
        "tf_name": "AtDOF5.8",
        "accession": "Q9FGD6",
        "seq_file": "AtDOF5.8.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "AtPLATZ2_5dbaf": {
        "tf_id": 54,
        "tf_name": "AtPLATZ2",
        "accession": "AT1G76590",
        "seq_file": "AtPLATZ2.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "AtPLATZ4_e1c1e": {
        "tf_id": 55,
        "tf_name": "AtPLATZ4",
        "accession": "AT1G32700",
        "seq_file": "AtPLATZ4.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "BBX21_15acd": {
        "tf_id": 53,
        "tf_name": "BBX21",
        "accession": "Q9LQZ7",
        "seq_file": "BBX21.txt",
        "template_homolog": None,
        "notes": "Arabidopsis AtBBX21 homolog used for potato study",
    },
    "BnCDF1": {
        "tf_id": 9,
        "tf_name": "BnCDF1",
        "accession": "A0A816KYE7",
        "seq_file": "BnCDF1.txt",
        "template_homolog": "AtDOF5.8",
        "notes": "Predicted using homologous AtDOF5.8 template prefix; sequence is 100% BnCDF1",
    },
    "CDF3_8413b": {
        "tf_id": 5,
        "tf_name": "CDF3",
        "accession": "Q9LZP7",
        "seq_file": "CDF3.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "GhGT3b_A04_be592": {
        "tf_id": 49,
        "tf_name": "GhGT-3b_A04",
        "accession": "Gh_A04G0781",
        "seq_file": "GhGT-3b_A04.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "MdDOF54_cff3d": {
        "tf_id": 7,
        "tf_name": "MdDOF54",
        "accession": "A0A498K1B1",
        "seq_file": "MdDOF54.txt",
        "template_homolog": None,
        "notes": "ColabFold AlphaFold2-ptm prediction suite",
    },
    "MtNLP1_95155": {
        "tf_id": 31,
        "tf_name": "NLP1",
        "accession": "A0A977NVL6",
        "seq_file": "MtNLP1.txt",
        "template_homolog": None,
        "notes": "Modeled on 934 AA sequence of Nature Plants 2018 study (A0A977NVL6)",
    },
}


def validate_pdb_file(pdb_path: str) -> Dict[str, Any]:
    """Validates readability, format, ATOM records, and B-factors of a PDB file."""
    if not os.path.isfile(pdb_path):
        raise FileNotFoundError(f"PDB file not found: {pdb_path}")

    atom_count = 0
    residues = set()
    chains = set()
    b_factors = []

    with open(pdb_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("ATOM  ") or line.startswith("HETATM"):
                atom_count += 1
                chain_id = line[21].strip()
                res_seq = line[22:26].strip()
                res_name = line[17:20].strip()
                chains.add(chain_id)
                residues.add((chain_id, res_seq, res_name))
                try:
                    bf = float(line[60:66].strip())
                    b_factors.append(bf)
                except ValueError:
                    pass

    if atom_count == 0:
        raise ValueError(f"No ATOM or HETATM records found in PDB file: {pdb_path}")

    mean_b_factor = round(sum(b_factors) / len(b_factors), 2) if b_factors else None

    return {
        "atom_count": atom_count,
        "residue_count": len(residues),
        "chains": list(chains),
        "mean_b_factor": mean_b_factor,
    }


def ingest_alphafold_structures(
    db: Session,
    af_root: str,
    dry_run: bool = False,
    force: bool = False
) -> Dict[str, Any]:
    """Parses, validates, and ingests all 60 AlphaFold2 models into protein_structures."""
    if not os.path.isdir(af_root):
        raise FileNotFoundError(f"AlphaFold root directory not found: {af_root}")

    folders = sorted(os.listdir(af_root))
    if len(folders) != 12:
        raise ValueError(f"Expected 12 AlphaFold folders, found {len(folders)}")

    # Check existing count
    existing_count = db.query(ProteinStructure).count()
    if existing_count > 0:
        if force:
            print(f"[FORCE] Clearing {existing_count} existing structure records...")
            db.query(ProteinStructure).delete()
            db.flush()
        else:
            raise RuntimeError(
                f"protein_structures table already contains {existing_count} rows. "
                "Use --force to clear and re-ingest."
            )

    # Pre-load TFs and Sequences to verify foreign keys
    tfs = db.query(TranscriptionFactor).all()
    tf_ids = {tf.id for tf in tfs}
    tf_map = {tf.id: tf for tf in tfs}

    seqs = db.query(ProteinSequence).all()
    seq_map = {s.sequence: s for s in seqs}

    imported_models = []
    total_structures_created = 0
    total_pdbs_validated = 0

    print("=" * 80)
    print(f"STARTING ALPHAFOLD STRUCTURE INGESTION (dry_run={dry_run})")
    print(f"Source Directory: {af_root}")
    print(f"Total Model Suites: {len(folders)}")
    print("=" * 80)

    for suite_idx, folder in enumerate(folders, 1):
        if folder not in AF_SUITE_SPECS:
            raise ValueError(f"Unrecognized AlphaFold folder without mapping spec: {folder}")

        spec = AF_SUITE_SPECS[folder]
        fdir = os.path.join(af_root, folder)
        files = sorted(os.listdir(fdir))

        target_tf_id = spec["tf_id"]
        if target_tf_id not in tf_ids:
            raise ValueError(f"Foreign key failure: TF ID #{target_tf_id} not in database")

        target_tf = tf_map[target_tf_id]

        # Read query sequence from CSV
        csv_files = [f for f in files if f.endswith(".csv")]
        if not csv_files:
            raise ValueError(f"No CSV sequence file in {folder}")
        csv_path = os.path.join(fdir, csv_files[0])
        with open(csv_path, "r", encoding="utf-8") as cfp:
            r = list(csv.reader(cfp))
            query_seq = r[1][1].strip() if len(r) > 1 and len(r[1]) > 1 else ""

        if not query_seq:
            raise ValueError(f"Could not extract query sequence from {csv_path}")

        # Check sequence concordance with protein_sequences table
        if query_seq not in seq_map:
            raise ValueError(f"Query sequence for {folder} does not match any record in protein_sequences")

        matching_db_seq = seq_map[query_seq]
        print(f"\n[{suite_idx:02d}/12] Suite '{folder}' -> #{target_tf_id} ({target_tf.tf_name}) | Plant: {target_tf.plant.display_name[:20]}")
        print(f"       Concordant Sequence: {matching_db_seq.source_filename} ({len(query_seq)} AA)")

        # Locate diagnostic plot images (relative paths with forward slashes)
        pae_images = [f for f in files if f.endswith("_pae.png")]
        plddt_images = [f for f in files if f.endswith("_plddt.png")]
        cov_images = [f for f in files if f.endswith("_coverage.png")]

        pae_path = os.path.relpath(os.path.join(fdir, pae_images[0]), PROJECT_ROOT).replace("\\", "/") if pae_images else None
        plddt_path = os.path.relpath(os.path.join(fdir, plddt_images[0]), PROJECT_ROOT).replace("\\", "/") if plddt_images else None
        cov_path = os.path.relpath(os.path.join(fdir, cov_images[0]), PROJECT_ROOT).replace("\\", "/") if cov_images else None

        # Discover all 5 PDB rank models
        pdb_files = [f for f in files if f.endswith(".pdb")]
        if len(pdb_files) != 5:
            raise ValueError(f"Expected 5 PDB rank files in {folder}, found {len(pdb_files)}")

        # Sort PDB files by rank number (rank_001 to rank_005)
        def get_rank(fname):
            m = re.search(r'rank_0*(\d+)', fname)
            return int(m.group(1)) if m else 99

        pdb_files_sorted = sorted(pdb_files, key=get_rank)

        for rank_num, pdb_fname in enumerate(pdb_files_sorted, start=1):
            pdb_full_path = os.path.join(fdir, pdb_fname)
            pdb_rel_path = os.path.relpath(pdb_full_path, PROJECT_ROOT).replace("\\", "/")

            # Validate PDB format and coordinates
            pdb_val = validate_pdb_file(pdb_full_path)
            total_pdbs_validated += 1

            if pdb_val["residue_count"] != len(query_seq):
                raise ValueError(
                    f"Residue count mismatch in {pdb_fname}: "
                    f"PDB has {pdb_val['residue_count']}, query has {len(query_seq)}"
                )

            # Read matching scores JSON for exact mean pLDDT and pTM
            score_fname = pdb_fname.replace(".pdb", ".json").replace("unrelaxed_", "scores_")
            score_full_path = os.path.join(fdir, score_fname)

            mean_plddt = None
            ptm_val = None
            if os.path.isfile(score_full_path):
                with open(score_full_path, "r", encoding="utf-8") as scp:
                    sc_data = json.load(scp)
                    plddt_list = sc_data.get("plddt", [])
                    if plddt_list:
                        mean_plddt = round(sum(plddt_list) / len(plddt_list), 2)
                    ptm_val = sc_data.get("ptm")

            if mean_plddt is None:
                mean_plddt = pdb_val["mean_b_factor"]

            # Construct notes string
            notes_parts = [f"Rank {rank_num} model"]
            if ptm_val is not None:
                notes_parts.append(f"pTM={ptm_val:.2f}")
            if spec["notes"]:
                notes_parts.append(spec["notes"])
            notes_str = "; ".join(notes_parts)

            # Create ProteinStructure entity
            struct_record = ProteinStructure(
                tf_id=target_tf_id,
                model_identifier=folder,
                structure_type="AlphaFold2",
                rank_num=rank_num,
                pdb_file_path=pdb_rel_path,
                pae_image_path=pae_path,
                plddt_image_path=plddt_path,
                coverage_image_path=cov_path,
                mean_plddt=mean_plddt,
                template_homolog=spec["template_homolog"],
                validation_status="Computed",
                notes=notes_str,
                created_at=datetime.now(timezone.utc),
            )
            db.add(struct_record)
            total_structures_created += 1

            print(f"       Rank {rank_num}: {pdb_fname[:35]}... -> {pdb_val['atom_count']} atoms, mean pLDDT: {mean_plddt:.2f}")

            imported_models.append({
                "tf_id": target_tf_id,
                "tf_name": target_tf.tf_name,
                "suite": folder,
                "rank": rank_num,
                "pdb_file": pdb_rel_path,
                "atoms": pdb_val["atom_count"],
                "residues": pdb_val["residue_count"],
                "mean_plddt": mean_plddt,
                "template_homolog": spec["template_homolog"],
            })

    # Flush session to verify constraints
    db.flush()

    if dry_run:
        print("\n[DRY RUN] Ingestion simulation completed successfully. Rolling back transaction.")
        db.rollback()
    else:
        db.commit()
        print(f"\n[COMMITTED] Successfully committed {total_structures_created} structure records to phytostress.db.")

    return {
        "suites_processed": len(folders),
        "total_structures_created": total_structures_created,
        "total_pdbs_validated": total_pdbs_validated,
        "dry_run": dry_run,
        "models": imported_models,
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest AlphaFold structures into PhytoStress TF Atlas database.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate ingestion without committing to database.")
    parser.add_argument("--force", action="store_true", help="Clear existing structure records before ingestion.")
    parser.add_argument(
        "--af-dir",
        default=os.path.join(PROJECT_ROOT, "AlphaFold -20261008T053401Z-1-001", "AlphaFold"),
        help="Path to source AlphaFold directory."
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        summary = ingest_alphafold_structures(
            db=db,
            af_root=args.af_dir,
            dry_run=args.dry_run,
            force=args.force
        )
        print("\nAlphaFold Ingestion Summary:")
        print(f"  Model Suites Processed: {summary['suites_processed']}")
        print(f"  PDB Coordinate Files Validated: {summary['total_pdbs_validated']}")
        print(f"  Total Structure Records Created: {summary['total_structures_created']}")
        print(f"  Dry Run Mode: {summary['dry_run']}")
    except Exception as e:
        db.rollback()
        print(f"\nFATAL INGESTION ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
