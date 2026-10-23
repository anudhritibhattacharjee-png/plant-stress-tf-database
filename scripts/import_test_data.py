#!/usr/bin/env python3
"""PhytoStress TF Atlas — Controlled Test Data Importer.

Imports exactly 5 curated representative records from `data/test/test_records.json`
into the normalized SQLite/PostgreSQL relational database.

Authoritative mapping reference:
- docs/data_mapping_report.md
- docs/data_quality_report.md
- docs/data_dictionary.md
- docs/test_import_selection.md
"""

import os
import sys
import json
import re
import hashlib
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone

# Ensure workspace root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.app.database import SessionLocal, engine
from backend.app.models import (
    Base,
    TFFamily,
    Plant,
    TranscriptionFactor,
    StressCondition,
    TFStressAssociation,
    TFIdentifier,
    ResearchPaper,
    TFPaperAssociation,
    TargetGene,
    TFTargetAssociation,
    Pathway,
    TFPathwayAssociation,
    ImportAudit,
)


def compute_sha256(filepath: str) -> str:
    """Computes the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def clean_string(val: Optional[str]) -> Optional[str]:
    """Strips leading/trailing whitespace and normalizes empty strings to None."""
    if val is None:
        return None
    val = str(val).strip()
    return val if val else None


def clean_title(title_raw: Optional[str]) -> str:
    """Strips enclosing quotes (single, double, smart quotes) and whitespace."""
    if not title_raw:
        return ""
    t = str(title_raw).strip()
    # Strip leading/trailing double or smart quotes
    t = re.sub(r'^[“"\'\s]+|[”"\'\s]+$', '', t)
    return t.strip()


def extract_clean_doi(doi_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Extracts clean DOI identifier and canonical HTTP URL.
    
    Returns:
        (clean_doi, doi_url)
    """
    if not doi_str:
        return None, None
    raw = str(doi_str).strip()
    clean = raw
    for prefix in ["https://doi.org/", "http://doi.org/", "https://link.springer.com/"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break
    # Normalize clean DOI
    clean = clean.strip()
    url = raw if raw.startswith("http") else f"https://doi.org/{clean}"
    return clean, url


def get_or_create_family(session: Session, raw_family: str) -> TFFamily:
    """Retrieves or creates a normalized TFFamily."""
    fam_name = clean_string(raw_family) or "Unknown"
    fam = session.query(TFFamily).filter(TFFamily.name == fam_name).first()
    if not fam:
        fam = TFFamily(name=fam_name)
        session.add(fam)
        session.flush()
    return fam


def get_or_create_plant(session: Session, raw_plant: str) -> Plant:
    """Retrieves or creates a normalized Plant entity.
    
    Preserves display_name verbatim while parsing common name and Latin binomial.
    """
    display = clean_string(raw_plant) or "Unknown"
    plant = session.query(Plant).filter(Plant.display_name == display).first()
    if plant:
        return plant

    common = display
    scientific = None
    tax_id = None

    # Parse parenthetical scientific binomial or comments
    # e.g., "Tomato (Solanum lycopersicum)"
    m = re.match(r"^([^(]+)(?:\(([^;)]+)(?:;\s*([^)]+))?\))?$", display)
    if m:
        common = m.group(1).strip()
        if m.group(2):
            scientific = m.group(2).strip()

    # Known common-to-scientific mapping fallbacks if unstated
    known_taxonomy = {
        "Tomato": ("Solanum lycopersicum", 4081),
        "Arabidopsis": ("Arabidopsis thaliana", 3702),
        "Rice": ("Oryza sativa", 4530),
        "Apple": ("Malus domestica", 3750),
        "Wheat": ("Triticum aestivum", 4565),
    }

    if common in known_taxonomy:
        if not scientific:
            scientific = known_taxonomy[common][0]
        if not tax_id:
            tax_id = known_taxonomy[common][1]

    plant = Plant(
        display_name=display,
        common_name=common,
        scientific_name=scientific,
        ncbi_taxonomy_id=tax_id
    )
    session.add(plant)
    session.flush()
    return plant


def get_or_create_paper(session: Session, record: Dict[str, Any]) -> ResearchPaper:
    """Retrieves or creates a ResearchPaper record with deduplication."""
    title = clean_title(record.get("Research paper "))
    journal = clean_string(record.get("Journal"))
    if journal in ["___", "—", "-"]:
        journal = None
    
    year_val = record.get("Year")
    year = int(float(year_val)) if year_val is not None else None
    
    doi, doi_url = extract_clean_doi(record.get("DOI Number"))

    query = session.query(ResearchPaper)
    if doi:
        paper = query.filter(ResearchPaper.doi == doi).first()
    else:
        paper = query.filter(ResearchPaper.title == title).first()

    if not paper:
        paper = ResearchPaper(
            title=title,
            journal=journal,
            year=year,
            doi=doi,
            doi_url=doi_url
        )
        session.add(paper)
        session.flush()
    return paper


def parse_stresses_for_record(raw_stress: str) -> List[Tuple[str, str]]:
    """Splits composite stress text into normalized individual condition names and categories.
    
    Returns list of (stress_name, stress_type).
    """
    normalized_list = []
    # Specific biological mappings for controlled test records
    clean = clean_string(raw_stress) or ""
    
    if "Drought, cold, osmotic stress" in clean:
        normalized_list = [
            ("Drought", "Abiotic"),
            ("Cold", "Abiotic"),
            ("Osmotic stress", "Abiotic")
        ]
    elif "Salt, drought" in clean:
        normalized_list = [
            ("Salt stress", "Abiotic"),
            ("Drought", "Abiotic")
        ]
    elif "Nitrogen/nitrate availability" in clean:
        normalized_list = [
            ("Nitrate availability", "Nutrient"),
            ("Nitrogen limitation", "Nutrient")
        ]
    elif clean in ["Salt stress", "Salt"]:
        normalized_list = [("Salt stress", "Abiotic")]
    elif clean in ["Drought", "Drought stress"]:
        normalized_list = [("Drought", "Abiotic")]
    else:
        # Fallback general split on commas and 'and'
        parts = re.split(r",\s*|\s+and\s+", clean)
        for p in parts:
            p_clean = p.strip()
            if p_clean:
                normalized_list.append((p_clean, "Abiotic"))
                
    return normalized_list


def link_stresses(session: Session, tf: TranscriptionFactor, raw_stress: str) -> List[StressCondition]:
    """Links normalized stress conditions to TF via junction table."""
    stress_defs = parse_stresses_for_record(raw_stress)
    linked_stresses = []
    
    for s_name, s_type in stress_defs:
        cond = session.query(StressCondition).filter(StressCondition.stress_name == s_name).first()
        if not cond:
            cond = StressCondition(stress_name=s_name, stress_type=s_type)
            session.add(cond)
            session.flush()
        
        # Check junction
        existing_assoc = session.query(TFStressAssociation).filter(
            TFStressAssociation.tf_id == tf.id,
            TFStressAssociation.stress_id == cond.id
        ).first()
        if not existing_assoc:
            assoc = TFStressAssociation(
                tf_id=tf.id,
                stress_id=cond.id,
                specific_effect=tf.regulatory_effect
            )
            session.add(assoc)
        linked_stresses.append(cond)
        
    session.flush()
    return linked_stresses


def parse_and_link_identifiers(session: Session, tf: TranscriptionFactor, record: Dict[str, Any]) -> List[TFIdentifier]:
    """Parses and stores all external accessions/identifiers without data loss or fabrication.
    
    Follows docs/data_mapping_report.md Section 3 & 4.
    """
    raw_id_text = clean_string(record.get("Uniprot Accession ID/Valid Gene ID")) or ""
    id_type = clean_string(record.get("Identifier Type")) or ""
    created_identifiers = []

    # Case E: Explicitly "Not verified"
    if "Not verified" in raw_id_text:
        tf.is_verified = False
        tf.notes = "Accession explicitly flagged as 'Not verified' in literature source."
        
        # Parse auxiliary NCBI Gene ID if present in id_type
        # e.g., "NCBI Gene 101255410 (SlDof22); paper gene symbol"
        ncbi_match = re.search(r"NCBI\s+Gene\s+(\d+)", id_type, re.IGNORECASE)
        if ncbi_match:
            ncbi_id = ncbi_match.group(1)
            ident_ncbi = TFIdentifier(
                tf_id=tf.id,
                identifier_type="NCBI Gene",
                identifier_value=ncbi_id,
                verification_status="Not verified",
                raw_supplied_text=raw_id_text,
                is_primary=False
            )
            session.add(ident_ncbi)
            created_identifiers.append(ident_ncbi)
            
        # Parse gene symbol
        sym_match = re.search(r"\((\w+)\)", id_type)
        if sym_match:
            sym = sym_match.group(1)
            ident_sym = TFIdentifier(
                tf_id=tf.id,
                identifier_type="Gene symbol",
                identifier_value=sym,
                verification_status="Not verified",
                raw_supplied_text=raw_id_text,
                is_primary=False
            )
            session.add(ident_sym)
            created_identifiers.append(ident_sym)
            
        session.flush()
        return created_identifiers

    # Official UniProt accession regex (covers 6-char [OPQ] and 6/10-char [A-NR-Z] accessions)
    uniprot_pattern = r"\b([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})\b"
    uniprots = re.findall(uniprot_pattern, raw_id_text)
    
    if len(uniprots) > 1:
        # Determine primary accession (e.g. Q84NC5 as documented in data_quality_report.md)
        primary_candidate = "Q84NC5" if "Q84NC5" in uniprots else uniprots[0]
        for acc in uniprots:
            ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="UniProtKB",
                identifier_value=acc,
                verification_status="Verified",
                raw_supplied_text=raw_id_text,
                is_primary=(acc == primary_candidate)
            )
            session.add(ident)
            created_identifiers.append(ident)
        session.flush()
        return created_identifiers

    # Case D: Gene models (e.g. "Solyc02g087980 and Solyc06g074350...")
    solyc_matches = re.findall(r"Solyc\d{2}g\d{6}", raw_id_text)
    if solyc_matches:
        for idx, solyc in enumerate(solyc_matches):
            ident = TFIdentifier(
                tf_id=tf.id,
                identifier_type="Sol Genomics Network",
                identifier_value=solyc,
                verification_status="Verified",
                raw_supplied_text=raw_id_text,
                is_primary=(idx == 0)
            )
            session.add(ident)
            created_identifiers.append(ident)
        session.flush()
        return created_identifiers

    # Case A & B: Single standard UniProt accession (e.g. "A0A498K1B1", "Q9LZP7")
    if len(uniprots) == 1:
        acc = uniprots[0]
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="UniProtKB",
            identifier_value=acc,
            verification_status="Verified",
            raw_supplied_text=raw_id_text,
            is_primary=True
        )
        session.add(ident)
        created_identifiers.append(ident)
        session.flush()
        return created_identifiers


    # Fallback if other raw identifier string
    if raw_id_text:
        ident = TFIdentifier(
            tf_id=tf.id,
            identifier_type="Curated Identifier",
            identifier_value=raw_id_text,
            verification_status="Verified",
            raw_supplied_text=raw_id_text,
            is_primary=True
        )
        session.add(ident)
        created_identifiers.append(ident)
        session.flush()

    return created_identifiers


