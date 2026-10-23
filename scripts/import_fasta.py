#!/usr/bin/env python3
"""PhytoStress TF Atlas — FASTA Sequence Ingestion and Validation Script.

Safely parses, validates, normalizes, stores, and links all 41 curated FASTA files
to their respective transcription factor entities in phytostress.db.

Authoritative reference documents:
- docs/data_mapping_report.md (Section 6)
- docs/data_quality_report.md (Section 2.I)
- docs/data_dictionary.md
- docs/fasta_inventory.md
"""

import os
import sys
import re
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
from backend.app.models.identifier import TFIdentifier

# IUPAC 20 canonical amino acid residue average molecular weights in Daltons
AA_WEIGHTS = {
    'A': 71.0788,
    'R': 156.1875,
    'N': 114.1038,
    'D': 115.0886,
    'C': 103.1388,
    'E': 129.1155,
    'Q': 128.1307,
    'G': 57.0519,
    'H': 137.1411,
    'I': 113.1594,
    'L': 113.1594,
    'K': 128.1741,
    'M': 131.1926,
    'F': 147.1766,
    'P': 97.1167,
    'S': 87.0782,
    'T': 101.1051,
    'W': 186.2132,
    'Y': 163.1760,
    'V': 99.1326,
}
WATER_WEIGHT = 18.01524
CANONICAL_AA_SET = set(AA_WEIGHTS.keys())


def compute_molecular_weight(sequence: str) -> float:
    """Calculates average molecular weight of a protein sequence in Daltons."""
    seq_upper = sequence.upper()
    mw = sum(AA_WEIGHTS.get(aa, 110.0) for aa in seq_upper) + WATER_WEIGHT
    return round(mw, 2)


def extract_uniprot_accession(header: str) -> Optional[str]:
    """Extracts UniProt accession from FASTA header if present."""
    if not header:
        return None
    # Pattern 1: Standard UniProt pipe format: >sp|Q9FGD6|... or >tr|A0A816KYE7|...
    m = re.search(r'[\|]([A-Z0-9]{6,10})[\|]', header)
    if m:
        return m.group(1)
    # Pattern 2: Suffix or token accession: >AHL10_ARATH_O22812 or >BBX21_ARATH_Q9LQZ7
    words = re.findall(r'[A-Za-z0-9_.-]+', header)
    for w in words:
        subparts = re.split(r'[_|-]', w)
        for sp in subparts:
            if re.match(r'^[A-NR-Z][0-9][A-Z][A-Z0-9]{3}[0-9]$|^[OPQ][0-9][A-Z0-9]{3}[0-9]$', sp):
                return sp
    return None