def parse_and_link_targets_and_pathways(session: Session, tf: TranscriptionFactor, plant: Plant, raw_targets: str):
    """Parses downstream target genes and physiological pathways according to data dictionary."""
    clean = clean_string(raw_targets) or ""
    if not clean:
        return

    # Specific deterministic parsing for representative test records
    targets_to_add = []
    pathways_to_add = []

    if "MdAPX3" in clean:  # Record 1: MdDOF54
        targets_to_add = ["MdAPX3", "MdACO1", "MdTGD2", "MdAPL3"]
        pathways_to_add = ["Hydraulic water transport", "Photosynthetic drought response"]
    elif "CBF/DREB2A" in clean:  # Record 2: CDF3
        targets_to_add = ["CBF", "DREB2A", "ZAT10", "ZAT12"]
        pathways_to_add = ["Osmoprotection", "Oxidative-stress metabolism"]
    elif "Nitrate accumulation" in clean:  # Record 3: OsMADS25
        pathways_to_add = ["Nitrate accumulation", "Nitrate-dependent root development"]
    elif "Flowering-time network" in clean:  # Record 4: SlCDF1 / SlCDF3
        pathways_to_add = ["Flowering-time network", "Abiotic-stress response"]
    elif "SlSOS1" in clean:  # Record 5: SlDOF22
        targets_to_add = ["SlSOS1"]
        pathways_to_add = ["Ascorbate recycling", "SOS-mediated Na+ homeostasis"]

    # Link targets
    for gene_sym in targets_to_add:
        target = session.query(TargetGene).filter(
            TargetGene.gene_symbol == gene_sym,
            TargetGene.plant_id == plant.id
        ).first()
        if not target:
            target = TargetGene(gene_symbol=gene_sym, plant_id=plant.id)
            session.add(target)
            session.flush()
        
        # Link junction
        existing_assoc = session.query(TFTargetAssociation).filter(
            TFTargetAssociation.tf_id == tf.id,
            TFTargetAssociation.target_gene_id == target.id
        ).first()
        if not existing_assoc:
            session.add(TFTargetAssociation(
                tf_id=tf.id,
                target_gene_id=target.id,
                regulation_mode="Reported downstream target"
            ))

    # Link pathways
    for p_name in pathways_to_add:
        pathway = session.query(Pathway).filter(Pathway.pathway_name == p_name).first()
        if not pathway:
            pathway = Pathway(pathway_name=p_name)
            session.add(pathway)
            session.flush()
        
        existing_assoc = session.query(TFPathwayAssociation).filter(
            TFPathwayAssociation.tf_id == tf.id,
            TFPathwayAssociation.pathway_id == pathway.id
        ).first()
        if not existing_assoc:
            session.add(TFPathwayAssociation(
                tf_id=tf.id,
                pathway_id=pathway.id
            ))

    session.flush()


def run_test_import(
    json_path: str = "data/test/test_records.json",
    session: Optional[Session] = None,
    dry_run: bool = False,
    force: bool = False
) -> Dict[str, Any]:
    """Orchestrates the 5-record test import into the database.
    
    Returns a dictionary of execution results and statistics.
    """
    should_close_session = False
    if session is None:
        session = SessionLocal()
        should_close_session = True

    try:
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Test records file not found at: {json_path}")

        file_hash = compute_sha256(json_path)
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        if len(records) != 5:
            raise ValueError(f"Expected exactly 5 test records, got {len(records)}")

        # Deterministic Duplicate-Safety Check:
        # Check whether any of the test records are already present in the database.
        # We match on (tf_name, research_paper.doi).
        existing_tf_count = 0
        for rec in records:
            tf_name = clean_string(rec.get("TF / TF family"))
            doi, _ = extract_clean_doi(rec.get("DOI Number"))
            if doi:
                existing = session.query(TranscriptionFactor).join(
                    TFPaperAssociation, TranscriptionFactor.id == TFPaperAssociation.tf_id
                ).join(
                    ResearchPaper, TFPaperAssociation.paper_id == ResearchPaper.id
                ).filter(
                    TranscriptionFactor.tf_name == tf_name,
                    ResearchPaper.doi == doi
                ).first()
                if existing:
                    existing_tf_count += 1

        if existing_tf_count == len(records) and not force:
            print(f"[DUPLICATE-SAFETY] All {len(records)} test records are already present in the database.")
            print("[DUPLICATE-SAFETY] Skipping re-import to guarantee idempotent duplicate-safety.")
            return {
                "status": "SKIPPED_EXISTING",
                "message": "All 5 records already exist in database. Import skipped safely.",
                "records_processed": len(records),
                "records_inserted": 0,
                "file_hash": file_hash
            }

        # Begin transaction
        stats = {
            "records_processed": 0,
            "records_inserted": 0,
            "plants_created": 0,
            "families_created": 0,
            "papers_created": 0,
            "stresses_created": 0,
            "stress_associations": 0,
            "identifiers_created": 0,
            "targets_created": 0,
            "pathways_created": 0,
            "imported_tfs": []
        }

        # Source row index lookup for provenance
        provenance_map = {
            "MdDOF54": (8, "Excel Row 8 / Prototype Record #7"),
            "CDF3": (6, "Excel Row 6 / Prototype Record #5"),
            "OsMADS25": (22, "Excel Row 22 / Prototype Record #21"),
            "SlCDF1 / SlCDF3": (7, "Excel Row 7 / Prototype Record #6"),
            "SlDOF22": (2, "Excel Row 2 / Prototype Record #1"),
        }

        for idx, rec in enumerate(records, start=1):
            stats["records_processed"] += 1
            raw_tf_name = clean_string(rec.get("TF / TF family"))
            raw_stress = clean_string(rec.get("Stress condition"))
            raw_targets = clean_string(rec.get("Key Target(s) / Pathway"))
            
            # Resolve Family & Plant
            family = get_or_create_family(session, rec.get("Standardized TF Family"))
            plant = get_or_create_plant(session, rec.get("Plant"))
            
            # Provenance
            source_row, source_desc = provenance_map.get(raw_tf_name, (idx, "Test Record"))
            
            # Create TF entity (Preserves exact raw values)
            tf = TranscriptionFactor(
                tf_name=raw_tf_name,
                family_id=family.id,
                plant_id=plant.id,
                regulatory_effect=clean_string(rec.get("Regulatory Effect")),
                mechanism_description=clean_string(rec.get("How it regulates stress")),
                validation_system=clean_string(rec.get("Validation System")),
                evidence_summary=clean_string(rec.get("Evidence Type")),
                raw_supplied_tf=raw_tf_name,
                raw_stress=raw_stress,
                raw_targets=raw_targets,
                source_dataset="test_records_json",
                source_row_index=source_row,
                is_verified=True,  # Default, adjusted in parse_and_link_identifiers if unverified
                notes=None
            )
            session.add(tf)
            session.flush()
            stats["records_inserted"] += 1

            # Paper & Paper Association
            paper = get_or_create_paper(session, rec)
            paper_assoc = session.query(TFPaperAssociation).filter(
                TFPaperAssociation.tf_id == tf.id,
                TFPaperAssociation.paper_id == paper.id
            ).first()
            if not paper_assoc:
                session.add(TFPaperAssociation(
                    tf_id=tf.id,
                    paper_id=paper.id,
                    evidence_notes=clean_string(rec.get("Evidence Type"))
                ))
                session.flush()

            # Stresses & Junctions
            linked_stresses = link_stresses(session, tf, raw_stress)
            stats["stress_associations"] += len(linked_stresses)

            # Identifiers
            created_ids = parse_and_link_identifiers(session, tf, rec)
            stats["identifiers_created"] += len(created_ids)

            # Targets & Pathways
            parse_and_link_targets_and_pathways(session, tf, plant, raw_targets)

            stats["imported_tfs"].append({
                "id": tf.id,
                "tf_name": tf.tf_name,
                "plant": plant.common_name,
                "family": family.name,
                "is_verified": tf.is_verified,
                "stresses": [s.stress_name for s in linked_stresses],
                "identifiers": [(i.identifier_type, i.identifier_value, i.verification_status) for i in created_ids]
            })

        # Collect exact database entity counts
        stats["tfs_count"] = session.query(TranscriptionFactor).count()
        stats["plants_count"] = session.query(Plant).count()
        stats["families_count"] = session.query(TFFamily).count()
        stats["papers_count"] = session.query(ResearchPaper).count()
        stats["paper_associations_count"] = session.query(TFPaperAssociation).count()
        stats["stresses_count"] = session.query(StressCondition).count()
        stats["stress_associations_count"] = session.query(TFStressAssociation).count()
        stats["identifiers_count"] = session.query(TFIdentifier).count()
        stats["targets_count"] = session.query(TargetGene).count()
        stats["target_associations_count"] = session.query(TFTargetAssociation).count()
        stats["pathways_count"] = session.query(Pathway).count()
        stats["pathway_associations_count"] = session.query(TFPathwayAssociation).count()

        # Create ImportAudit record
        audit = ImportAudit(
            source_name=json_path,
            source_type="JSON",
            source_hash=file_hash,
            records_processed=stats["records_processed"],
            records_inserted=stats["records_inserted"],
            records_updated=0,
            status="SUCCESS",
            validation_summary=json.dumps({
                "imported_count": stats["records_inserted"],
                "tfs": [t["tf_name"] for t in stats["imported_tfs"]],
                "duplicate_safety": "deterministic_checked",
                "table_counts": {
                    "transcription_factors": stats["tfs_count"],
                    "plants": stats["plants_count"],
                    "tf_families": stats["families_count"],
                    "research_papers": stats["papers_count"],
                    "stress_conditions": stats["stresses_count"],
                    "tf_identifiers": stats["identifiers_count"],
                    "target_genes": stats["targets_count"],
                    "pathways": stats["pathways_count"]
                }
            }),
            error_information=None
        )
        session.add(audit)
        session.flush()
        stats["audits_count"] = session.query(ImportAudit).count()


        if dry_run:
            print("[DRY-RUN] Rolling back transaction without committing changes.")
            session.rollback()
            stats["status"] = "DRY_RUN_SUCCESS"
        else:
            session.commit()
            stats["status"] = "SUCCESS"
            print(f"[SUCCESS] Successfully committed {stats['records_inserted']} TF records and associated entities.")

        return stats

    except Exception as e:
        session.rollback()
        print(f"[ERROR] Import failed with error: {e}. Transaction rolled back.")
        # Attempt to log failed audit if possible in new session
        try:
            audit_fail = ImportAudit(
                source_name=json_path,
                source_type="JSON",
                records_processed=0,
                records_inserted=0,
                records_updated=0,
                status="FAILED",
                error_information=str(e)
            )
            session.add(audit_fail)
            session.commit()
        except Exception:
            pass
        raise e
    finally:
        if should_close_session:
            session.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PhytoStress TF Atlas Test Data Importer")
    parser.add_argument("--json", default="data/test/test_records.json", help="Path to test JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without committing")
    parser.add_argument("--force", action="store_true", help="Force re-import even if records exist")
    args = parser.parse_args()

    print(f"Starting test data import from '{args.json}' (dry_run={args.dry_run}, force={args.force})...")
    res = run_test_import(json_path=args.json, dry_run=args.dry_run, force=args.force)
    print(json.dumps(res, indent=2, default=str))