def get_asset_mapping_specification() -> Dict[str, Dict[str, Any]]:
    """Returns authoritative mapping rules and metadata for all 41 FASTA files."""
    return {
        "AHL10.txt": {
            "target_tf_ids": [60],
            "accession": "O22812",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "AtC3H14.txt": {
            "target_tf_ids": [63],
            "accession": "Q9C9N3",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "AtC3H15.txt": {
            "target_tf_ids": [62],
            "accession": "Q9C9F5",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "AtDOF5.8.txt": {
            "target_tf_ids": [3],
            "accession": "Q9FGD6",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "AtPLATZ2.txt": {
            "target_tf_ids": [54],
            "accession": "AT1G76590",
            "rule": "Rule A (Filename stem; Anomaly 1)",
            "synthetic_header": ">AtPLATZ2_AT1G76590",
            "status": "Header generated",
            "provenance": "Stripped internal whitespace; generated synthetic FASTA header from locus AT1G76590",
        },
        "AtPLATZ4.txt": {
            "target_tf_ids": [55],
            "accession": "AT1G32700",
            "rule": "Rule A (Filename stem; Anomaly 2)",
            "synthetic_header": ">AtPLATZ4_AT1G32700",
            "status": "Header generated",
            "provenance": "Generated synthetic FASTA header from locus AT1G32700",
        },
        "BBX21.txt": {
            "target_tf_ids": [53],
            "accession": "Q9LQZ7",
            "rule": "Rule A (Filename stem homolog)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; Arabidopsis AtBBX21 homolog used for potato study",
        },
        "BnCDF1.txt": {
            "target_tf_ids": [9],
            "accession": "A0A816KYE7",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "CDF3.txt": {
            "target_tf_ids": [5],
            "accession": "Q9LZP7",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "GT2.txt": {
            "target_tf_ids": [48],
            "accession": "Q39117",
            "rule": "Rule A (Filename stem matches GT-2)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; Arabidopsis GT-2 homolog used for cotton study",
        },
        "GhGT-3b_A04.txt": {
            "target_tf_ids": [49],
            "accession": "Gh_A04G0781",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "GmNLP7a.txt": {
            "target_tf_ids": [40],
            "accession": "Glyma.09G137000",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "MdDOF54.txt": {
            "target_tf_ids": [7],
            "accession": "A0A498K1B1",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "MtNLP1.txt": {
            "target_tf_ids": [31],
            "accession": "A0A977NVL6",
            "rule": "Rule B (UniProt accession) / Rule D (Disambiguation)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; disambiguated via UniProt A0A977NVL6 (Nature Plants 2018)",
        },
        "MtNLP1 (2).txt": {
            "target_tf_ids": [32],
            "accession": "A0A072V3U8",
            "rule": "Rule B (UniProt accession) / Rule D (Disambiguation)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; disambiguated via UniProt A0A072V3U8 (Plant Comms 2021)",
        },
        "NLP1.txt": {
            "target_tf_ids": [28],
            "accession": "Q10S83",
            "rule": "Rule B (UniProt accession)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; rice NLP1 subunit of NLP family (Record #28)",
        },
        "NLP2.txt": {
            "target_tf_ids": [28, 37],
            "accession": "Q0JC27",
            "rule": "Rule A (Stem NLP2) / Rule B (UniProt Q0JC27)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent of Record #28 (Rice NLP family) and primary gene of Record #37 (NLP2)",
        },
        "NLP3.txt": {
            "target_tf_ids": [28],
            "accession": "Q5NB82",
            "rule": "Rule B (UniProt accession)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; rice NLP3 subunit of NLP family (Record #28)",
        },
        "NLP4.txt": {
            "target_tf_ids": [38],
            "accession": "Q9AS33",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "NLP7.txt": {
            "target_tf_ids": [29, 30, 34, 35],
            "accession": "Q84TH9",
            "rule": "Rule A (Stem NLP7) / Rule B (UniProt Q84TH9)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; shared sequence across Arabidopsis NLP7/NLP family studies (#29, #30, #34, #35)",
        },
        "NLP8.txt": {
            "target_tf_ids": [39],
            "accession": "O22864",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "OsC3H47.txt": {
            "target_tf_ids": [61],
            "accession": "Q8GW05",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "OsDOF1.txt": {
            "target_tf_ids": [12],
            "accession": "Q9FE00",
            "rule": "Rule A (Filename stem; Anomaly 3)",
            "synthetic_header": ">OsDOF1_Q9FE00",
            "status": "Header generated",
            "provenance": "Generated synthetic FASTA header from accession Q9FE00",
        },
        "OsDOF15.txt": {
            "target_tf_ids": [14],
            "accession": "B7E8H7",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "OsDOF18.txt": {
            "target_tf_ids": [15],
            "accession": "Q7FAN8",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "OsMADS25.txt": {
            "target_tf_ids": [21, 22],
            "accession": "Q84NC5",
            "rule": "Rule A (Stem OsMADS25) / Rule B (UniProt Q84NC5)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; shared sequence across rice OsMADS25 studies (#21, #22)",
        },
        "OsMADS3.txt": {
            "target_tf_ids": [20],
            "accession": "Q40704",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "OsZFP213.txt": {
            "target_tf_ids": [50],
            "accession": "Q2QM53",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "SlBZR1.txt": {
            "target_tf_ids": [59],
            "accession": "Solyc04g079980",
            "rule": "Rule C (Composite constituent: SlBZR1 of SlBZR1 / SlBZR1D)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent locus Solyc04g079980",
        },
        "SlCDF1.txt": {
            "target_tf_ids": [6],
            "accession": "A0A3Q7F8Y3",
            "rule": "Rule C (Composite constituent: SlCDF1 of SlCDF1 / SlCDF3)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent locus Solyc02g087980",
        },
        "SlCDF3.txt": {
            "target_tf_ids": [6],
            "accession": "A0A3Q7H2S9",
            "rule": "Rule C (Composite constituent: SlCDF3 of SlCDF1 / SlCDF3)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent locus Solyc06g074350",
        },
        "SlGATA17.txt": {
            "target_tf_ids": [52],
            "accession": "Solyc05g056120",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "SlMBP11.txt": {
            "target_tf_ids": [16],
            "accession": "A0A3Q7F370",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "SlMBP8.txt": {
            "target_tf_ids": [17],
            "accession": "A0A3Q7JXP0",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "SlNLP1.txt": {
            "target_tf_ids": [33],
            "accession": "A0A3Q7HL32",
            "rule": "Rule C (Composite constituent: SlNLP1 of NLP1 / NLP5)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent locus SlNLP1",
        },
        "SlNLP5.txt": {
            "target_tf_ids": [33],
            "accession": "A0A3Q7HUP0",
            "rule": "Rule C (Composite constituent: SlNLP5 of NLP1 / NLP5)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent locus SlNLP5",
        },
        "TDR6.txt": {
            "target_tf_ids": [23],
            "accession": "A0A3Q7F788",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "TaMADS51.txt": {
            "target_tf_ids": [19],
            "accession": "O82130",
            "rule": "Rule A (Filename stem)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file",
        },
        "TaZNF.fasta.txt": {
            "target_tf_ids": [2],
            "accession": "A0A1D5V0E4",
            "rule": "Rule A (Double extension .fasta.txt stripped)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; stripped compound extension .fasta.txt",
        },
        "VOZ1.txt": {
            "target_tf_ids": [44],
            "accession": "Q9SGQ0",
            "rule": "Rule C (Composite constituent: VOZ1 of VOZ1 / VOZ2)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent locus AT1G28520",
        },
        "VOZ2.txt": {
            "target_tf_ids": [44],
            "accession": "Q9SLB9",
            "rule": "Rule C (Composite constituent: VOZ2 of VOZ1 / VOZ2)",
            "status": "Verified",
            "provenance": "Parsed directly from source FASTA file; constituent locus AT2G42400",
        },
    }


def ingest_fasta_sequences(
    db: Session,
    fasta_dir: str,
    dry_run: bool = False,
    force: bool = False
) -> Dict[str, Any]:
    """Parses and ingests all 41 FASTA sequences into the database."""
    if not os.path.isdir(fasta_dir):
        raise FileNotFoundError(f"FASTA directory not found: {fasta_dir}")

    files = sorted(os.listdir(fasta_dir))
    if len(files) != 41:
        raise ValueError(f"Expected 41 FASTA files in '{fasta_dir}', but found {len(files)}")

    # Check if protein_sequences table is already populated
    existing_count = db.query(ProteinSequence).count()
    if existing_count > 0:
        if force:
            print(f"[FORCE] Removing {existing_count} existing sequence records from database...")
            db.query(ProteinSequence).delete()
            db.flush()
        else:
            raise RuntimeError(
                f"protein_sequences table already contains {existing_count} rows. "
                "Use --force to clear and re-ingest."
            )

    # Pre-load all transcription factors to verify foreign keys
    tfs = db.query(TranscriptionFactor).all()
    tf_ids_in_db = {tf.id for tf in tfs}
    tf_map = {tf.id: tf for tf in tfs}

    specs = get_asset_mapping_specification()

    # Track audit metrics
    imported_records = []
    total_associations = 0
    total_aa_residues = 0
    header_generated_count = 0

    print("=" * 80)
    print(f"STARTING FASTA SEQUENCE INGESTION (dry_run={dry_run})")
    print(f"Source Directory: {fasta_dir}")
    print(f"Total Physical Files: {len(files)}")
    print("=" * 80)

    for idx, fname in enumerate(files, 1):
        if fname not in specs:
            raise ValueError(f"Unrecognized FASTA file without mapping rule: {fname}")

        spec = specs[fname]
        filepath = os.path.join(fasta_dir, fname)

        # Read binary for exact byte safety & hash verification
        with open(filepath, "rb") as fp:
            raw_bytes = fp.read()

        file_sha256 = hashlib.sha256(raw_bytes).hexdigest()

        # Decode content
        text_content = raw_bytes.decode("utf-8", errors="replace")
        lines = text_content.splitlines()

        first_line = lines[0].strip() if lines else ""
        has_header = first_line.startswith(">")

        if has_header:
            fasta_header = first_line
            seq_lines = lines[1:]
        else:
            fasta_header = spec.get("synthetic_header")
            if not fasta_header:
                raise ValueError(f"File '{fname}' lacks header but no synthetic header configured")
            seq_lines = lines
            header_generated_count += 1

        # Concatenate and normalize sequence
        raw_seq = "".join(seq_lines)
        # Strip all whitespace (including internal spaces, e.g. AtPLATZ2.txt)
        clean_seq = "".join(raw_seq.split()).upper()

        if len(clean_seq) == 0:
            raise ValueError(f"Empty sequence encountered in '{fname}'")

        # Validate canonical amino acid alphabet
        seq_chars = set(clean_seq)
        invalid_chars = seq_chars - CANONICAL_AA_SET
        if invalid_chars:
            raise ValueError(f"Invalid amino acid characters {invalid_chars} in '{fname}'")

        seq_len = len(clean_seq)
        mw_da = compute_molecular_weight(clean_seq)
        total_aa_residues += seq_len

        # Extract or confirm accession
        accession = spec.get("accession")
        if not accession and has_header:
            accession = extract_uniprot_accession(fasta_header)

        # Validate foreign keys
        target_tf_ids = spec["target_tf_ids"]
        for tid in target_tf_ids:
            if tid not in tf_ids_in_db:
                raise ValueError(f"Foreign key violation: TF ID #{tid} does not exist in database")

        # Create ProteinSequence records for each linked TF
        for tid in target_tf_ids:
            seq_record = ProteinSequence(
                tf_id=tid,
                accession=accession,
                fasta_header=fasta_header,
                sequence=clean_seq,
                sequence_length=seq_len,
                molecular_weight=mw_da,
                source_filename=fname,
                validation_status=spec["status"],
                provenance=spec["provenance"],
                created_at=datetime.now(timezone.utc),
            )
            db.add(seq_record)
            total_associations += 1

        tf_names_preview = ", ".join([f"#{tid} ({tf_map[tid].tf_name})" for tid in target_tf_ids])
        print(f"[{idx:02d}/41] Ingested '{fname}' -> {seq_len} AA, {mw_da:,.1f} Da -> {tf_names_preview}")

        imported_records.append({
            "filename": fname,
            "sha256": file_sha256,
            "length": seq_len,
            "molecular_weight": mw_da,
            "target_ids": target_tf_ids,
            "status": spec["status"],
            "accession": accession,
        })

    # Flush session to check all constraints
    db.flush()

    if dry_run:
        print("\n[DRY RUN] Ingestion simulation completed successfully. Rolling back transaction.")
        db.rollback()
    else:
        db.commit()
        print(f"\n[COMMITTED] Successfully committed {total_associations} sequence records to phytostress.db.")

    summary = {
        "total_files_parsed": len(files),
        "total_associations_created": total_associations,
        "total_aa_residues": total_aa_residues,
        "header_generated_count": header_generated_count,
        "dry_run": dry_run,
        "records": imported_records,
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Ingest FASTA sequences into PhytoStress TF Atlas database.")
    parser.add_argument("--dry-run", action="store_true", help="Simulate ingestion without committing to database.")
    parser.add_argument("--force", action="store_true", help="Remove existing sequence records before ingestion.")
    parser.add_argument(
        "--fasta-dir",
        default=os.path.join(PROJECT_ROOT, "FASTA sequence of TFs-20261008T053415Z-1-001", "FASTA sequence of TFs"),
        help="Path to source FASTA directory."
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        summary = ingest_fasta_sequences(
            db=db,
            fasta_dir=args.fasta_dir,
            dry_run=args.dry_run,
            force=args.force
        )
        print("\nIngestion Summary:")
        print(f"  Physical files processed: {summary['total_files_parsed']}")
        print(f"  Total sequence records created: {summary['total_associations_created']}")
        print(f"  Total amino acid residues: {summary['total_aa_residues']:,}")
        print(f"  Synthetic headers generated: {summary['header_generated_count']}")
        print(f"  Dry run mode: {summary['dry_run']}")
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
